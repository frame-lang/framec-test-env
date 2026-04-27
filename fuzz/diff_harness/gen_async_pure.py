#!/usr/bin/env python3
"""
Pure-Frame async fuzzer — Phase 6 of FUZZ_PLAN.md.

Generates Frame systems with `async` interface methods that await a
mock async helper, exercising the per-backend async lowering. The
helper is injected by the per-language renderer so the @@system
block stays language-neutral; the Python oracle is the canonical
trace and every other backend (TS, JS, Rust, C++, C#, Java, Kotlin,
Swift, Dart, GDScript) must produce byte-identical output.

Async is an 11-backend feature. C, Go, PHP, Ruby, Lua, Erlang lack
native async semantics and are skipped per matrix footnote (see
`runtime-capability-matrix.md`).

Axes (kept tight for Phase 6's first cut):

    pattern         single_await       — fetch(key): str { result = await op(key); @@:(result) }
                    two_awaits         — same but two sequential awaits, concatenated
                    await_then_trans   — fetch transitions after the await result

    state_count     [2, 3]             — flat machines for the first cut
    hsm_depth       [0, 1]             — flat or single-parent HSM

Product: 3 × 2 × 2 = 12 cases. Small enough to land Phase 6 with a
working differential against Python without exploding the case
matrix. Future expansion (two-phase init, await-then-mutate-domain)
follows the same shape; add an axis here and a renderer arm in
langs.py.

Usage:
    python3 gen_async_pure.py --max 12 --out ../cases/async
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path

PATTERNS = ["single_await", "two_awaits", "await_then_trans"]
STATE_COUNTS = [2, 3]
HSM_DEPTHS = [0, 1]


def state_name(i: int) -> str:
    return f"$S{i}"


def gen_handler_body(pattern: str, n: int) -> list[str]:
    """Emit the `fetch(key: str): str` handler body in Python-canonical
    syntax. Renderers for non-Python backends rewrite the embedded
    native code (e.g. `result = await op(key)`) per their async
    primitives — Python `await op(key)` becomes JS `await op(key)`,
    Rust `op(key).await`, Java `op(key).get()`, etc.

    `op` is a placeholder name; the renderer prepends its definition
    in the case's prolog so framec sees a real symbol pass through."""
    out = []
    if pattern == "single_await":
        out.append('                result = await op(key)')
        out.append('                @@:(result)')
    elif pattern == "two_awaits":
        out.append('                a = await op(key)')
        out.append('                b = await op(key)')
        out.append('                @@:(a + b)')
    elif pattern == "await_then_trans":
        # Transition after the await. Per Frame semantics the post-
        # transition `@@:(...)` still sets the return slot — the
        # interface caller awaits the wrapper which reads the slot
        # after the transition completes.
        next_state = state_name(1 % n)
        out.append('                result = await op(key)')
        out.append('                @@:(result)')
        out.append(f'                -> {next_state}')
    else:
        raise ValueError(f"unknown pattern {pattern}")
    return out


def gen_system(case_id: int, params: dict) -> tuple[str, str]:
    sys_name = f"Async{case_id:04d}"
    n = params["n_states"]
    depth = params["hsm_depth"]
    pattern = params["pattern"]

    lines = []
    lines.append("@@target python_3")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append("        async fetch(key: str): str")
    lines.append("        status(): str")
    lines.append("")
    lines.append("    machine:")
    for i in range(n):
        st = state_name(i)
        has_parent = depth > 0 and 0 < i <= depth
        lines.append(f"        {st}{' => $S0' if has_parent else ''} {{")
        if i == 0:
            lines.append("            fetch(key: str): str {")
            lines.extend(gen_handler_body(pattern, n))
            lines.append("            }")
            lines.append(f'            status(): str {{ @@:("s{i}") }}')
        else:
            # Non-start states: fetch/status return a fixed string so
            # the post-transition fetch in `await_then_trans` produces
            # a deterministic trace.
            lines.append("            fetch(key: str): str {")
            lines.append('                @@:("done")')
            lines.append("            }")
            lines.append(f'            status(): str {{ @@:("s{i}") }}')
        if has_parent:
            lines.append("            => $^")
        lines.append("        }")
    lines.append("}")
    return "\n".join(lines) + "\n", sys_name


def gen_meta(case_id: int, sys_name: str, params: dict) -> dict:
    """Per-case meta consumed by the per-backend renderer. The renderer
    builds: (1) a prolog defining the mock async `op` helper in the
    target language; (2) a driver that calls `fetch("k")` once and
    prints the trace.

    Expected trace (oracle, identical across all 11 async backends):

        TRACE: CALL fetch
        TRACE: RET <value>
        TRACE: status <s_after>

    where <value> is the renderer-defined `op` output for the pattern,
    and <s_after> is `s{1 % n}` for `await_then_trans` else `s0`."""
    n = params["n_states"]
    pattern = params["pattern"]
    if pattern == "single_await":
        expected_value = "value_for_k"
        expected_state = "s0"
    elif pattern == "two_awaits":
        expected_value = "value_for_kvalue_for_k"
        expected_state = "s0"
    elif pattern == "await_then_trans":
        expected_value = "value_for_k"
        expected_state = f"s{1 % n}"
    else:
        raise ValueError(f"unknown pattern {pattern}")

    return {
        "trace_fmt": "v1",
        "harness_kind": "async",
        "sys_name": sys_name,
        "axes": {
            "n_states": n,
            "hsm_depth": params["hsm_depth"],
            "pattern": pattern,
        },
        "expected": {
            "value": expected_value,
            "state": expected_state,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=12)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "cases" / "async",
    )
    args = p.parse_args()

    random.seed(args.seed)
    axes = list(itertools.product(PATTERNS, STATE_COUNTS, HSM_DEPTHS))
    random.shuffle(axes)
    axes = axes[: args.max]

    args.out.mkdir(parents=True, exist_ok=True)
    for f in args.out.glob("case_*.*"):
        f.unlink()

    for cid, (pattern, n, d) in enumerate(axes):
        params = dict(n_states=n, hsm_depth=d, pattern=pattern)
        src, sys_name = gen_system(cid, params)
        meta = gen_meta(cid, sys_name, params)
        (args.out / f"case_{cid:04d}.frame").write_text(src)
        (args.out / f"case_{cid:04d}.meta").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Generated {len(axes)} async cases in {args.out}")


if __name__ == "__main__":
    main()
