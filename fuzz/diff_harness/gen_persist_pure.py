#!/usr/bin/env python3
"""
Pure-Frame persist fuzzer — Phase 2 of FUZZ_PLAN.md.

Generates `@@persist` systems WITHOUT an inlined language-specific harness.
The epilog (instantiate / drive sequence / save / restore / inspect) is
generated per-backend at run time by `diff_harness/run_persist.py`, which
reads the companion `.meta` sidecar.

Each case is reduced to a pair of files:
    cases/persist/case_0042.frame    — the pure @@system block
    cases/persist/case_0042.meta     — axes + expected trace parameters

Axes (unchanged from the pre-harness fuzzer):
    STATE_COUNTS      [2, 3, 5]
    HSM_DEPTHS        [0, 1, 2]   # 0=flat, 1=one parent, 2=grandparent chain
    DOMAIN_SETS       ["int", "int_str", "int_str_bool"]
    TARGET_OFFSETS    [0, 1, 2]   # how many advance() calls before snapshot
    (STATE_VARS dropped for now — no existing fuzz code actually varies it)

5 × 3 × 3 × 3 = 135 cases (down from 162 because we dropped STATE_VARS).

Usage:
    python3 gen_persist_pure.py --max 162 --out ../cases/persist
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path

STATE_COUNTS = [2, 3, 5]
HSM_DEPTHS = [0, 1, 2]
DOMAIN_SETS = ["int", "int_str", "int_str_bool"]
TARGET_OFFSETS = [0, 1, 2]


def state_name(i: int) -> str:
    return f"$S{i}"


def gen_machine_block(n: int, depth: int, has_str: bool, has_bool: bool) -> str:
    """Emit the `interface:` + `machine:` sections for a case.

    Every case has the same core interface — `advance()`, `set_x(v: int)`,
    optional `set_s(v: str)` / `set_b(v: bool)`, plus `status(): str` and
    getters `get_x(): int` / `get_s(): str` / `get_b(): bool`. The getters
    let the harness read domain state back without poking at private
    fields, which vary per-backend."""
    lines = ["    interface:"]
    lines.append("        advance()")
    lines.append("        set_x(v: int)")
    if has_str:
        lines.append("        set_s(v: str)")
    if has_bool:
        lines.append("        set_b(v: bool)")
    lines.append("        status(): str")
    lines.append("        get_x(): int")
    if has_str:
        lines.append("        get_s(): str")
    if has_bool:
        lines.append("        get_b(): bool")
    lines.append("")
    lines.append("    machine:")
    for i in range(n):
        st = state_name(i)
        # HSM: states 1..depth chain back to S0 as parent. `depth=0` flat,
        # `depth=1` → S1 under S0, `depth=2` → S1 under S0, S2 under S0.
        has_parent = depth > 0 and 0 < i <= depth
        if has_parent:
            lines.append(f"        {st} => {state_name(0)} {{")
        else:
            lines.append(f"        {st} {{")
        nxt = state_name((i + 1) % n)
        lines.append(f"            advance() {{ -> {nxt} }}")
        # `;` after each native statement: required for Dart/JS/Java/
        # Kotlin/C#/C++/Swift/Go, harmless for Python/Ruby/Lua.
        lines.append("            set_x(v: int) { self.x = v; }")
        if has_str:
            lines.append("            set_s(v: str) { self.s = v; }")
        if has_bool:
            lines.append("            set_b(v: bool) { self.b = v; }")
        lines.append(f'            status(): str {{ @@:("s{i}") }}')
        lines.append("            get_x(): int { @@:(self.x) }")
        if has_str:
            lines.append("            get_s(): str { @@:(self.s) }")
        if has_bool:
            lines.append("            get_b(): bool { @@:(self.b) }")
        if has_parent:
            lines.append("            => $^")
        lines.append("        }")
    return "\n".join(lines)


def gen_domain_block(domain_set: str) -> str:
    lines = ["    domain:"]
    lines.append("        x: int = 0")
    if domain_set in ("int_str", "int_str_bool"):
        lines.append('        s: str = ""')
    if domain_set == "int_str_bool":
        # Canonical bool form is Python-style `False` (the oracle). Each
        # non-Python backend's rewrite_trace lowercases it at runtime via
        # a word-boundary substitution that avoids string literals.
        lines.append("        b: bool = False")
    return "\n".join(lines)


def gen_case_frame(case_id: int, params: dict) -> tuple[str, str]:
    """Return (frame_source, sys_name). The frame source targets python_3
    by default; run_persist.py rewrites @@target per-backend at runtime."""
    sys_name = f"Persist{case_id:04d}"
    has_str = params["domain_set"] in ("int_str", "int_str_bool")
    has_bool = params["domain_set"] == "int_str_bool"

    parts = []
    parts.append("@@target python_3")
    parts.append("")
    parts.append("@@persist")
    parts.append(f"@@system {sys_name} {{")
    parts.append(gen_machine_block(params["n_states"], params["hsm_depth"], has_str, has_bool))
    parts.append("")
    parts.append(gen_domain_block(params["domain_set"]))
    parts.append("}")
    return "\n".join(parts) + "\n", sys_name


def gen_meta(case_id: int, sys_name: str, params: dict) -> dict:
    """The meta sidecar captures everything run_persist.py needs to
    render the epilog — axes, expected status, domain values to set."""
    n = params["n_states"]
    target = params["target_offset"] % n
    seed = 1000 + case_id
    has_str = params["domain_set"] in ("int_str", "int_str_bool")
    has_bool = params["domain_set"] == "int_str_bool"
    return {
        "trace_fmt": "v1",
        "harness_kind": "persist",
        "sys_name": sys_name,
        "axes": {
            "n_states": n,
            "hsm_depth": params["hsm_depth"],
            "domain_set": params["domain_set"],
            "target_offset": target,
        },
        "sequence": {
            "advances_pre": target,
            "set_x": seed,
            "set_s": f"sval_{seed}" if has_str else None,
            "set_b": (seed % 2 == 0) if has_bool else None,
            "expected_status": f"s{target}",
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=162)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path,
                   default=Path(__file__).resolve().parents[1] / "cases" / "persist")
    args = p.parse_args()

    random.seed(args.seed)
    axes = list(itertools.product(
        STATE_COUNTS, HSM_DEPTHS, DOMAIN_SETS, TARGET_OFFSETS,
    ))
    random.shuffle(axes)
    axes = axes[:args.max]

    args.out.mkdir(parents=True, exist_ok=True)
    # Clean stale cases so a rerun with fewer --max doesn't leave leftovers.
    for f in args.out.glob("case_*.*"):
        f.unlink()

    for cid, (n, d, ds, t) in enumerate(axes):
        params = dict(n_states=n, hsm_depth=d, domain_set=ds, target_offset=t)
        src, sys_name = gen_case_frame(cid, params)
        meta = gen_meta(cid, sys_name, params)
        (args.out / f"case_{cid:04d}.frame").write_text(src)
        (args.out / f"case_{cid:04d}.meta").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Generated {len(axes)} persist cases in {args.out}")


if __name__ == "__main__":
    main()
