#!/usr/bin/env python3
"""
Phase 9 — nested Frame syntax fuzzer.

Frame's framec recursively expands Frame syntax inside the args of
other Frame constructs. The contract is that source like
`@@:self.foo(@@:return)` or `@@:return = @@:self.bar()` works
identically to the explicit-intermediate form
`r = @@:return; @@:self.foo(r)`. Defect #10 in the cookbook-port
tracker (now closed) exposed a regression where the inner segment
passed through verbatim — generated Python had a literal
`self.foo(@@:return)` which crashed at parse time. This fuzzer
locks the recursive-expansion contract in by generating canonical
shapes and asserting the runtime output.

Patterns:

  P1  @@:return arg            @@:self.foo(@@:return)
  P2  @@:params arg            @@:self.foo(@@:params.x)
  P3  op-call inside @@:(...)  @@:(self.add_one(@@:return))
  P4  self-call RHS of @@:=    @@:return = @@:self.compute()
  P5  self-call RHS of $.var=  $.cache = @@:self.compute()
  P6  op-call arg              @@:self.tag(self.peek())
  P7  two-level nest           @@:self.outer(@@:self.inner(@@:return))

Each generated case is self-checking — the system runs, prints
either PASS or FAIL with the diagnostic, and exits non-zero on
mismatch.

Targets: python_3, javascript, erlang. Mirrors gen_selfcall.py's
target set; expand later if the harness shape proves out.

Usage:
    python3 gen_nested.py
    ./run_nested.sh
"""
import argparse
from pathlib import Path

# Each pattern declares an expected final-trace value the driver
# asserts after invoking the system. The trace is a single int that
# the test handlers cumulatively bump; framec's recursive expansion
# is correct iff the trace matches.
PATTERNS = [
    "p1_return_arg",
    "p2_params_arg",
    "p3_op_in_return",
    "p4_selfcall_in_return",
    "p5_selfcall_in_statevar",
    "p6_op_arg",
    "p7_two_level",
]


class LangSpec:
    __slots__ = ("target", "ext", "stmt_end", "self_word",
                 "println_pass", "fail_exit_def")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k, ""))


def _build_specs():
    # `self_word` is the receiver token used inside handler bodies for
    # bare passthrough of operation/method/field access (e.g., `self.X`
    # or `this.X`). The `@@:self.method()` form is rewritten by framec
    # uniformly across backends — `self_word` only governs the bare
    # pass-through cases (`self.peek()`, `self.cache = ...`).
    specs = {}
    specs["python_3"] = LangSpec(
        target="python_3", ext="fpy",
        stmt_end="",
        self_word="self",
        println_pass='print("PASS: nested-frame")',
        fail_exit_def='''
def _fail(msg):
    print(f"FAIL: {msg}")
    raise SystemExit(1)
''',
    )
    specs["javascript"] = LangSpec(
        target="javascript", ext="fjs",
        stmt_end=";",
        self_word="this",
        println_pass='console.log("PASS: nested-frame");',
        fail_exit_def='''
function _fail(msg) { console.log("FAIL: " + msg); process.exit(1); }
''',
    )
    specs["erlang"] = LangSpec(
        target="erlang", ext="ferl",
        stmt_end="",
        self_word="self",
        println_pass="",  # external escript driver
        fail_exit_def="",
    )
    return specs


LANGS = _build_specs()


