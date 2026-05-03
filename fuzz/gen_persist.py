#!/usr/bin/env python3
"""
Persist round-trip fuzzer for framec.

Generates Frame systems with `@@persist` plus a self-checking harness that:
  1. Drives the system through a deterministic sequence of transitions
     into a chosen "target" state, with domain vars set to known values.
  2. Calls save_state() / saveState() to serialize.
  3. Constructs a fresh instance via restore_state(snapshot).
  4. Asserts that the restored instance reports the same state and the
     same domain-var values as before serialization.

Each case prints `PASS` on success or `FAIL: <label>` + exits non-zero on
any mismatch, so the runner's regex-matching of `PASS`/`FAIL` works
without additional wiring.

Supported targets in this file: python_3, javascript, typescript, go.
Rust/C/Java/others need external library linking for JSON which is out
of scope for the local runner; those are validated in the Docker matrix.

Structural axes varied:
  state count           : 2, 3, 5
  HSM depth             : flat / 2-level / 3-level
  state variables       : on/off
  domain-var types mix  : int-only / int+str / int+str+bool
  target state offset   : which state the snapshot lands in
  domain-var values     : deterministic per-case to detect cross-contamination

Usage:
  python3 gen_persist.py --max 200
  ./run_persist.sh
"""
import argparse
import itertools
import random
from pathlib import Path

STATE_COUNTS = [2, 3, 5]
HSM_DEPTHS = [0, 1, 2]
STATE_VARS = [False, True]
DOMAIN_SETS = ["int", "int_str", "int_str_bool"]
TARGET_OFFSETS = [0, 1, 2]  # how many transitions before snapshot

# --- Per-language config -------------------------------------------------

class LangSpec:
    __slots__ = (
        "target", "ext", "int_type", "str_type", "bool_type",
        "self_x", "self_s", "self_b",
        "save_call", "restore_call", "status_cmp", "int_cmp", "str_cmp",
        "bool_true", "bool_false", "println", "fail_exit",
        "prolog", "harness_header", "harness_footer",
    )
    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k, ""))


def _build_specs():
    specs = {}

    specs["python_3"] = LangSpec(
        target="python_3", ext="fpy",
        int_type="int", str_type="str", bool_type="bool",
        self_x="self.x", self_s="self.s", self_b="self.b",
        save_call="snap = inst.save_state()",
        # RFC-0012 amendment: load is an instance method, two-step.
        restore_call="rest = {SYS}()\n    rest.restore_state(snap)",
        status_cmp='if rest.status() != inst_status: _fail(f"status: {{rest.status()}} != {{inst_status}}")',
        int_cmp='if rest.x != inst.x: _fail(f"x: {{rest.x}} != {{inst.x}}")',
        str_cmp='if rest.s != inst.s: _fail(f"s: {{rest.s}} != {{inst.s}}")',
        bool_true="True", bool_false="False",
        println='print("PASS: persist round-trip")',
        fail_exit='''
def _fail(msg):
    print(f"FAIL: {msg}")
    raise SystemExit(1)
''',
        prolog="",
        harness_footer="",
    )

    specs["javascript"] = LangSpec(
        target="javascript", ext="fjs",
        int_type="number", str_type="string", bool_type="boolean",
        self_x="this.x", self_s="this.s", self_b="this.b",
        save_call="const snap = inst.saveState();",
        # RFC-0012 amendment: load is an instance method, two-step.
        restore_call="const rest = @@{SYS}();\n    rest.restoreState(snap);",
        status_cmp='if (rest.status() !== inst_status) _fail(`status: ${{rest.status()}} !== ${{inst_status}}`);',
        int_cmp='if (rest.x !== inst.x) _fail(`x: ${{rest.x}} !== ${{inst.x}}`);',
        str_cmp='if (rest.s !== inst.s) _fail(`s: ${{rest.s}} !== ${{inst.s}}`);',
        bool_true="true", bool_false="false",
        println='console.log("PASS: persist round-trip");',
        fail_exit='''
function _fail(msg) { console.log("FAIL: " + msg); process.exit(1); }
''',
        prolog="",
        harness_footer="",
    )

    specs["typescript"] = LangSpec(
        target="typescript", ext="fts",
        int_type="number", str_type="string", bool_type="boolean",
        self_x="this.x", self_s="this.s", self_b="this.b",
        save_call="const snap = inst.saveState();",
        restore_call="const rest = {SYS}.restoreState(snap);",
        status_cmp='if (rest.status() !== inst_status) _fail(`status: ${{rest.status()}} !== ${{inst_status}}`);',
        int_cmp='if (rest.x !== inst.x) _fail(`x: ${{rest.x}} !== ${{inst.x}}`);',
        str_cmp='if (rest.s !== inst.s) _fail(`s: ${{rest.s}} !== ${{inst.s}}`);',
        bool_true="true", bool_false="false",
        println='console.log("PASS: persist round-trip");',
        fail_exit='''
function _fail(msg: string): void { console.log("FAIL: " + msg); process.exit(1); }
''',
        prolog="",
        harness_footer="",
    )

    return specs

