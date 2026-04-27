#!/usr/bin/env python3
"""
Pure-Frame multi-system fuzzer — Phase 7 of FUZZ_PLAN.md.

Generates pairs of `@@system` blocks where one system holds an
instance of another in its `domain:` section and calls into it.
Tests cross-system instantiation and dispatch.

Erlang is excluded per matrix footnote — gen_statem processes
don't compose as in-process instances. Backend applicability is
**16** of the standard 17.

Axes (kept tight for Phase 7's first cut):

    pattern         simple_call        — outer.run() calls self.inner.bump()
                    multi_call         — outer fires inner.bump() three times
                    transition_call    — outer transitions, then calls inner

    state_count     [2, 3]             — flat machines for the first cut
    hsm_depth       [0]                — flat only (HSM × multi-system × per-
                                         backend types is too many axes)

Product: 3 × 2 × 1 = 6 cases. Same scoping discipline as
gen_async_pure.py first cut: prove the architecture across a
handful of backends, expand axes once stable.

Frame source structure:

    @@system Counter {
        interface:
            bump()
            get_n(): int

        machine:
            $Active {
                bump() { self.n = self.n + 1 }
                get_n(): int { @@:(self.n) }
            }

        domain:
            n: int = 0
    }

    @@system Driver {
        interface:
            run()
            get_total(): int

        machine:
            $Idle {
                run() {
                    self.inner.bump()
                    self.inner.bump()
                    -> $Done
                }
                get_total(): int { @@:(self.inner.get_n()) }
            }
            $Done {
                get_total(): int { @@:(self.inner.get_n()) }
            }

        domain:
            inner: Counter = @@Counter()
    }

The renderer's driver instantiates only the OUTER system; the inner
is constructed transitively by the outer's domain init. Trace
contract:

    TRACE: CALL run
    TRACE: CALL get_total
    TRACE: total <N>

Where <N> is `expected.total` — the bump count the Driver's run()
fires (typically 2 for simple_call, 3 for multi_call, etc).

Usage:
    python3 gen_multisys_pure.py --max 6 --out ../cases/multisys
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path

PATTERNS = ["simple_call", "multi_call", "transition_call"]
STATE_COUNTS = [2, 3]
HSM_DEPTHS = [0, 1]


def state_name(i: int) -> str:
    return f"$D{i}"


def gen_run_body(pattern: str, n: int) -> tuple[list[str], int]:
    """Emit the Driver's `run()` handler body. Returns (lines,
    expected_bump_count). `;` after each call so C-family targets
    (Dart, Java, C#, Rust, etc.) accept the statement; Python
    ignores the terminator."""
    out = []
    if pattern == "simple_call":
        out.append("                self.inner.bump();")
        out.append("                self.inner.bump();")
        return out, 2
    elif pattern == "multi_call":
        out.append("                self.inner.bump();")
        out.append("                self.inner.bump();")
        out.append("                self.inner.bump();")
        return out, 3
    elif pattern == "transition_call":
        # Transition before the cross-system call. Exercises the
        # post-transition return-slot path: the bump fires after
        # the state change.
        next_state = state_name(1 % n)
        out.append("                self.inner.bump();")
        out.append(f"                -> {next_state}")
        return out, 1
    else:
        raise ValueError(f"unknown pattern {pattern}")


def gen_inner_system() -> str:
    """Counter system — same shape across every fuzz case. The outer
    system's domain holds an instance of this."""
    return """\
@@system Counter {
    interface:
        bump()
        get_n(): int

    machine:
        $Active {
            bump() { self.n = self.n + 1; }
            get_n(): int { @@:(self.n) }
        }

    domain:
        n: int = 0
}"""


def gen_outer_system(case_id: int, params: dict) -> tuple[str, str, int]:
    sys_name = f"Driver{case_id:04d}"
    n = params["n_states"]
    pattern = params["pattern"]
    run_lines, bump_count = gen_run_body(pattern, n)

    lines = []
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append("        run()")
    lines.append("        get_total(): int")
    lines.append("")
    lines.append("    machine:")
    for i in range(n):
        st = state_name(i)
        lines.append(f"        {st} {{")
        if i == 0:
            lines.append("            run() {")
            lines.extend(run_lines)
            lines.append("            }")
            lines.append("            get_total(): int { @@:(self.inner.get_n()) }")
        else:
            # Other states: run is a no-op, get_total still works.
            lines.append("            run() { }")
            lines.append("            get_total(): int { @@:(self.inner.get_n()) }")
        lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append("        inner: Counter = @@Counter()")
    lines.append("}")
    return "\n".join(lines), sys_name, bump_count


def gen_case_frame(case_id: int, params: dict) -> tuple[str, str, int]:
    """Returns (frame_source, outer_sys_name, expected_bump_count)."""
    inner = gen_inner_system()
    outer, sys_name, bump_count = gen_outer_system(case_id, params)

    parts = []
    parts.append("@@target python_3")
    parts.append("")
    parts.append(inner)
    parts.append("")
    parts.append(outer)
    return "\n".join(parts) + "\n", sys_name, bump_count


def gen_meta(case_id: int, sys_name: str, params: dict, bump_count: int) -> dict:
    return {
        "trace_fmt": "v1",
        "harness_kind": "multisys",
        "sys_name": sys_name,
        "axes": {
            "n_states": params["n_states"],
            "hsm_depth": params["hsm_depth"],
            "pattern": params["pattern"],
        },
        "expected": {
            "total": bump_count,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=6)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "cases" / "multisys",
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
        src, sys_name, bump_count = gen_case_frame(cid, params)
        meta = gen_meta(cid, sys_name, params, bump_count)
        (args.out / f"case_{cid:04d}.frame").write_text(src)
        (args.out / f"case_{cid:04d}.meta").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Generated {len(axes)} multisys cases in {args.out}")


if __name__ == "__main__":
    main()