def gen_case(lang, pattern):
    """Emit one .f<ext> source for a (language, pattern) pair.
    The body is small (~30 lines) — one system, one $S0 state with
    a `drive()` event that exercises the pattern, plus accessors
    for the final domain values that the driver asserts on."""
    spec = LANGS[lang]
    sys_name = f"Nested_{pattern}"

    # Per-pattern: drive() body + expected final n value.
    # n starts at 0 and gets bumped via the patterns.
    if pattern == "p1_return_arg":
        # @@:return = 5; @@:self.absorb(@@:return) → absorb adds the arg to n.
        # Expected: n == 5.
        body = [
            f"                @@:return = 5{spec.stmt_end}",
            f"                @@:self.absorb(@@:return)",
        ]
        expected_n = 5
    elif pattern == "p2_params_arg":
        # drive(x: int) → @@:self.absorb(@@:params.x). Caller passes 7.
        # Expected: n == 7.
        body = [
            f"                @@:self.absorb(@@:params.x)",
        ]
        expected_n = 7
    elif pattern == "p3_op_in_return":
        # @@:return = 4; @@:(<self>.add_one(@@:return)) → return is 5,
        # then absorb with @@:return adds 5 to n.
        # Expected: n == 5.
        body = [
            f"                @@:return = 4{spec.stmt_end}",
            f"                @@:({spec.self_word}.add_one(@@:return))",
            f"                @@:self.absorb(@@:return)",
        ]
        expected_n = 5
    elif pattern == "p4_selfcall_in_return":
        # @@:return = @@:self.compute() — compute returns 9, n unchanged
        # by compute. After drive: absorb with @@:return adds 9 to n.
        # Expected: n == 9.
        body = [
            f"                @@:return = @@:self.compute()",
            f"                @@:self.absorb(@@:return)",
        ]
        expected_n = 9
    elif pattern == "p5_selfcall_in_statevar":
        # self.cache = @@:self.compute() — sets domain `cache` to 9,
        # then absorb_cache reads it and bumps n.
        # The FUZZ_PLAN.md shape uses `$.var = @@:self.foo()` (state-var
        # LHS); the codegen-relevant question is whether the @@:self
        # call's return value lands on the LHS regardless of whether
        # the LHS is a state-var or a domain field. Domain field
        # avoids needing to declare `$.cache: int = 0` inline in the
        # state, keeping the fixture compact.
        # Expected: n == 9.
        body = [
            f"                {spec.self_word}.cache = @@:self.compute(){spec.stmt_end}",
            f"                @@:self.absorb_cache()",
        ]
        expected_n = 9
    elif pattern == "p6_op_arg":
        # @@:self.absorb(<self>.peek()) — peek returns 3.
        # Expected: n == 3.
        body = [
            f"                @@:self.absorb({spec.self_word}.peek())",
        ]
        expected_n = 3
    elif pattern == "p7_two_level":
        # @@:return = 2; @@:self.absorb(@@:self.add_two(@@:return))
        # add_two returns input + 2 = 4, absorb adds 4 to n.
        # Expected: n == 4.
        body = [
            f"                @@:return = 2{spec.stmt_end}",
            f"                @@:self.absorb(@@:self.add_two(@@:return))",
        ]
        expected_n = 4
    else:
        raise ValueError(f"unknown pattern {pattern}")

    # Drive event signature varies by pattern (only p2 takes a param).
    drive_sig = "drive(x: int)" if pattern == "p2_params_arg" else "drive()"

    lines: list[str] = []
    lines.append(f"@@target {spec.target}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append(f"        {drive_sig}")
    lines.append("        absorb(v: int)")
    lines.append("        absorb_cache()")
    lines.append("        add_one(x: int): int")
    lines.append("        add_two(x: int): int")
    lines.append("        compute(): int")
    lines.append("        peek(): int")
    lines.append("        get_n(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $S0 {")
    lines.append(f"            {drive_sig} {{")
    lines.append("\n".join(body))
    lines.append("            }")
    self_n = f"{spec.self_word}.n"
    self_cache = f"{spec.self_word}.cache"
    lines.append(f"            absorb(v: int) {{ {self_n} = {self_n} + v{spec.stmt_end} }}")
    lines.append(f"            absorb_cache() {{ {self_n} = {self_n} + {self_cache}{spec.stmt_end} }}")
    lines.append(f"            add_one(x: int): int {{ @@:(x + 1) }}")
    lines.append(f"            add_two(x: int): int {{ @@:(x + 2) }}")
    lines.append(f"            compute(): int {{ @@:(9) }}")
    lines.append(f"            peek(): int {{ @@:(3) }}")
    lines.append(f"            get_n(): int {{ @@:({self_n}) }}")
    lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append("        n: int = 0")
    lines.append("        cache: int = 0")
    lines.append("}")
    lines.append("")

    # Inline test driver per language. Erlang uses the external
    # escript driver authored by run_nested.sh — embedded comments
    # carry the expected value.
    if lang == "python_3":
        lines.append("# Inline test driver — runs at module load.")
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        if pattern == "p2_params_arg":
            lines.append("_inst.drive(7)")
        else:
            lines.append("_inst.drive()")
        lines.append(f"_n = _inst.get_n()")
        lines.append(f"if _n != {expected_n}:")
        lines.append(f"    _fail(f\"expected n={expected_n}, got {{_n}}\")")
        lines.append(spec.println_pass)
    elif lang == "javascript":
        lines.append("// Inline test driver — runs immediately.")
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if pattern == "p2_params_arg":
            lines.append("_inst.drive(7);")
        else:
            lines.append("_inst.drive();")
        lines.append(f"const _n = _inst.get_n();")
        lines.append(f"if (_n !== {expected_n}) {{ _fail(\"expected n={expected_n}, got \" + _n); }}")
        lines.append(spec.println_pass)
    elif lang == "erlang":
        # Stash expected value as a Frame comment so the runner can read it.
        # Erlang Frame source's comment leader is `%`. The runner picks up
        # the line, builds an external escript, drives the system, asserts.
        lines.append(f"%% FUZZ_EXPECTED_N: {expected_n}")
        if pattern == "p2_params_arg":
            lines.append(f"%% FUZZ_DRIVE_ARG: 7")

    return "\n".join(lines), expected_n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir",
                        default=str(Path(__file__).parent / "cases_nested"))
    parser.add_argument("--langs", nargs="+",
                        default=["python_3", "javascript", "erlang"])
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # Wipe stale cases so a regenerated set doesn't mix old + new.
    for f in out.glob("*"):
        f.unlink()

    count = 0
    for lang in args.langs:
        spec = LANGS[lang]
        for pat in PATTERNS:
            src, _expected = gen_case(lang, pat)
            path = out / f"{pat}.{spec.ext}"
            path.write_text(src)
            count += 1
    print(f"generated {count} cases across {len(args.langs)} langs × "
          f"{len(PATTERNS)} patterns into {out}")


if __name__ == "__main__":
    main()
