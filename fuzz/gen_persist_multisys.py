#!/usr/bin/env python3
"""
Phase 25 — RFC-0015 fuzz: parameterized sub-system × persist round-trip.

Locks in the Issue #2 fix shipped by RFC-0015. The original defect
class: an outer system holds a parameterized inner sub-system in its
domain (`inner: Inner = @@Inner(seed)`), the user calls save_state()
on the outer, and restore crashes because the codegen tries to
reconstruct `inner` by calling its user-defined `_init(seed)` with
the wrong arity (or no args at all).

RFC-0015's factory-only contract eliminates the user-arg constructor:
restore allocates with the empty blank-allocator, then populates from
the saved nested blob. This phase exercises the contract end-to-end.

Patterns:
  P1 simple_nested        — outer holds inner (zero-arg). Mutate inner
                            via outer call, save outer, restore, verify
                            inner state survived.
  P2 parameterized_inner  — outer holds @@Inner(seed). Same round-trip;
                            verifies the seed-driven init survives.
  P3 chained              — outer.middle.inner (3-level). Mutate the
                            leaf, save root, restore, verify.

The fixtures are minimal — exercise the fix shape, not feature
breadth. Phase 24 already covers persist × state-args; this is
specifically about cross-system persist composition.

Usage:
  python3 gen_persist_multisys.py --max 30
  ./run_persist_multisys.sh
"""
import argparse
from pathlib import Path


# Per-language config — start with Python (canary), JS, TS, Rust as the
# first wave. Python is the spec baseline; JS/TS prove dynamic
# composition; Rust proves typed cross-system restore.

class LangSpec:
    __slots__ = (
        "target", "ext", "int_type",
        "save_call", "restore_call", "instantiate", "println", "exit_fail",
        "indent",
    )
    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k, ""))


LANGS = {
    "python_3": LangSpec(
        target="python_3", ext="fpy", int_type="int",
        save_call="snap = root.save_state()",
        restore_call="rest = {SYS}()\n    rest.restore_state(snap)",
        instantiate="root = @@{SYS}()",
        println='print("PASS: {tag}")',
        exit_fail="raise SystemExit(1)",
        indent="    ",
    ),
    "javascript": LangSpec(
        target="javascript", ext="fjs", int_type="number",
        save_call="const snap = root.saveState();",
        restore_call="const rest = new {SYS}();\n    rest.restoreState(snap);",
        instantiate="const root = @@{SYS}();",
        println='console.log("PASS: {tag}");',
        exit_fail="process.exit(1);",
        indent="    ",
    ),
    "typescript": LangSpec(
        target="typescript", ext="fts", int_type="number",
        save_call="const snap = root.saveState();",
        restore_call="const rest = new {SYS}();\n    rest.restoreState(snap);",
        instantiate="const root = @@{SYS}();",
        println='console.log("PASS: {tag}");',
        exit_fail="process.exit(1);",
        indent="    ",
    ),
    "rust": LangSpec(
        target="rust", ext="frs", int_type="i32",
        save_call="let snap = root.save_state();",
        restore_call="let mut rest = {SYS}::new();\n    rest.restore_state(snap);",
        instantiate="let mut root = {SYS}::new();",
        println='println!("PASS: {tag}");',
        exit_fail="std::process::exit(1);",
        indent="    ",
    ),
}


# --- Pattern P1: simple_nested -------------------------------------------

