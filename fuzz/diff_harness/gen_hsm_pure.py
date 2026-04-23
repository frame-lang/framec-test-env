#!/usr/bin/env python3
"""
Pure-Frame HSM parent-semantics fuzzer — Phase 4 of FUZZ_PLAN.md.

Tests the `=> $^` event-forward from a child handler, plus the
transition-guard semantic that suppresses post-forward statements in
the child when the parent's handler transitions.

Structure (depth=2):
  machine:
      $C0 => $P   (INITIAL — child, forwards drive() to parent)
      $C1 => $P   (sibling of $C0 under same parent)
      $P          (parent)
      $Q0 => $Q   (uncle child — in a different subtree)
      $Q          (uncle parent)

Child `$C0`'s `drive()`:
  pre-forward stmts  (set self.t_count = 1)
  => $^              (forward to $P)
  post-forward stmts (increment self.t_count — MUST be suppressed
                      when the parent transitions)

Parent `$P`'s `drive()` varies by axis:
  noop     — does nothing                  (no transition)
  sibling  — -> $C1                        (child sibling transition)
  uncle    — -> $Q0                        (cross-subtree transition)

Axes:
  parent_action         ["noop", "sibling", "uncle"]
  post_forward_stmts    [1, 2, 3]
  post_forward_structure ["linear", "if_guarded", "if_both_arms"]
  child_pre_stmts       [0, 1, 2]

Product: 3 × 3 × 3 × 3 = 81 cases.

Correctness is defined by the Python oracle's actual trace output;
all other backends must match byte-for-byte.

Usage:
    python3 gen_hsm_pure.py --max 81 --out ../cases/hsm
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path

PARENT_ACTIONS = ["noop", "sibling", "uncle"]
POST_FORWARD_STMTS = [1, 2, 3]
POST_FORWARD_STRUCTURES = ["linear", "if_guarded", "if_both_arms"]
CHILD_PRE_STMTS = [0, 1, 2]


def gen_child_body(pre_k: int, post_k: int, post_structure: str) -> list[str]:
    """Emit the child's `drive()` body.

      [pre_k times]       self.t_count = self.t_count + 0;  (no-op bump to 0)
      self.t_count = 1;   canonical pre-forward set
      => $^;              forward to parent
      <post_structure block (mutates t_count post_k times — MUST NOT RUN)>

    Post-forward stmts are emitted in PYTHON-CANONICAL syntax (indent
    + `:`). Per-target rewriters in `langs.py` translate to native
    form (C-family braces, Ruby/Lua `then/end`, Erlang `case of`)."""
    out = []
    # Pre-forward padding — some noop increments, then canonical set.
    # These run; they probe that pre-forward code is executed.
    for _ in range(pre_k):
        out.append("                self.t_count = self.t_count + 0;")
    out.append("                self.t_count = 1;")
    out.append("                => $^;")
    if post_structure == "linear":
        for _ in range(post_k):
            out.append("                self.t_count = self.t_count + 1;")
    elif post_structure == "if_guarded":
        # Fresh instance: self.x == 0, TRUE branch fires.
        out.append("                if self.x == 0:")
        for _ in range(post_k):
            out.append("                    self.t_count = self.t_count + 1;")
        out.append("                else:")
        out.append("                    self.t_count = self.t_count + 0;")
    elif post_structure == "if_both_arms":
        out.append("                if self.x == 0:")
        for _ in range(post_k):
            out.append("                    self.t_count = self.t_count + 1;")
        out.append("                else:")
        for _ in range(post_k):
            out.append("                    self.t_count = self.t_count + 1;")
    return out


def gen_parent_drive_body(parent_action: str) -> str:
    if parent_action == "noop":
        return "            drive() { self.parent_ran = self.parent_ran + 1; }"
    if parent_action == "sibling":
        return (
            "            drive() {\n"
            "                self.parent_ran = self.parent_ran + 1;\n"
            "                -> $C1\n"
            "            }"
        )
    if parent_action == "uncle":
        return (
            "            drive() {\n"
            "                self.parent_ran = self.parent_ran + 1;\n"
            "                -> $Q0\n"
            "            }"
        )
    raise ValueError(parent_action)


def gen_system(case_id: int, params: dict) -> tuple[str, str]:
    sys_name = f"Hsm{case_id:04d}"
    lines = []
    lines.append("@@target python_3")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append("        drive()")
    lines.append("        trace(): int")
    lines.append("        parent_count(): int")
    lines.append("        status(): str")
    lines.append("")
    lines.append("    machine:")

    # $C0 — INITIAL (child, forwards to parent $P)
    lines.append("        $C0 => $P {")
    lines.append("            drive() {")
    lines.extend(gen_child_body(
        params["child_pre_stmts"],
        params["post_forward_stmts"],
        params["post_forward_structure"],
    ))
    lines.append("            }")
    lines.append('            status(): str { @@:("C0") }')
    # Default-forward unhandled events (trace(), parent_count()) to $P
    # so the harness can observe domain state when parent_action=noop
    # leaves the machine in $C0.
    lines.append("            => $^")
    lines.append("        }")

    # $C1 — sibling child (target for "sibling" parent_action)
    lines.append("        $C1 => $P {")
    lines.append('            status(): str { @@:("C1") }')
    lines.append("            => $^")
    lines.append("        }")

    # $P — parent
    lines.append("        $P {")
    lines.append(gen_parent_drive_body(params["parent_action"]))
    lines.append("            trace(): int { @@:(self.t_count) }")
    lines.append("            parent_count(): int { @@:(self.parent_ran) }")
    lines.append('            status(): str { @@:("P") }')
    lines.append("        }")

    # $Q0 — uncle child (target for "uncle" parent_action)
    lines.append("        $Q0 => $Q {")
    lines.append('            status(): str { @@:("Q0") }')
    lines.append("            => $^")
    lines.append("        }")

    # $Q — uncle parent (separate subtree root)
    lines.append("        $Q {")
    lines.append("            trace(): int { @@:(self.t_count) }")
    lines.append("            parent_count(): int { @@:(self.parent_ran) }")
    lines.append('            status(): str { @@:("Q") }')
    lines.append("        }")

    lines.append("")
    lines.append("    domain:")
    lines.append("        x: int = 0")
    lines.append("        t_count: int = 0")
    lines.append("        parent_ran: int = 0")
    lines.append("}")
    return "\n".join(lines) + "\n", sys_name


def gen_meta(case_id: int, sys_name: str, params: dict) -> dict:
    """Metadata used by the per-lang renderer and for reporting.
    `expected` is informational — the live Python run is the oracle."""
    return {
        "trace_fmt": "v1",
        "harness_kind": "hsm",
        "sys_name": sys_name,
        "axes": {
            "parent_action": params["parent_action"],
            "post_forward_stmts": params["post_forward_stmts"],
            "post_forward_structure": params["post_forward_structure"],
            "child_pre_stmts": params["child_pre_stmts"],
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=81)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path,
                   default=Path(__file__).resolve().parents[1] / "cases" / "hsm")
    args = p.parse_args()

    random.seed(args.seed)
    axes = list(itertools.product(
        PARENT_ACTIONS, POST_FORWARD_STMTS,
        POST_FORWARD_STRUCTURES, CHILD_PRE_STMTS,
    ))
    random.shuffle(axes)
    axes = axes[:args.max]

    args.out.mkdir(parents=True, exist_ok=True)
    for f in args.out.glob("case_*.*"):
        f.unlink()

    for cid, (pa, pk, ps, cp) in enumerate(axes):
        params = dict(
            parent_action=pa,
            post_forward_stmts=pk,
            post_forward_structure=ps,
            child_pre_stmts=cp,
        )
        src, sys_name = gen_system(cid, params)
        meta = gen_meta(cid, sys_name, params)
        (args.out / f"case_{cid:04d}.frame").write_text(src)
        (args.out / f"case_{cid:04d}.meta").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Generated {len(axes)} hsm cases in {args.out}")


if __name__ == "__main__":
    main()
