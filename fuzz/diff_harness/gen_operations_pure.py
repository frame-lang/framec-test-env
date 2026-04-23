#!/usr/bin/env python3
"""
Pure-Frame operations fuzzer — Phase 5 of FUZZ_PLAN.md.

Exercises the `operations:` block across axes:
  - caller_context: how the op is invoked — via interface, from inside
    another operation, or from a state handler body.
  - return_type: int | str | bool.
  - domain_access: op body reads domain, mutates domain, or neither.

Frame architectural notes (per the author, 2026-04-23):

  1. Frame syntax is translated per-target by framec: `@@system`,
     `$State`, `-> $State`, `=> $^`, `@@:(expr)`, `@@:return(expr)`,
     `@@:self.event()`, `$.var`, domain field access via `self.`
     (under framec's indirection rules).
  2. Native syntax in handler / action / operation bodies is passed
     through verbatim. Framec does NOT mangle it.
  3. The target compiler catches bad native syntax.

Consequences for a 17-backend fuzz: one Frame source can't use
syntax that is native-specific to any single target. Shared ground:
  - int literals (42), str literals ("hello") — portable.
  - Bool literals (`true`/`True`) — NOT portable. Use comparison
    expressions (`self.counter == 10`) instead.
  - Method names starting with a capital letter — valid in every
    target. Lowercase-leading names fail in Go (requires PascalCase
    for exported methods) and clash with Python-flavoured rewriters.
  - Semicolon statement termination — valid in Python (no-op),
    required by brace-family.

For dispatch syntax that is fundamentally target-divergent (Lua's
colon-dispatch, C's free-function form, Erlang's module-function
form), the fuzz harness per-target `rewrite_trace` layer does the
canonical-to-native rewrite. That is NOT framec territory — it is
the harness-level source preprocessor, sitting between the canonical
Python-style generator output and framec's input.

Every case compiles to exactly the same driver shape, emitting a
fixed TRACE sequence that the Python oracle produces authoritatively:

  TRACE: direct <value>            -- result of direct `inst.op(...)`
  TRACE: via_event <value>         -- result after `inst.drive()` sets
                                       self.result via the op call
  TRACE: counter <int>             -- final domain counter
  TRACE: done

Byte-equal diff across every backend defines correctness.

Product: 3 × 3 × 3 = 27 cases.

Usage:
    python3 gen_operations_pure.py --max 27 --out ../cases/operations
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path

CALLER_CONTEXTS = ["interface", "op_to_op", "action"]
RETURN_TYPES = ["int", "str", "bool"]
DOMAIN_ACCESS = ["none", "read", "write"]


# The portable source-side expression we return for each type with
# `domain_access == "none"`. Int and str literals are lexically
# identical across all 17 targets (42, "hello"). Bool cannot use the
# literal `true` (Python wants `True`); instead we use a comparison
# that evaluates to true in every target's semantics, which Frame
# passes through unchanged.
def base_value(rtype: str) -> str:
    return {"int": "42", "str": '"hello"', "bool": "self.counter == 10"}[rtype]


def expected_trace_value(rtype: str, domain_access: str) -> str:
    """The value the op returns under the oracle's trace, as a string.

    For int reads/writes, trace shows the counter's value (10 / 11).
    For str/bool reads/writes, the op still mutates counter but
    returns the base literal — the domain-access axis only affects
    the counter trace line, not the op's return."""
    if rtype == "int":
        if domain_access == "read":
            return "10"
        if domain_access == "write":
            return "11"
        return "42"
    if rtype == "bool":
        return "true"
    # str
    return "hello"