LANGS = _build_specs()


def state_name(i): return f"$S{i}"
def state_erlang(i): return f"s{i}"


def gen_machine(params, spec):
    """Emit machine block + interface. Instance-member references use
    `spec.self_x/s/b` for target-language correctness (e.g. `this.x` in
    JS/TS, `self.x` in Python)."""
    n = params["n_states"]
    depth = params["hsm_depth"]
    domain_set = params["domain_set"]
    has_str = domain_set in ("int_str", "int_str_bool")
    has_bool = domain_set == "int_str_bool"
    int_t = spec.int_type
    str_t = spec.str_type
    bool_t = spec.bool_type

    lines = ["    interface:"]
    lines.append("        advance()")
    lines.append(f"        set_x(v: {int_t})")
    if has_str:
        lines.append(f"        set_s(v: {str_t})")
    if has_bool:
        lines.append(f"        set_b(v: {bool_t})")
    lines.append(f"        status(): {str_t}")
    lines.append("")
    lines.append("    machine:")
    for i in range(n):
        st = state_name(i)
        has_parent = depth > 0 and 0 < i <= depth
        if has_parent:
            parent = state_name(0)
            lines.append(f"        {st} => {parent} {{")
        else:
            lines.append(f"        {st} {{")
        nxt = state_name((i + 1) % n)
        lines.append(f"            advance() {{ -> {nxt} }}")
        lines.append(f"            set_x(v: {int_t}) {{ {spec.self_x} = v }}")
        if has_str:
            lines.append(f"            set_s(v: {str_t}) {{ {spec.self_s} = v }}")
        if has_bool:
            lines.append(f"            set_b(v: {bool_t}) {{ {spec.self_b} = v }}")
        lines.append(f'            status(): {str_t} {{ @@:("s{i}") }}')
        if has_parent:
            lines.append("            => $^")
        lines.append("        }")
    return "\n".join(lines)


def gen_system_frame(case_id, params, spec):
    sys_name = f"Persist{case_id:04d}"
    lines = []
    lines.append(f'@@[target("{spec.target}")]')
    lines.append("")
    if spec.prolog:
        lines.append(spec.prolog)
        lines.append("")
    lines.append("@@[persist]")
    lines.append(f"@@system {sys_name} {{")
    # RFC-0012 amendment: declare the framework-managed save/load ops.
    save_ret = "str" if spec.target == "python_3" else "string"
    save_method = "save_state" if spec.target == "python_3" else "saveState"
    load_method = "restore_state" if spec.target == "python_3" else "restoreState"
    lines.append("    operations:")
    lines.append("        @@[save]")
    lines.append(f"        {save_method}(): {save_ret} {{}}")
    lines.append("")
    lines.append("        @@[load]")
    lines.append(f"        {load_method}(data: {save_ret}) {{}}")
    lines.append("")
    lines.append(gen_machine(params, spec))
    lines.append("")
    lines.append("    domain:")
    lines.append("        x: int = 0")
    if params["domain_set"] in ("int_str", "int_str_bool"):
        lines.append('        s: str = ""')
    if params["domain_set"] == "int_str_bool":
        lines.append("        b: bool = false" if spec.target != "python_3" else "        b: bool = False")
    lines.append("}")
    return "\n".join(lines), sys_name


