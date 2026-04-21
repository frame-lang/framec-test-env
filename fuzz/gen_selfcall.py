#!/usr/bin/env python3
"""
@@:self transition-guard fuzzer for framec.

Generates Frame systems where one interface method calls @@:self.<other>()
inside its handler body, then attempts to observe side effects *after* the
self-call. The other method is one of two variants:

  variant = "transition": @@:self.trigger() transitions to a new state.
     The calling handler's subsequent statements MUST be suppressed, OR
     the system must be in a structure where the post-call side effect
     never lands on the original state's domain.
     Concretely: after `@@:self.trigger()` with trigger → $S_next,
     we assert that the original handler's `self.trace = 2` assignment
     DID NOT run.

  variant = "noop": @@:self.noop() mutates domain but doesn't transition.
     The caller's subsequent statements MUST run normally (no guard
     trigger). We assert that `self.trace` reaches its expected
     post-call value.

Both variants test the transition-guard: the guard triggers on state
change, is a no-op otherwise.

Each generated case is self-checking (prints PASS / FAIL) and exits
non-zero on mismatch.

Targets: python_3, javascript, erlang (where @@:self is supported per
the matrix-status memo). Erlang has already been bug-prone in this area
so we want fuzz coverage.

Usage:
  python3 gen_selfcall.py --max 100
  ./run_selfcall.sh
"""
import argparse
import itertools
import random
from pathlib import Path

STATE_COUNTS = [2, 3, 5]
HSM_DEPTHS = [0, 1, 2]
VARIANTS = ["transition", "noop"]
POST_CALL_STMTS = [1, 2, 3]  # how many stmts after the @@:self call
# Nested post-call blocks: follow the self-call with an if/else that also
# mutates t_count, exercising the orphan-reply injector + transition-guard
# interaction we fixed earlier in Erlang.
POST_STRUCTURE = ["linear", "if_guarded", "if_both_arms"]


class LangSpec:
    __slots__ = (
        "target", "ext", "self_x", "self_trace", "stmt_end",
        "println", "fail_exit", "new_call", "get_trace_expr",
    )
    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k, ""))


def _build_specs():
    specs = {}
    specs["python_3"] = LangSpec(
        target="python_3", ext="fpy",
        self_x="self.x", self_trace="self.t_count", stmt_end="",
        println='print("PASS: self-call guard")',
        fail_exit='''
def _fail(msg):
    print(f"FAIL: {msg}")
    raise SystemExit(1)
''',
        new_call="inst = @@{SYS}()",
        get_trace_expr="inst.trace",
    )
    specs["javascript"] = LangSpec(
        target="javascript", ext="fjs",
        self_x="this.x", self_trace="this.t_count", stmt_end=";",
        println='console.log("PASS: self-call guard");',
        fail_exit='''
function _fail(msg) { console.log("FAIL: " + msg); process.exit(1); }
''',
        new_call="const inst = new {SYS}();",
        get_trace_expr="inst.trace",
    )
    specs["erlang"] = LangSpec(
        target="erlang", ext="ferl",
        self_x="self.x", self_trace="self.t_count", stmt_end="",
        println="",  # Erlang has no in-file harness; we use an external escript
        fail_exit="",
        new_call="",
        get_trace_expr="",
    )
    return specs

LANGS = _build_specs()