def op_body(rtype: str, domain_access: str) -> list[str]:
    """Emit the operation body using native-target `return`.

    For `none`: op returns the base expression (literal or portable bool).
    For `read`:
      - int: returns self.counter (pre-increment).
      - str / bool: still computes the same base expression; the
        domain read is implicit via self.counter for bool.
    For `write`: increments counter, then returns — same per-type
    mapping as `read`.

    Return values:
      int none=42, read=10, write=11
      str (any) = "hello"
      bool (any) = (self.counter == 10) / (self.counter > 10) /
                   (self.counter > 10) — always true in MVP cases."""
    lines = []
    if domain_access == "write":
        lines.append("                self.counter = self.counter + 1;")
    if rtype == "int":
        expr = "self.counter" if domain_access in ("read", "write") else "42"
    elif rtype == "bool":
        # After a write the counter is 11; after a read it's 10. Pick a
        # portable comparison that is true in both cases so the expected
        # trace value is consistent ("true") across the 3 domain_access
        # values. (true/false variation is a later axis.)
        if domain_access == "write":
            expr = "self.counter > 10"      # 11 > 10 → true
        elif domain_access == "read":
            expr = "self.counter >= 10"     # 10 >= 10 → true
        else:
            expr = "self.counter == 10"     # initial 10 → true
    else:  # str
        expr = '"hello"'
    # Trailing `;` is valid in Python and required by brace-family
    # targets (Java, C, Rust, Dart, etc.). Omitting it works for some
    # backends but not all — the portable choice is to include it.
    lines.append(f"                return {expr};")
    return lines


def gen_system(case_id: int, params: dict) -> tuple[str, str]:
    sys_name = f"Op{case_id:04d}"
    rtype = params["return_type"]
    ctx = params["caller_context"]
    da = params["domain_access"]
    # Portable domain defaults. `0`, `""` are lexically identical in every
    # target. Bool literals diverge (`true`/`True`), so use a comparison
    # that every target evaluates to false: `(1 == 0)`.
    default_ret = {"int": "0", "str": '""', "bool": "(1 == 0)"}[rtype]

    lines = []
    lines.append("@@target python_3")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    operations:")
    lines.append(f"        Op(): {rtype} {{")
    lines.extend(op_body(rtype, da))
    lines.append("        }")

    # op_to_op: wrapper operation that calls op() and returns the same.
    if ctx == "op_to_op":
        lines.append(f"        OpOuter(): {rtype} {{")
        lines.append(f"                return self.Op();")
        lines.append("        }")

    lines.append("")
    lines.append("    interface:")
    lines.append("        drive()")
    lines.append(f"        get_result(): {rtype}")
    lines.append("        get_counter(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $A {")
    lines.append("            drive() {")

    if ctx == "interface":
        lines.append("                self.result = self.Op();")
    elif ctx == "op_to_op":
        lines.append("                self.result = self.OpOuter();")
    else:  # action
        lines.append("                self.result = self.Bump();")

    lines.append("            }")
    lines.append(f"            get_result(): {rtype} {{ @@:(self.result) }}")
    lines.append("            get_counter(): int { @@:(self.counter) }")
    lines.append("        }")
    lines.append("")

    if ctx == "action":
        lines.append("    actions:")
        lines.append(f"        Bump(): {rtype} {{")
        lines.append(f"                return self.Op();")
        lines.append("        }")
        lines.append("")

    lines.append("    domain:")
    lines.append(f"        result: {rtype} = {default_ret}")
    lines.append("        counter: int = 10")
    lines.append("}")
    return "\n".join(lines) + "\n", sys_name


def gen_meta(case_id: int, sys_name: str, params: dict) -> dict:
    return {
        "trace_fmt": "v1",
        "harness_kind": "operations",
        "sys_name": sys_name,
        "axes": params,
        "expected_value": expected_trace_value(
            params["return_type"], params["domain_access"]
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=27)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "cases" / "operations",
    )
    args = p.parse_args()

    random.seed(args.seed)
    axes = list(
        itertools.product(
            CALLER_CONTEXTS,
            RETURN_TYPES,
            DOMAIN_ACCESS,
        )
    )
    random.shuffle(axes)
    axes = axes[: args.max]

    args.out.mkdir(parents=True, exist_ok=True)
    for f in args.out.glob("case_*.*"):
        f.unlink()

    for cid, (ctx, rt, da) in enumerate(axes):
        params = dict(
            caller_context=ctx,
            return_type=rt,
            domain_access=da,
        )
        src, sys_name = gen_system(cid, params)
        meta = gen_meta(cid, sys_name, params)
        (args.out / f"case_{cid:04d}.frame").write_text(src)
        (args.out / f"case_{cid:04d}.meta").write_text(
            json.dumps(meta, indent=2) + "\n"
        )

    print(f"Generated {len(axes)} operations cases in {args.out}")


if __name__ == "__main__":
    main()
