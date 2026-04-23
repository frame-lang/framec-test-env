#!/usr/bin/env python3
"""
Pure-Frame @@:self fuzzer — Phase 3 of FUZZ_PLAN.md.

Generates Frame systems where an interface method `drive()` calls
`@@:self.<target>()` where <target> is either:

  transition — target handler transitions to a new state.
    Post-call statements in the caller MUST be suppressed (the
    transition-guard semantic). We observe via a `t_count` state-var:
    pre-call sets it to 1; post-call increments it; after drive
    returns, we query `trace()` — if it equals 1, the guard worked.

  noop — target handler doesn't transition.
    Post-call statements run normally; `t_count` reflects increments.

Axes:
  state_count     [2, 3, 5]
  hsm_depth       [0, 1, 2]   # 0=flat, 1=one parent, 2=grandparent chain
  variant         ["transition", "noop"]
  post_call_stmts [1, 2, 3]
  post_structure  ["linear", "if_guarded", "if_both_arms"]

Product: 3 × 3 × 2 × 3 × 3 = 162 cases.

Usage:
    python3 gen_selfcall_pure.py --max 162 --out ../cases/selfcall
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path

STATE_COUNTS = [2, 3, 5]
HSM_DEPTHS = [0, 1, 2]
VARIANTS = ["transition", "noop"]
POST_CALL_STMTS = [1, 2, 3]
POST_STRUCTURES = ["linear", "if_guarded", "if_both_arms"]


def state_name(i: int) -> str:
    return f"$S{i}"


def gen_caller_body(call_target: str, post_k: int, post_structure: str) -> list[str]:
    """Emit the `drive()` handler body.

      self.t_count = 1;
      @@:self.<call_target>();
      <post_structure block (mutates t_count post_k times)>

    The generator emits PYTHON-CANONICAL syntax (indent-based `if X:`
    / `else:` blocks) as the single source of truth. Per-target
    rewriters in `langs.py` translate to each backend's native form:
    C-family `if (X) { ... } else { ... }`, Ruby/Lua `if X then ...
    else ... end`, Erlang `case X of ... end`. Python and GDScript
    (indent + `:`) need no transform.

    All non-block statements use `self.` + `;` suffix — per-target
    rewriters translate `self.` to `this.`/`s.`/`$this->` etc. and
    strip `;` where the target language can't handle it."""
    out = []
    out.append("                self.t_count = 1;")
    out.append(f"                @@:self.{call_target}();")
    if post_structure == "linear":
        for _ in range(post_k):
            out.append("                self.t_count = self.t_count + 1;")
    elif post_structure == "if_guarded":
        # Fresh instance has `self.x == 0` so the TRUE branch always
        # fires. The FALSE branch is structurally there to exercise
        # the guard's handling of both arms.
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


def gen_system(case_id: int, params: dict) -> tuple[str, str]:
    sys_name = f"SelfCall{case_id:04d}"
    n = params["n_states"]
    depth = params["hsm_depth"]
    variant = params["variant"]
    call_target = "trigger" if variant == "transition" else "noop"
    next_state = state_name(1 % n)

    lines = []
    lines.append("@@target python_3")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append("        drive()")
    lines.append("        trigger()")
    lines.append("        noop()")
    lines.append("        trace(): int")
    lines.append("        status(): str")
    lines.append("")
    lines.append("    machine:")
    for i in range(n):
        st = state_name(i)
        has_parent = depth > 0 and 0 < i <= depth
        lines.append(f"        {st}{' => $S0' if has_parent else ''} {{")
        if i == 0:
            # Caller state.
            lines.append("            drive() {")
            lines.extend(gen_caller_body(
                call_target,
                params["post_call_stmts"],
                params["post_structure"],
            ))
            lines.append("            }")
            lines.append(f"            trigger() {{ -> {next_state} }}")
            lines.append("            noop() { self.x = self.x + 0; }")
            lines.append("            trace(): int { @@:(self.t_count) }")
            lines.append(f'            status(): str {{ @@:("s{i}") }}')
        else:
            # Other states: trigger/noop no-op, trace/status reflect state.
            lines.append("            trigger() { }")
            lines.append("            noop() { }")
            lines.append("            trace(): int { @@:(self.t_count) }")
            lines.append(f'            status(): str {{ @@:("s{i}") }}')
        if has_parent:
            lines.append("            => $^")
        lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append("        x: int = 0")
    lines.append("        t_count: int = 0")
    lines.append("}")
    return "\n".join(lines) + "\n", sys_name


def gen_meta(case_id: int, sys_name: str, params: dict) -> dict:
    """What the renderer and oracle need to know about the case."""
    n = params["n_states"]
    variant = params["variant"]
    post_k = params["post_call_stmts"]
    if variant == "transition":
        expected_state = f"s{1 % n}"
        expected_trace = 1            # guard suppresses post-call stmts
    else:
        expected_state = "s0"
        # `if self.x == 0` always fires for a fresh instance (x=0),
        # so post_k increments from either `linear` or the true arm.
        # `if_both_arms` has the same count because only one arm runs.
        expected_trace = 1 + post_k
    return {
        "trace_fmt": "v1",
        "harness_kind": "selfcall",
        "sys_name": sys_name,
        "axes": {
            "n_states": n,
            "hsm_depth": params["hsm_depth"],
            "variant": variant,
            "post_call_stmts": post_k,
            "post_structure": params["post_structure"],
        },
        "expected": {
            "state": expected_state,
            "trace": expected_trace,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=162)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path,
                   default=Path(__file__).resolve().parents[1] / "cases" / "selfcall")
    args = p.parse_args()

    random.seed(args.seed)
    axes = list(itertools.product(
        STATE_COUNTS, HSM_DEPTHS, VARIANTS, POST_CALL_STMTS, POST_STRUCTURES,
    ))
    random.shuffle(axes)
    axes = axes[:args.max]

    args.out.mkdir(parents=True, exist_ok=True)
    for f in args.out.glob("case_*.*"):
        f.unlink()

    for cid, (n, d, v, pk, ps) in enumerate(axes):
        params = dict(
            n_states=n, hsm_depth=d, variant=v,
            post_call_stmts=pk, post_structure=ps,
        )
        src, sys_name = gen_system(cid, params)
        meta = gen_meta(cid, sys_name, params)
        (args.out / f"case_{cid:04d}.frame").write_text(src)
        (args.out / f"case_{cid:04d}.meta").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Generated {len(axes)} selfcall cases in {args.out}")


if __name__ == "__main__":
    main()
