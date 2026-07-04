#!/usr/bin/env python3
"""
Phase 26 — async × persist cross-product.

Phase 6 (async) and Phase 2 (persist) are orthogonal at the codegen
level — async maps to the host-language coroutine primitive, persist
serializes domain + compartment chain. Their intersection is small but
real: a system can be both `@@[async]` (an interface method awaits) and
`@@[persist(...)]` (domain + machine state survive a save/restore).

The interesting seam is the async casing's transient gate (`busy` /
`in_flight`) plus the `_<Name>Machine` split: does the machine state
round-trip while the gate stays out of the snapshot, and does a fresh
restored casing start with a clear gate?

Coverage — all 11 async backends (Phase 6 breadth; C, Go, PHP, Ruby,
Lua, Erlang have no async semantics and are excluded), four patterns:

  P1 await_then_save   — drive one async op, save outside the handler,
                         restore, drive again (value survived).
  P2 save_between_awaits — save between two async ops on the live
                         instance; the snapshot captures the mid value.
  P3 restore_then_await — save a clean-slate instance, restore, and make
                         the FIRST op on the restored casing an await.
  P4 gate_clears       — drive a full gate cycle, save, restore, and
                         confirm subsequent awaits on the restored casing
                         succeed (gate isn't stuck busy / wasn't
                         serialized). Mirrors the hand-written matrix
                         fixture `async_persist_roundtrip_gate_clears`.

All four reuse one proven `@@[async] @@[persist] system Counter` whose
`async bump()` increments a persisted `value`; only the driver's
save-point and await ordering differ. Each backend's system block and
driver mirror the matrix's per-language async + persist idioms.

Usage:
  python3 gen_async_persist.py --max 3
  python3 gen_async_persist.py --max 3 --patterns p4_gate_clears
"""
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# --- the four driver scripts, as (save_after_n_pre_bumps, extra_pre_bumps,
#     post_restore_bumps). Expected values are computed from the op order:
#     each bump increments the current instance; save/restore carry `value`.
PATTERNS = {
    "p1_await_then_save":   dict(pre=1, save_at=1, post=1),   # s1->1, save(1), s2->2
    "p2_save_between_awaits": dict(pre=2, save_at=1, post=1), # s1->1, save(1), s1->2, s2->2
    "p3_restore_then_await": dict(pre=0, save_at=0, post=1),  # save(0), s2->1
    "p4_gate_clears":       dict(pre=1, save_at=1, post=2),   # s1->1, save(1), s2->2, s2->3
}


@dataclass
class LangSpec:
    target: str
    ext: str
    persist_t: str
    save: str            # save method name
    load: str            # load method name
    ret_int: str         # interface return type
    domain_t: str        # domain field type
    self_ref: str        # self. / this. / this->
    stmt_end: str        # ; or ''
    body_await: str      # await line inside handler body (no indent), or ''
    ret_suffix: str      # extra line after @@:() (rust: return;), or ''
    preamble: str        # text emitted before the @@system block
    indent: str          # driver body indent
    head: str            # driver opening
    tail: str            # driver closing
    ops: dict = field(default_factory=dict)  # op-name -> callable


def _sys_block(s: LangSpec) -> str:
    body = ""
    if s.body_await:
        body += f"                {s.body_await}\n"
    body += f"                {s.self_ref}value = {s.self_ref}value + 1{s.stmt_end}\n"
    body += f"                @@:({s.self_ref}value){s.ret_suffix}"
    return f'''@@[persist({s.persist_t})]
@@[save({s.save})]
@@[load({s.load})]
@@[async]
@@system Counter {{
    interface:
        async bump(): {s.ret_int}

    machine:
        $S {{
            bump(): {s.ret_int} {{
{body}
            }}
        }}

    domain:
        value: {s.domain_t} = 0
}}'''


def _driver(s: LangSpec, steps: list) -> str:
    lines = []
    for step in steps:
        rendered = s.ops[step[0]](*step[1:])
        for ln in rendered.split("\n"):
            lines.append(s.indent + ln if ln else ln)
    return s.head + "\n" + "\n".join(lines) + "\n" + s.tail


