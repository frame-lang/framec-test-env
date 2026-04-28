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
                 "field_op", "method_op", "param_prefix",
                 "println_pass", "fail_exit_def")

    def __init__(self, **kw):
        defaults = {"field_op": ".", "method_op": ".", "param_prefix": ""}
        for k in self.__slots__:
            setattr(self, k, kw.get(k, defaults.get(k, "")))


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
    specs["typescript"] = LangSpec(
        target="typescript", ext="fts",
        stmt_end=";",
        self_word="this",
        println_pass='console.log("PASS: nested-frame");',
        fail_exit_def='''
function _fail(msg: string): never { console.log("FAIL: " + msg); process.exit(1); }
''',
    )
    specs["ruby"] = LangSpec(
        target="ruby", ext="frb",
        stmt_end="",
        self_word="self",
        println_pass='puts("PASS: nested-frame")',
        fail_exit_def='''
def _fail(msg)
  puts("FAIL: #{msg}")
  exit(1)
end
''',
    )
    specs["lua"] = LangSpec(
        target="lua", ext="flua",
        stmt_end="",
        self_word="self",
        # Lua method calls use `:` (auto-passes `self`); field access
        # uses `.`.
        method_op=":",
        println_pass='print("PASS: nested-frame")',
        fail_exit_def='''
function _fail(msg)
    print("FAIL: " .. msg)
    os.exit(1)
end
''',
    )
    specs["php"] = LangSpec(
        target="php", ext="fphp",
        stmt_end=";",
        self_word="$this",
        # PHP uses `->` for both field access and method calls.
        field_op="->",
        method_op="->",
        # PHP variables (incl. parameters) carry a `$` prefix.
        param_prefix="$",
        println_pass='echo "PASS: nested-frame\\n";',
        fail_exit_def='''
function _fail($msg) { echo "FAIL: $msg\\n"; exit(1); }
''',
    )
    specs["dart"] = LangSpec(
        target="dart", ext="fdart",
        stmt_end=";",
        self_word="this",
        println_pass='print("PASS: nested-frame");',
        fail_exit_def='''
void _fail(String msg) { print("FAIL: $msg"); throw Exception(msg); }
''',
    )
    specs["rust"] = LangSpec(
        target="rust", ext="frs",
        stmt_end=";",
        self_word="self",
        println_pass='println!("PASS: nested-frame");',
        # Rust assertion uses panic, which carries a non-zero exit
        # naturally. The `_fail` helper formats a fatal-panic message.
        fail_exit_def='''
fn _fail(msg: &str) -> ! { panic!("FAIL: {}", msg); }
''',
    )
    specs["go"] = LangSpec(
        target="go", ext="fgo",
        stmt_end="",
        # Go's generated handler signature uses `s` as the receiver
        # name; `self.X` would be a free-variable reference.
        self_word="s",
        println_pass='fmt.Println("PASS: nested-frame")',
        fail_exit_def='''
func _fail(msg string) { fmt.Println("FAIL: " + msg); os.Exit(1) }
''',
    )
    specs["swift"] = LangSpec(
        target="swift", ext="fswift",
        stmt_end="",
        self_word="self",
        println_pass='print("PASS: nested-frame")',
        fail_exit_def='''
func _fail(_ msg: String) -> Never { fatalError("FAIL: \\(msg)") }
''',
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
        # @@:return = 4; @@:(<self><method_op>add_one(@@:return)) → return is 5,
        # then absorb with @@:return adds 5 to n.
        # Expected: n == 5.
        body = [
            f"                @@:return = 4{spec.stmt_end}",
            f"                @@:({spec.self_word}{spec.method_op}add_one(@@:return))",
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
            f"                {spec.self_word}{spec.field_op}cache = @@:self.compute(){spec.stmt_end}",
            f"                @@:self.absorb_cache()",
        ]
        expected_n = 9
    elif pattern == "p6_op_arg":
        # @@:self.absorb(<self><method_op>peek()) — peek returns 3.
        # Expected: n == 3.
        body = [
            f"                @@:self.absorb({spec.self_word}{spec.method_op}peek())",
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
    # PHP requires the `<?php` opener at the very top of the source —
    # without it the generated file is treated as literal HTML. The
    # other backends pass through the prolog cleanly.
    if lang == "php":
        lines.append("<?php")
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
    self_n = f"{spec.self_word}{spec.field_op}n"
    self_cache = f"{spec.self_word}{spec.field_op}cache"
    # Parameter-name references in handler bodies. PHP needs `$v` /
    # `$x`; everything else takes the bare name.
    p_v = f"{spec.param_prefix}v"
    p_x = f"{spec.param_prefix}x"
    lines.append(f"            absorb(v: int) {{ {self_n} = {self_n} + {p_v}{spec.stmt_end} }}")
    lines.append(f"            absorb_cache() {{ {self_n} = {self_n} + {self_cache}{spec.stmt_end} }}")
    lines.append(f"            add_one(x: int): int {{ @@:({p_x} + 1) }}")
    lines.append(f"            add_two(x: int): int {{ @@:({p_x} + 2) }}")
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
    drive_arg_str = "7" if pattern == "p2_params_arg" else ""

    if lang == "python_3":
        lines.append("# Inline test driver — runs at module load.")
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        lines.append(f"_inst.drive({drive_arg_str})")
        lines.append(f"_n = _inst.get_n()")
        lines.append(f"if _n != {expected_n}:")
        lines.append(f"    _fail(f\"expected n={expected_n}, got {{_n}}\")")
        lines.append(spec.println_pass)
    elif lang == "javascript":
        lines.append("// Inline test driver — runs immediately.")
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        lines.append(f"_inst.drive({drive_arg_str});")
        lines.append(f"const _n = _inst.get_n();")
        lines.append(f"if (_n !== {expected_n}) {{ _fail(\"expected n={expected_n}, got \" + _n); }}")
        lines.append(spec.println_pass)
    elif lang == "typescript":
        lines.append("// Inline test driver.")
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        lines.append(f"_inst.drive({drive_arg_str});")
        lines.append(f"const _n: number = _inst.get_n();")
        lines.append(f"if (_n !== {expected_n}) {{ _fail(\"expected n={expected_n}, got \" + _n); }}")
        lines.append(spec.println_pass)
    elif lang == "ruby":
        lines.append("# Inline test driver.")
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        lines.append(f"_inst.drive({drive_arg_str})")
        lines.append(f"_n = _inst.get_n")
        lines.append(f"_fail(\"expected n={expected_n}, got #{{_n}}\") unless _n == {expected_n}")
        lines.append(spec.println_pass)
    elif lang == "lua":
        lines.append("-- Inline test driver.")
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        lines.append(f"_inst:drive({drive_arg_str})")
        lines.append(f"local _n = _inst:get_n()")
        lines.append(f"if _n ~= {expected_n} then _fail(\"expected n={expected_n}, got \" .. tostring(_n)) end")
        lines.append(spec.println_pass)
    elif lang == "php":
        lines.append("// Inline test driver.")
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        lines.append(f"$_inst->drive({drive_arg_str});")
        lines.append(f"$_n = $_inst->get_n();")
        lines.append(f"if ($_n !== {expected_n}) {{ _fail(\"expected n={expected_n}, got \" . $_n); }}")
        lines.append(spec.println_pass)
    elif lang == "dart":
        lines.append("// Inline test driver — wrapped in main() per Dart convention.")
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        lines.append(f"    _inst.drive({drive_arg_str});")
        lines.append(f"    final _n = _inst.get_n();")
        lines.append(f"    if (_n != {expected_n}) {{ _fail(\"expected n={expected_n}, got $_n\"); }}")
        lines.append(f"    {spec.println_pass}")
        lines.append("}")
    elif lang == "rust":
        lines.append("// Inline test driver — Rust requires a fn main().")
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        lines.append(f"    _inst.drive({drive_arg_str});")
        lines.append(f"    let _n = _inst.get_n();")
        lines.append(f"    if _n != {expected_n} {{ _fail(&format!(\"expected n={expected_n}, got {{}}\", _n)); }}")
        lines.append(f"    {spec.println_pass}")
        lines.append("}")
    elif lang == "go":
        # Go needs `package main` + `import` for fmt/os in the prolog.
        # The Frame source's prolog (above @@system) is the place;
        # framec passes it through. Emit those at the very top of
        # the file by splicing before the @@system. The generated
        # method receivers use `s` — matches our self_word.
        lines.insert(2, "package main")
        lines.insert(3, "")
        lines.insert(4, 'import "fmt"')
        lines.insert(5, 'import "os"')
        lines.insert(6, "")
        lines.append("// Inline test driver.")
        lines.append(spec.fail_exit_def)
        lines.append("func main() {")
        lines.append(f"    sm := New{sys_name}()")
        lines.append(f"    sm.Drive({drive_arg_str})")
        lines.append(f"    n := sm.Get_n()")
        lines.append(f"    if n != {expected_n} {{ _fail(fmt.Sprintf(\"expected n={expected_n}, got %d\", n)) }}")
        lines.append(f"    {spec.println_pass}")
        lines.append("}")
    elif lang == "swift":
        # Swift accepts top-level code in a single .swift file.
        lines.append("// Inline test driver.")
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        lines.append(f"_inst.drive({drive_arg_str})")
        lines.append(f"let _n = _inst.get_n()")
        lines.append(f"if _n != {expected_n} {{ _fail(\"expected n={expected_n}, got \\(_n)\") }}")
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
                        default=["python_3", "javascript", "typescript",
                                 "ruby", "lua", "php", "dart", "erlang"])
    # Rust/Go/Swift LangSpecs ship in this generator but are NOT
    # included in the default langs list because they expose an
    # unfixed framec codegen defect: when `@@:return` is passed
    # as an arg to a typed-int method, the framec output passes
    # `Option<&Box<dyn Any>>` (Rust) / `any` (Go) / `Any?` (Swift)
    # to a method expecting `i64` / `int` / `Int` without inserting
    # the downcast. Patterns p1, p3, p4, p7 fail; p2, p5, p6 pass.
    # Run explicitly with `--langs rust go swift` to reproduce
    # the defect for diagnosis.
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
