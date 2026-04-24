#!/usr/bin/env python3
"""
Pure-Frame nested-expression fuzzer — Phase 9 of FUZZ_PLAN.md.

Permutes Frame constructs in expression position inside OTHER Frame
constructs. Defect #10 (2026-04-24) surfaced that nested Frame
segments in `@@:self.method(args)` leaked the inner verbatim. Phase
9 locks that in — and checks every (outer, inner) pair for the same
contract: any Frame expression can appear wherever ANY other Frame
construct expects an expression.

**Expression-position outer slots:**

| tag       | form                        |
|-----------|-----------------------------|
| selfcall  | `@@:self.echo(<E>)`         |
| ret_sugar | `@@:(<E>)`                  |
| ret_set   | `@@:return = <E>`           |
| svar_set  | `$.val = <E>`               |
| dbl_call  | `@@:self.dbl(<E>)` (returns 2×E) |

**Inner expressions (each evaluates to a value):**

| tag     | form                              | yields |
|---------|-----------------------------------|--------|
| lit     | `42`                              | 42     |
| param   | `@@:params.x`  (requires `x`)     | x      |
| ret     | `@@:return`   (after `@@:return=N`) | N    |
| sv      | `$.val`       (after `$.val = N`) | N      |
| self_dbl | `@@:self.dbl(@@:params.x)`       | 2x     |
| nest_sc | `@@:self.echo(@@:params.x)`       | x      |

Note: every construct we use is framec-translated syntax. We
deliberately avoid native-only constructs like `self.<op>(...)`
because operation calls are NATIVE code (authors write target-
specific call syntax — `SysName_op(self, ...)` for C, `op(Data, ...)`
for Erlang, etc.). A portable cross-target fuzz source must stick
to Frame syntax for every position.

Not every (outer, inner) is meaningful (e.g., `@@:return = @@:return`
is a no-op), and some combinations are degenerate. We generate the
full cross-product and let the oracle define expected output.

Product: 5 × 6 = 30 cases (MVP; expand with more outers / deeper
nesting in follow-ons).

Usage:
    python3 gen_nested_pure.py --max 30 --out ../cases/nested
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path

OUTERS = ["selfcall", "ret_sugar", "ret_set", "svar_set", "dbl_call"]
INNERS = [
    "lit",
    "param",
    "ret",
    "sv",
    "self_dbl",
    "nest_sc",
    "deep_nest",    # 3-level nested @@:self.echo(@@:self.echo(@@:self.echo(x)))
    "arith_mixed",  # @@:params.x + @@:params.x — typed-local arithmetic
]

# Integer probe values — pick distinct so the expected computation
# can be unambiguously checked against the oracle.
PROBE_X = 7


def inner_expr_and_value(inner: str) -> tuple[str, int]:
    """Return (Frame source of inner expression, integer value it
    evaluates to for x == PROBE_X).

    For inners that need prior state (`@@:return`, `$.val`), the
    handler body emits a setup line before the outer construct."""
    return {
        "lit":         ("42",                                       42),
        "param":       ("@@:params.x",                              PROBE_X),
        "ret":         ("@@:return",                                PROBE_X),
        "sv":          ("$.val",                                    PROBE_X),
        "self_dbl":    ("@@:self.dbl(@@:params.x)",                 2 * PROBE_X),
        "nest_sc":     ("@@:self.echo(@@:params.x)",                PROBE_X),
        "deep_nest":   ("@@:self.echo(@@:self.echo(@@:self.echo(@@:params.x)))", PROBE_X),
        "arith_mixed": ("@@:params.x + @@:params.x",                2 * PROBE_X),
    }[inner]


def inner_setup(inner: str) -> list[str]:
    """Frame statements that MUST run before the outer construct so
    the inner expression yields the value the oracle expects."""
    return {
        "lit":         [],
        "param":       [],
        "ret":         ["                @@:return = @@:params.x"],
        "sv":          ["                $.val = @@:params.x"],
        "self_dbl":    [],
        "deep_nest":   [],
        "arith_mixed": [],
        "nest_sc":  [],
    }[inner]


def outer_body(outer: str, inner_src: str) -> list[str]:
    """Emit the outer construct wrapping the inner. After this body
    runs, the probe's return value should equal the inner's integer
    value (per the oracle)."""
    return {
        # @@:return = @@:self.echo(<inner>) — capture the self-call's
        # returned value in probe's @@:return slot, then propagate.
        # Without capture, the caller's @@:return is never set by the
        # nested call (`@@:(n)` inside echo writes echo's own context,
        # which pops after return). Capture makes the probe's return
        # value deterministic across all 17 targets.
        "selfcall":  [
            f"                @@:return = @@:self.echo({inner_src})",
            "                @@:(@@:return)",
        ],
        "ret_sugar": [f"                @@:({inner_src})"],
        "ret_set":   [
            f"                @@:return = {inner_src}",
            "                @@:(@@:return)",
        ],
        # $.val = <inner>; then emit $.val as the return value.
        "svar_set":  [
            f"                $.val = {inner_src}",
            "                @@:($.val)",
        ],
        # @@:self.dbl(<inner>) — dbl returns 2×arg. Captured into
        # probe's @@:return so the final value is deterministic.
        "dbl_call":  [
            f"                @@:return = @@:self.dbl({inner_src})",
            "                @@:(@@:return)",
        ],
    }[outer]


def expected_value(outer: str, inner_value: int) -> int:
    if outer == "dbl_call":
        return inner_value * 2
    return inner_value


def case_supported(outer: str, inner: str) -> bool:
    """Prune degenerate cases."""
    # `$.val = $.val` — legal but a no-op; keep.
    # `@@:return = @@:return` — ditto; keep.
    # `self.Doubler(nest_sc)` where nest_sc uses @@:self.echo —
    # syntactically fine.
    _ = outer, inner
    return True


def gen_system(case_id: int, outer: str, inner: str) -> tuple[str, str, int]:
    sys_name = f"Nested{case_id:04d}"
    inner_src, inner_value = inner_expr_and_value(inner)
    expect = expected_value(outer, inner_value)

    lines = []
    lines.append("@@target python_3")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append("        probe(x: int): int")
    lines.append("        echo(n: int): int")
    lines.append("        dbl(n: int): int")
    lines.append("        get_sv(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $A {")
    lines.append("            probe(x: int): int {")
    lines.extend(inner_setup(inner))
    lines.extend(outer_body(outer, inner_src))
    lines.append("            }")
    # `@@:params.n` (not bare `n`) to keep the body portable — PHP
    # writes `$n`, Erlang writes `N`. Framec translates @@:params per-
    # target; a bare identifier here would fail in PHP (undefined
    # constant `n`) and Erlang (unbound variable).
    lines.append("            echo(n: int): int { @@:(@@:params.n) }")
    # `@@:params.n` is now framec-translated per target: it emits
    # the declared typed local `n` (or `$n` for PHP, `N` for Erlang).
    # Using the Frame construct keeps the single source portable —
    # native `n` would break PHP (undefined constant `n` — needs `$n`)
    # and potentially other targets where the bare name isn't in
    # scope as written.
    lines.append("            dbl(n: int): int { @@:(@@:params.n + @@:params.n) }")
    lines.append("            get_sv(): int { @@:($.val) }")
    lines.append("")
    lines.append("            $.val: int = 0")
    lines.append("        }")
    lines.append("}")
    return "\n".join(lines) + "\n", sys_name, expect


def gen_meta(case_id: int, sys_name: str, outer: str, inner: str, expect: int) -> dict:
    return {
        "trace_fmt": "v1",
        "harness_kind": "nested",
        "sys_name": sys_name,
        "axes": {"outer": outer, "inner": inner},
        "probe_x": PROBE_X,
        "expected_value": expect,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=len(OUTERS) * len(INNERS))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "cases" / "nested",
    )
    args = p.parse_args()

    random.seed(args.seed)
    pairs = [(o, i) for o, i in itertools.product(OUTERS, INNERS)
             if case_supported(o, i)]
    random.shuffle(pairs)
    pairs = pairs[: args.max]

    args.out.mkdir(parents=True, exist_ok=True)
    for f in args.out.glob("case_*.*"):
        f.unlink()

    for cid, (outer, inner) in enumerate(pairs):
        src, sys_name, expect = gen_system(cid, outer, inner)
        meta = gen_meta(cid, sys_name, outer, inner, expect)
        (args.out / f"case_{cid:04d}.frame").write_text(src)
        (args.out / f"case_{cid:04d}.meta").write_text(
            json.dumps(meta, indent=2) + "\n"
        )

    print(f"Generated {len(pairs)} nested cases in {args.out}")


if __name__ == "__main__":
    main()