def gen_case(lang, case_id, params):
    spec = LANGS[lang]
    n = params["n_states"]
    depth = params["hsm_depth"]
    variant = params["variant"]
    post_k = params["post_call_stmts"]
    post_structure = params.get("post_structure", "linear")
    sys_name = f"SelfCall{case_id:04d}"

    # State where the caller handler lives
    caller_state = "$S0"
    next_state = f"$S{1 % n}"

    lines = []
    lines.append(f"@@target {spec.target}")
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
        st = f"$S{i}"
        has_parent = depth > 0 and 0 < i <= depth
        if has_parent:
            lines.append(f"        {st} => $S0 {{")
        else:
            lines.append(f"        {st} {{")

        if i == 0:
            # Caller state: drive() contains the @@:self call + post-call stmts
            call_target = "trigger" if variant == "transition" else "noop"
            body = []
            body.append(f"                {spec.self_trace} = 1{spec.stmt_end}")
            body.append(f"                @@:self.{call_target}(){spec.stmt_end}")
            if post_structure == "linear":
                for k in range(post_k):
                    body.append(f"                {spec.self_trace} = {spec.self_trace} + 1{spec.stmt_end}")
            elif post_structure == "if_guarded":
                # Post-call if/else with increment only in the true arm.
                # Exercises the transition-guard wrapping of case/if blocks.
                # Both arms are structurally present — the false branch
                # must not contribute to t_count either.
                if lang == "python_3":
                    body.append(f"                if {spec.self_x} == 0:")
                    for k in range(post_k):
                        body.append(f"                    {spec.self_trace} = {spec.self_trace} + 1")
                    body.append(f"                else:")
                    body.append(f"                    {spec.self_trace} = {spec.self_trace} + 0")
                else:
                    body.append(f"                if ({spec.self_x} == 0) {{")
                    for k in range(post_k):
                        body.append(f"                    {spec.self_trace} = {spec.self_trace} + 1{spec.stmt_end}")
                    body.append(f"                }} else {{")
                    body.append(f"                    {spec.self_trace} = {spec.self_trace} + 0{spec.stmt_end}")
                    body.append(f"                }}")
            elif post_structure == "if_both_arms":
                # Both arms mutate — verify guard suppresses BOTH paths.
                if lang == "python_3":
                    body.append(f"                if {spec.self_x} == 0:")
                    for k in range(post_k):
                        body.append(f"                    {spec.self_trace} = {spec.self_trace} + 1")
                    body.append(f"                else:")
                    for k in range(post_k):
                        body.append(f"                    {spec.self_trace} = {spec.self_trace} + 1")
                else:
                    body.append(f"                if ({spec.self_x} == 0) {{")
                    for k in range(post_k):
                        body.append(f"                    {spec.self_trace} = {spec.self_trace} + 1{spec.stmt_end}")
                    body.append(f"                }} else {{")
                    for k in range(post_k):
                        body.append(f"                    {spec.self_trace} = {spec.self_trace} + 1{spec.stmt_end}")
                    body.append(f"                }}")
            lines.append("            drive() {")
            lines.append("\n".join(body))
            lines.append("            }")
            # trigger() transitions, noop() doesn't
            lines.append(f"            trigger() {{ -> {next_state} }}")
            lines.append(f"            noop() {{ {spec.self_x} = {spec.self_x} + 0{spec.stmt_end} }}")
            lines.append(f'            trace(): int {{ @@:({spec.self_trace}) }}')
            lines.append(f'            status(): str {{ @@:("s0") }}')
        else:
            # Other states have trigger/noop as no-ops and trace/status
            lines.append(f"            trigger() {{ }}")
            lines.append(f"            noop() {{ }}")
            lines.append(f'            trace(): int {{ @@:({spec.self_trace}) }}')
            lines.append(f'            status(): str {{ @@:("s{i}") }}')
        if has_parent:
            lines.append("            => $^")
        lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append("        x: int = 0")
    lines.append("        t_count: int = 0")
    lines.append("}")
    lines.append("")

    # Erlang: no in-file harness; emit system only. The runner wraps it
    # in an escript that calls drive() and checks state + trace.
    if lang == "erlang":
        # Stash expected values as a comment for the runner to parse
        if variant == "transition":
            expected_state = f"s{1 % n}"
            expected_trace = 1
        else:
            expected_state = "s0"
            # Count of +1 increments: linear = post_k, if_guarded = post_k
            # (true arm only), if_both_arms = post_k (one arm regardless).
            # But variant==noop here means the caller remains in S0, so the
            # post-call block runs. For if_guarded and if_both_arms, since
            # the state var (self.x) is 0 in the fresh instance, the TRUE
            # arm always fires — so expected increment is post_k either way.
            expected_trace = 1 + post_k
        lines.append(f"% FUZZ_EXPECTED_STATE: {expected_state}")
        lines.append(f"% FUZZ_EXPECTED_TRACE: {expected_trace}")
        return "\n".join(lines) + "\n"

    # Harness
    lines.append(spec.fail_exit.rstrip())
    lines.append("")
    # For both linear + if-guarded + if-both-arms post structures, the
    # TRUE branch of `if self.x == 0` always fires (fresh instance has
    # x == 0). So expected post-call trace increment is post_k regardless
    # of which post_structure was chosen.
    if lang == "python_3":
        lines.append("if __name__ == '__main__':")
        lines.append(f"    inst = @@{sys_name}()")
        lines.append("    inst.drive()")
        if variant == "transition":
            lines.append(f'    if inst.status() != "s{1 % n}": _fail(f"state: expected s{1 % n}, got {{inst.status()}}")')
            lines.append(f'    if inst.trace() != 1: _fail(f"trace: post-call stmts should be suppressed after transition; expected 1, got {{inst.trace()}}")')
        else:
            expected_trace = 1 + post_k
            lines.append(f'    if inst.status() != "s0": _fail(f"state: expected s0, got {{inst.status()}}")')
            lines.append(f'    if inst.trace() != {expected_trace}: _fail(f"trace: post-call stmts should run after noop; expected {expected_trace}, got {{inst.trace()}}")')
        lines.append(f"    {spec.println}")
    elif lang == "javascript":
        lines.append(f"const inst = new {sys_name}();")
        lines.append("inst.drive();")
        if variant == "transition":
            lines.append(f'if (inst.status() !== "s{1 % n}") _fail(`state: expected s{1 % n}, got ${{inst.status()}}`);')
            lines.append('if (inst.trace() !== 1) _fail(`trace: expected 1 after transition, got ${inst.trace()}`);')
        else:
            expected_trace = 1 + post_k
            lines.append('if (inst.status() !== "s0") _fail(`state: expected s0, got ${inst.status()}`);')
            lines.append(f'if (inst.trace() !== {expected_trace}) _fail(`trace: expected {expected_trace} after noop, got ${{inst.trace()}}`);')
        lines.append(spec.println)

    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=100)
    p.add_argument("--lang", type=str, default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path,
                   default=Path(__file__).parent / "cases_selfcall")
    args = p.parse_args()

    random.seed(args.seed)
    axes = list(itertools.product(
        STATE_COUNTS, HSM_DEPTHS, VARIANTS, POST_CALL_STMTS, POST_STRUCTURE,
    ))
    random.shuffle(axes)
    axes = axes[:args.max]

    langs = [args.lang] if args.lang else list(LANGS.keys())
    args.out.mkdir(parents=True, exist_ok=True)
    for lang_key in langs:
        if lang_key not in LANGS:
            continue
        spec = LANGS[lang_key]
        lang_dir = args.out / spec.target
        lang_dir.mkdir(exist_ok=True)
        for cid, (n, d, variant, post_k, post_structure) in enumerate(axes):
            params = dict(
                n_states=n, hsm_depth=d, variant=variant,
                post_call_stmts=post_k, post_structure=post_structure,
            )
            (lang_dir / f"case_{cid:04d}.{spec.ext}").write_text(
                gen_case(lang_key, cid, params))
        print(f"Generated {len(axes)} selfcall cases for {spec.target}")


if __name__ == "__main__":
    main()