def _steps(pattern: str, tag: str) -> list:
    p = PATTERNS[pattern]
    steps = [("decl", "s1"), ("init", "s1")]
    val = 0
    n = 0
    saved = None
    # pre-save bumps
    for _ in range(p["save_at"]):
        val += 1
        n += 1
        steps.append(("bump", "s1", f"v{n}", val))
    steps.append(("save", "s1", "snap"))
    saved = val
    # any extra pre bumps on s1 after save
    for _ in range(p["pre"] - p["save_at"]):
        val += 1
        n += 1
        steps.append(("bump", "s1", f"v{n}", val))
    # restore into fresh s2, then post-restore bumps
    steps.append(("decl", "s2"))
    steps.append(("restore", "s2", "snap"))
    val = saved
    for _ in range(p["post"]):
        val += 1
        n += 1
        steps.append(("bump", "s2", f"v{n}", val))
    steps.append(("pass", tag))
    return steps


def _build_specs() -> dict:
    S = {}

    S["python_3"] = LangSpec(
        target="python_3", ext="fpy", persist_t="str", save="save_state",
        load="restore_state", ret_int="int", domain_t="int", self_ref="self.",
        stmt_end="", body_await="await asyncio.sleep(0)", ret_suffix="",
        preamble="import asyncio\n", indent="    ",
        head="async def main():",
        tail="\nif __name__ == '__main__':\n    asyncio.run(main())",
        ops={
            "decl": lambda v: f"{v} = @@Counter()",
            "init": lambda v: f"await {v}.init()",
            "bump": lambda v, r, e: f"{r} = await {v}.bump()\nassert {r} == {e}, f\"{v}.bump: {{{r}}}\"",
            "save": lambda v, sn: f"{sn} = {v}.save_state()",
            "restore": lambda v, sn: f"{v}.restore_state({sn})",
            "pass": lambda tag: f'print("PASS: {tag}")',
        })

    S["typescript"] = LangSpec(
        target="typescript", ext="fts", persist_t="string", save="save_state",
        load="restore_state", ret_int="number", domain_t="number", self_ref="this.",
        stmt_end=";", body_await="await Promise.resolve();", ret_suffix="",
        preamble="", indent="    ",
        head="async function main(): Promise<void> {", tail="}\nmain();",
        ops={
            "decl": lambda v: f"const {v} = @@Counter();",
            "init": lambda v: f"await {v}.init();",
            "bump": lambda v, r, e: f"const {r} = await {v}.bump();\nif ({r} !== {e}) throw new Error(`{v}.bump: ${{{r}}}`);",
            "save": lambda v, sn: f"const {sn} = {v}.save_state();",
            "restore": lambda v, sn: f"{v}.restore_state({sn});",
            "pass": lambda tag: f'console.log("PASS: {tag}");',
        })

    S["javascript"] = LangSpec(
        target="javascript", ext="fjs", persist_t="string", save="save_state",
        load="restore_state", ret_int="number", domain_t="number", self_ref="this.",
        stmt_end=";", body_await="await Promise.resolve();", ret_suffix="",
        preamble="", indent="    ",
        head="async function main() {", tail="}\nmain();",
        ops={
            "decl": lambda v: f"const {v} = @@Counter();",
            "init": lambda v: f"await {v}.init();",
            "bump": lambda v, r, e: f"const {r} = await {v}.bump();\nif ({r} !== {e}) throw new Error(`{v}.bump: ${{{r}}}`);",
            "save": lambda v, sn: f"const {sn} = {v}.save_state();",
            "restore": lambda v, sn: f"{v}.restore_state({sn});",
            "pass": lambda tag: f'console.log("PASS: {tag}");',
        })

    S["kotlin"] = LangSpec(
        target="kotlin", ext="fkt", persist_t="String", save="save_state",
        load="restore_state", ret_int="Int", domain_t="Int", self_ref="this.",
        stmt_end="", body_await="yield()", ret_suffix="",
        preamble="import kotlinx.coroutines.runBlocking\nimport kotlinx.coroutines.yield\n",
        indent="    ", head="fun main() = runBlocking {", tail="}",
        ops={
            "decl": lambda v: f"val {v} = @@Counter()",
            "init": lambda v: f"{v}.init()",
            "bump": lambda v, r, e: f"val {r} = {v}.bump()\ncheck({r} == {e}) {{ \"{v}: ${r}\" }}",
            "save": lambda v, sn: f"val {sn} = {v}.save_state()",
            "restore": lambda v, sn: f"{v}.restore_state({sn})",
            "pass": lambda tag: f'println("PASS: {tag}")',
        })

    S["csharp"] = LangSpec(
        target="csharp", ext="fcs", persist_t="string", save="save_state",
        load="restore_state", ret_int="int", domain_t="int", self_ref="this.",
        stmt_end=";", body_await="await Task.Yield();", ret_suffix="",
        preamble="using System;\nusing System.Threading.Tasks;\n", indent="        ",
        head="class Program {\n    public static async Task Main(string[] args) {",
        tail="    }\n}",
        ops={
            "decl": lambda v: f"var {v} = @@Counter();",
            "init": lambda v: f"await {v}.init();",
            "bump": lambda v, r, e: f"var {r} = await {v}.bump();\nif ({r} != {e}) throw new Exception($\"{v}: {{{r}}}\");",
            "save": lambda v, sn: f"var {sn} = {v}.save_state();",
            "restore": lambda v, sn: f"{v}.restore_state({sn});",
            "pass": lambda tag: f'Console.WriteLine("PASS: {tag}");',
        })

    S["java"] = LangSpec(
        target="java", ext="fjava", persist_t="String", save="save_state",
        load="restore_state", ret_int="Integer", domain_t="int", self_ref="this.",
        stmt_end=";", body_await="", ret_suffix="",
        preamble="", indent="        ",
        head="class Main {\n    public static void main(String[] args) throws Exception {",
        tail="    }\n}",
        ops={
            "decl": lambda v: f"Counter {v} = @@Counter();",
            "init": lambda v: f"{v}.init().get();",
            "bump": lambda v, r, e: f"Integer {r} = {v}.bump().get();\nif ({r} != {e}) throw new RuntimeException(\"{v}: \" + {r});",
            "save": lambda v, sn: f"String {sn} = {v}.save_state();",
            "restore": lambda v, sn: f"{v}.restore_state({sn});",
            "pass": lambda tag: f'System.out.println("PASS: {tag}");',
        })

    S["rust"] = LangSpec(
        target="rust", ext="frs", persist_t="String", save="save_state",
        load="restore_state", ret_int="i32", domain_t="i32", self_ref="self.",
        stmt_end=";", body_await="tokio::task::yield_now().await;",
        ret_suffix="\n                return;", preamble="", indent="    ",
        head="#[tokio::main]\nasync fn main() -> Result<(), Box<dyn std::error::Error>> {",
        tail="    Ok(())\n}",
        ops={
            "decl": lambda v: f"let mut {v} = @@Counter();",
            "init": lambda v: f"{v}.init().await;",
            "bump": lambda v, r, e: f"let {r} = {v}.bump().await?;\nassert_eq!({r}, {e}, \"{v}.bump\");",
            "save": lambda v, sn: f"let {sn}: String = {v}.save_state();",
            "restore": lambda v, sn: f"{v}.restore_state({sn});",
            "pass": lambda tag: f'println!("PASS: {tag}");',
        })

    S["swift"] = LangSpec(
        target="swift", ext="fswift", persist_t="String", save="saveState",
        load="restoreState", ret_int="Int", domain_t="Int", self_ref="self.",
        stmt_end="", body_await="", ret_suffix="",
        preamble="import Foundation\nsetvbuf(stdout, nil, _IOLBF, 0)\n", indent="        ",
        head="let __sem = DispatchSemaphore(value: 0)\nTask {\n    do {",
        tail="    } catch { fatalError(\"unexpected: \\(error)\") }\n    __sem.signal()\n}\n__sem.wait()",
        ops={
            "decl": lambda v: f"let {v} = @@Counter()",
            "init": lambda v: f"await {v}.initAsync()",
            "bump": lambda v, r, e: f"let {r} = try await {v}.bump()\nguard {r} == {e} else {{ fatalError(\"{v}: \\({r})\") }}",
            "save": lambda v, sn: f"let {sn} = {v}.saveState()",
            "restore": lambda v, sn: f"{v}.restoreState({sn})",
            "pass": lambda tag: f'print("PASS: {tag}")',
        })

    S["dart"] = LangSpec(
        target="dart", ext="fdart", persist_t="String", save="save_state",
        load="restore_state", ret_int="int", domain_t="int", self_ref="this.",
        stmt_end=";", body_await="await Future.delayed(Duration.zero);",
        ret_suffix="", preamble="import 'dart:convert';\n", indent="    ",
        head="Future<void> main() async {", tail="}",
        ops={
            "decl": lambda v: f"final {v} = @@Counter();",
            "init": lambda v: f"await {v}.init();",
            "bump": lambda v, r, e: f"final {r} = await {v}.bump();\nif ({r} != {e}) throw Exception(\"{v}: ${r}\");",
            "save": lambda v, sn: f"final {sn} = {v}.save_state();",
            "restore": lambda v, sn: f"{v}.restore_state({sn});",
            "pass": lambda tag: f'print("PASS: {tag}");',
        })

    S["cpp"] = LangSpec(
        target="cpp_23", ext="fcpp", persist_t="std::string", save="save_state",
        load="restore_state", ret_int="int", domain_t="int", self_ref="this->",
        stmt_end=";", body_await="", ret_suffix="",
        preamble="#include <nlohmann/json.hpp>\n#include <iostream>\n", indent="    ",
        head="int main() {", tail="    return 0;\n}",
        ops={
            "decl": lambda v: f"auto {v} = @@Counter();",
            "init": lambda v: f"{v}.init().get();",
            "bump": lambda v, r, e: f"int {r} = {v}.bump().get();\nif ({r} != {e}) {{ std::cout << \"FAIL {v}: \" << {r} << std::endl; return 1; }}",
            "save": lambda v, sn: f"auto {sn} = {v}.save_state();",
            "restore": lambda v, sn: f"{v}.restore_state({sn});",
            "pass": lambda tag: f'std::cout << "PASS: {tag}" << std::endl;',
        })

    S["gdscript"] = LangSpec(
        target="gdscript", ext="fgd", persist_t="String", save="save_state",
        load="restore_state", ret_int="int", domain_t="int", self_ref="self.",
        stmt_end="", body_await="", ret_suffix="",
        preamble="extends SceneTree\n", indent="    ",
        head="func _init():", tail="    quit()",
        ops={
            "decl": lambda v: f"var {v} = @@Counter()",
            "init": lambda v: f"await {v}.init()",
            "bump": lambda v, r, e: f"var {r} = await {v}.bump()\nassert({r} == {e}, \"{v}: \" + str({r}))",
            "save": lambda v, sn: f"var {sn} = {v}.save_state()",
            "restore": lambda v, sn: f"{v}.restore_state({sn})",
            "pass": lambda tag: f'print("PASS: {tag}")',
        })

    return S