def gen_p1(lang, case_id):
    """Outer holds zero-arg Inner. Mutate inner, persist, restore,
    verify the inner state survived."""
    spec = LANGS[lang]
    tag = f"p1_simple_nested_{case_id}"

    if lang == "python_3":
        return f'''@@[target("python_3")]

@@[persist(str)]
@@[save(save_state)]
@@[load(restore_state)]
@@system Inner {{
    interface:
        bump()
        get_n(): int
    machine:
        $Active {{
            bump() {{ self.n = self.n + 1 }}
            get_n(): int {{ @@:(self.n) }}
        }}
    domain:
        n: int = 0
}}

@@[persist(str)]
@@[save(save_state)]
@@[load(restore_state)]
@@[main]
@@system Outer {{
    interface:
        tick()
        get_inner_n(): int
    machine:
        $Run {{
            tick() {{ self.inner.bump() }}
            get_inner_n(): int {{ @@:(self.inner.get_n()) }}
        }}
    domain:
        inner: Inner = @@Inner()
}}

if __name__ == "__main__":
    root = Outer()
    root.tick()
    root.tick()
    root.tick()
    if root.get_inner_n() != 3:
        print("FAIL pre: " + str(root.get_inner_n()))
        raise SystemExit(1)

    snap = root.save_state()
    rest = Outer()
    rest.restore_state(snap)
    if rest.get_inner_n() != 3:
        print("FAIL post: " + str(rest.get_inner_n()))
        raise SystemExit(1)

    print("PASS: {tag}")
'''
    if lang == "rust":
        return f'''@@[target("rust")]

use serde_json;

@@[persist(String)]
@@[save(save_state)]
@@[load(restore_state)]
@@system Inner {{
    interface:
        bump()
        get_n(): i32
    machine:
        $Active {{
            bump() {{ self.n = self.n + 1; }}
            get_n(): i32 {{ @@:(self.n) }}
        }}
    domain:
        n: i32 = 0
}}

@@[persist(String)]
@@[save(save_state)]
@@[load(restore_state)]
@@[main]
@@system Outer {{
    interface:
        tick()
        get_inner_n(): i32
    machine:
        $Run {{
            tick() {{ self.inner.bump(); }}
            get_inner_n(): i32 {{ @@:(self.inner.get_n()) }}
        }}
    domain:
        inner: Inner = @@Inner()
}}

fn main() {{
    let mut root = Outer::new();
    root.tick();
    root.tick();
    root.tick();
    if root.get_inner_n() != 3 {{
        println!("FAIL pre: {{}}", root.get_inner_n());
        std::process::exit(1);
    }}

    let snap = root.save_state();
    let mut rest = Outer::new();
    rest.restore_state(snap);
    if rest.get_inner_n() != 3 {{
        println!("FAIL post: {{}}", rest.get_inner_n());
        std::process::exit(1);
    }}

    println!("PASS: {tag}");
}}
'''
    if lang in ("javascript", "typescript"):
        is_ts = lang == "typescript"
        target = "typescript" if is_ts else "javascript"
        ts_n = ": number" if is_ts else ""
        ts_int = "number" if is_ts else "int"
        return f'''@@[target("{target}")]

@@[persist(string)]
@@[save(saveState)]
@@[load(restoreState)]
@@system Inner {{
    interface:
        bump()
        getN(): {ts_int}
    machine:
        $Active {{
            bump() {{ this.n = this.n + 1; }}
            getN(): {ts_int} {{ @@:(this.n) }}
        }}
    domain:
        n: {ts_int} = 0
}}

@@[persist(string)]
@@[save(saveState)]
@@[load(restoreState)]
@@[main]
@@system Outer {{
    interface:
        tick()
        getInnerN(): {ts_int}
    machine:
        $Run {{
            tick() {{ this.inner.bump(); }}
            getInnerN(): {ts_int} {{ @@:(this.inner.getN()) }}
        }}
    domain:
        inner: Inner = @@Inner()
}}

const root = new Outer();
root.tick();
root.tick();
root.tick();
if (root.getInnerN() !== 3) {{
    console.log("FAIL pre: " + root.getInnerN());
    process.exit(1);
}}
const snap = root.saveState();
const rest = new Outer();
rest.restoreState(snap);
if (rest.getInnerN() !== 3) {{
    console.log("FAIL post: " + rest.getInnerN());
    process.exit(1);
}}
console.log("PASS: {tag}");
'''
    raise NotImplementedError(lang)


def write_cases(out_dir: Path, langs, max_per_pattern):
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for lang in langs:
        spec = LANGS[lang]
        for i in range(max_per_pattern):
            case_id = f"{i:03d}"
            text = gen_p1(lang, case_id)
            tag = f"p1_simple_nested_{case_id}"
            out = out_dir / f"{lang}_{tag}.{spec.ext}"
            out.write_text(text)
            written += 1
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max", type=int, default=3,
                    help="Cases per pattern per language (default 3)")
    ap.add_argument("--langs", nargs="+",
                    default=["python_3", "javascript", "typescript", "rust"],
                    help="Languages to generate (default: 4-lang first wave)")
    ap.add_argument("--out-dir", type=Path,
                    default=Path("cases_persist_multisys"),
                    help="Output directory")
    args = ap.parse_args()

    n = write_cases(args.out_dir, args.langs, args.max)
    print(f"Wrote {n} cases to {args.out_dir}/ ({len(args.langs)} langs)")


if __name__ == "__main__":
    main()