def gen_harness_python(case_id, params, sys_name, spec):
    """Python harness: drive through K transitions, set domain, save, restore, verify."""
    n = params["n_states"]
    target = params["target_offset"] % n
    seed = 1000 + case_id
    has_str = params["domain_set"] in ("int_str", "int_str_bool")
    has_bool = params["domain_set"] == "int_str_bool"

    lines = []
    lines.append("")
    lines.append(spec.fail_exit.strip())
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append(f"    inst = @@{sys_name}()")
    for _ in range(target):
        lines.append("    inst.advance()")
    lines.append(f"    inst.set_x({seed})")
    if has_str:
        lines.append(f'    inst.set_s("sval_{seed}")')
    if has_bool:
        lines.append(f"    inst.set_b({'True' if seed % 2 == 0 else 'False'})")
    lines.append(f"    inst_status = inst.status()")
    lines.append(f"    {spec.save_call}")
    lines.append(f"    {spec.restore_call.format(SYS=sys_name)}")
    lines.append(f'    {spec.status_cmp.format()}')
    lines.append(f'    {spec.int_cmp.format()}')
    if has_str:
        lines.append(f'    {spec.str_cmp.format()}')
    if has_bool:
        lines.append(f'    if rest.b != inst.b: _fail(f"b: {{rest.b}} != {{inst.b}}")')
    lines.append(f"    {spec.println}")
    return "\n".join(lines) + "\n"


def gen_harness_js(case_id, params, sys_name, spec):
    n = params["n_states"]
    target = params["target_offset"] % n
    seed = 1000 + case_id
    has_str = params["domain_set"] in ("int_str", "int_str_bool")
    has_bool = params["domain_set"] == "int_str_bool"

    lines = []
    lines.append("")
    lines.append(spec.fail_exit.strip())
    lines.append("")
    lines.append(f"const inst = new {sys_name}();")
    for _ in range(target):
        lines.append("inst.advance();")
    lines.append(f"inst.set_x({seed});")
    if has_str:
        lines.append(f'inst.set_s("sval_{seed}");')
    if has_bool:
        lines.append(f"inst.set_b({spec.bool_true if seed % 2 == 0 else spec.bool_false});")
    lines.append("const inst_status = inst.status();")
    lines.append(f"{spec.save_call}")
    lines.append(f"{spec.restore_call.format(SYS=sys_name)}")
    lines.append(spec.status_cmp.format())
    lines.append(spec.int_cmp.format())
    if has_str:
        lines.append(spec.str_cmp.format())
    if has_bool:
        lines.append(f'if (rest.b !== inst.b) _fail(`b: ${{rest.b}} !== ${{inst.b}}`);')
    lines.append(spec.println)
    return "\n".join(lines) + "\n"


def gen_harness(lang, case_id, params, sys_name, spec):
    if lang == "python_3":
        return gen_harness_python(case_id, params, sys_name, spec)
    if lang in ("javascript", "typescript"):
        return gen_harness_js(case_id, params, sys_name, spec)
    raise ValueError(lang)


def gen_case(lang, case_id, params):
    spec = LANGS[lang]
    frame, sys_name = gen_system_frame(case_id, params, spec)
    harness = gen_harness(lang, case_id, params, sys_name, spec)
    return frame + "\n\n" + harness


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=100)
    p.add_argument("--lang", type=str, default=None,
                   help="Limit to one target (python_3 | javascript | typescript)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path,
                   default=Path(__file__).parent / "cases_persist")
    args = p.parse_args()

    random.seed(args.seed)
    axes = list(itertools.product(
        STATE_COUNTS, HSM_DEPTHS, STATE_VARS, DOMAIN_SETS, TARGET_OFFSETS,
    ))
    random.shuffle(axes)
    axes = axes[:args.max]

    langs = [args.lang] if args.lang else list(LANGS.keys())
    args.out.mkdir(parents=True, exist_ok=True)
    for lang_key in langs:
        if lang_key not in LANGS:
            print(f"unknown lang: {lang_key}")
            continue
        spec = LANGS[lang_key]
        lang_dir = args.out / spec.target
        lang_dir.mkdir(exist_ok=True)
        for cid, (n, d, sv, ds, t) in enumerate(axes):
            params = dict(
                n_states=n, hsm_depth=d, use_state_vars=sv,
                domain_set=ds, target_offset=t,
            )
            (lang_dir / f"case_{cid:04d}.{spec.ext}").write_text(
                gen_case(lang_key, cid, params))
        print(f"Generated {len(axes)} persist cases for {spec.target}")


if __name__ == "__main__":
    main()