SPECS = _build_specs()


def render_case(lang: str, pattern: str, case_id: str) -> str:
    s = SPECS[lang]
    tag = f"{pattern}_{case_id}"
    parts = [f'@@[target("{s.target}")]', ""]
    if s.preamble:
        parts.append(s.preamble.rstrip("\n"))
        parts.append("")
    parts.append(f"// async x persist -- {tag}" if s.ext not in ("fpy", "fgd")
                 else f"# async x persist -- {tag}")
    parts.append("")
    parts.append(_sys_block(s))
    parts.append("")
    parts.append(_driver(s, _steps(pattern, tag)))
    return "\n".join(parts) + "\n"


def write_cases(out_dir: Path, max_per_pattern: int, patterns, langs) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for lang in langs:
        s = SPECS[lang]
        for pattern in patterns:
            for i in range(max_per_pattern):
                case_id = f"{i:03d}"
                text = render_case(lang, pattern, case_id)
                out = out_dir / f"{s.target}_{pattern}_{case_id}.{s.ext}"
                out.write_text(text)
                written += 1
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max", type=int, default=3,
                    help="Cases per (pattern x backend) (default 3)")
    ap.add_argument("--out-dir", type=Path, default=Path("cases_async_persist"),
                    help="Output directory")
    ap.add_argument("--patterns", nargs="*", default=list(PATTERNS),
                    choices=list(PATTERNS), help="Patterns to emit")
    ap.add_argument("--langs", nargs="*", default=list(SPECS),
                    choices=list(SPECS), help="Backends to emit")
    args = ap.parse_args()

    n = write_cases(args.out_dir, args.max, args.patterns, args.langs)
    print(f"Wrote {n} cases to {args.out_dir}/ "
          f"({len(args.langs)} backends x {len(args.patterns)} patterns x {args.max})")


if __name__ == "__main__":
    main()
