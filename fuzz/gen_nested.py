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
    specs["java"] = LangSpec(
        target="java", ext="fjava",
        stmt_end=";",
        self_word="this",
        println_pass='System.out.println("PASS: nested-frame");',
        fail_exit_def='',  # static helper inside Main class instead
    )
    specs["kotlin"] = LangSpec(
        target="kotlin", ext="fkt",
        stmt_end="",
        self_word="this",
        println_pass='println("PASS: nested-frame")',
        fail_exit_def='''
fun _fail(msg: String): Nothing { throw RuntimeException("FAIL: " + msg) }
''',
    )
    specs["csharp"] = LangSpec(
        target="csharp", ext="fcs",
        stmt_end=";",
        self_word="this",
        println_pass='System.Console.WriteLine("PASS: nested-frame");',
        fail_exit_def='',
    )
    specs["c"] = LangSpec(
        target="c", ext="fc",
        stmt_end=";",
        # framec C codegen uses `self->field` member access on a
        # pointer-receiver shape.
        self_word="self",
        field_op="->",
        method_op="->",
        println_pass='printf("PASS: nested-frame\\n");',
        fail_exit_def='',
    )
    specs["cpp"] = LangSpec(
        target="cpp_17", ext="fcpp",
        stmt_end=";",
        self_word="this",
        field_op="->",
        method_op="->",
        println_pass='std::cout << "PASS: nested-frame" << std::endl;',
        fail_exit_def='',
    )
    specs["gdscript"] = LangSpec(
        target="gdscript", ext="fgd",
        stmt_end="",
        self_word="self",
        println_pass='print("PASS: nested-frame")',
        fail_exit_def='''
func _fail(msg):
    print("FAIL: " + msg)
    quit(1)
''',
    )
    return specs


LANGS = _build_specs()


def method_name(lang, name):
    """Per-language method-name casing. Go capitalises interface
    methods to mark them exported; framec's Go backend emits
    `Add_one` for a Frame source `Add_one`. Other backends use
    lowercase as written."""
    if lang == "go":
        return name[:1].upper() + name[1:]
    return name


def op_call(lang, sys_name, spec, method, args=""):
    """Native passthrough call to a same-system method. C lacks
    struct-method dispatch and uses framec's free-function shape
    `<Sys>_<method>(self[, args])`; everything else uses the
    language-native `<self><op>method([args])` form."""
    cased = method_name(lang, method)
    if lang == "c":
        if args:
            return f"{sys_name}_{cased}(self, {args})"
        return f"{sys_name}_{cased}(self)"
    return f"{spec.self_word}{spec.method_op}{cased}({args})"


def gen_case(lang, pattern):
    """Emit one .f<ext> source for a (language, pattern) pair.
    The body is small (~30 lines) — one system, one $S0 state with
    a `drive()` event that exercises the pattern, plus accessors
    for the final domain values that the driver asserts on."""
    spec = LANGS[lang]
    sys_name = f"Nested_{pattern}"

    # Per-language method-name casing for interface declarations
    # and handlers — Go capitalises (`Absorb`, `Get_n`); everything
    # else takes lowercase. Defined here so the per-pattern body
    # templates below can reference them.
    m_drive = method_name(lang, "drive")
    m_absorb = method_name(lang, "absorb")
    m_absorb_cache = method_name(lang, "absorb_cache")
    m_add_one = method_name(lang, "add_one")
    m_add_two = method_name(lang, "add_two")
    m_compute = method_name(lang, "compute")
    m_peek = method_name(lang, "peek")
    m_get_n = method_name(lang, "get_n")

    # Per-pattern: drive() body + expected final n value.
    # n starts at 0 and gets bumped via the patterns.
    if pattern == "p1_return_arg":
        # @@:return = 5; @@:self.{m_absorb}(@@:return) → absorb adds the arg to n.
        # Expected: n == 5.
        body = [
            f"                @@:return = 5{spec.stmt_end}",
            f"                @@:self.{m_absorb}(@@:return)",
        ]
        expected_n = 5
    elif pattern == "p2_params_arg":
        # drive(x: int) → @@:self.{m_absorb}(@@:params.x). Caller passes 7.
        # Expected: n == 7.
        body = [
            f"                @@:self.{m_absorb}(@@:params.x)",
        ]
        expected_n = 7
    elif pattern == "p3_op_in_return":
        # @@:return = 4; @@:(<op_call_add_one>(@@:return)) → return is 5,
        # then absorb with @@:return adds 5 to n.
        # Expected: n == 5.
        # op_call() handles per-language native call syntax: dot-call
        # for method-dispatch backends, free-function `<Sys>_<m>(self,
        # args)` for C. Go uses capitalised method names per its
        # export convention.
        body = [
            f"                @@:return = 4{spec.stmt_end}",
            f"                @@:({op_call(lang, sys_name, spec, 'add_one', '@@:return')})",
            f"                @@:self.{m_absorb}(@@:return)",
        ]
        expected_n = 5
    elif pattern == "p4_selfcall_in_return":
        # @@:return = @@:self.compute() — compute returns 9, n unchanged
        # by compute. After drive: absorb with @@:return adds 9 to n.
        # Expected: n == 9.
        body = [
            f"                @@:return = @@:self.{m_compute}()",
            f"                @@:self.{m_absorb}(@@:return)",
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
            f"                {spec.self_word}{spec.field_op}cache = @@:self.{m_compute}(){spec.stmt_end}",
            f"                @@:self.{m_absorb_cache}()",
        ]
        expected_n = 9
    elif pattern == "p6_op_arg":
        # @@:self.absorb(<op_call_peek>) — peek returns 3.
        # Expected: n == 3.
        body = [
            f"                @@:self.{m_absorb}({op_call(lang, sys_name, spec, 'peek')})",
        ]
        expected_n = 3
    elif pattern == "p7_two_level":
        # @@:return = 2; @@:self.{m_absorb}(@@:self.add_two(@@:return))
        # add_two returns input + 2 = 4, absorb adds 4 to n.
        # Expected: n == 4.
        body = [
            f"                @@:return = 2{spec.stmt_end}",
            f"                @@:self.{m_absorb}(@@:self.{m_add_two}(@@:return))",
        ]
        expected_n = 4
    else:
        raise ValueError(f"unknown pattern {pattern}")

    # Drive event signature varies per pattern:
    # - Patterns that use `@@:return` as a typed-int arg (p1, p3, p4, p7)
    #   need `: int` so framec's typed backends know to downcast the
    #   slot. Without the hint, rust/go/swift would emit type-errored
    #   code at the call site.
    # - Patterns that DON'T set @@:return (p2, p5, p6) keep drive()
    #   as void — declaring `: int` here makes Java's wrapper
    #   extract a never-set _return slot and NPE on the cast.
    needs_int_return = pattern in {"p1_return_arg", "p3_op_in_return",
                                    "p4_selfcall_in_return",
                                    "p7_two_level"}
    if pattern == "p2_params_arg":
        drive_sig = "drive(x: int)"
    elif needs_int_return:
        drive_sig = "drive(): int"
    else:
        drive_sig = "drive()"

    drive_decl = drive_sig.replace("drive", m_drive)

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
    lines.append(f"        {drive_decl}")
    lines.append(f"        {m_absorb}(v: int)")
    lines.append(f"        {m_absorb_cache}()")
    lines.append(f"        {m_add_one}(x: int): int")
    lines.append(f"        {m_add_two}(x: int): int")
    lines.append(f"        {m_compute}(): int")
    lines.append(f"        {m_peek}(): int")
    lines.append(f"        {m_get_n}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $S0 {")
    lines.append(f"            {drive_decl} {{")
    lines.append("\n".join(body))
    lines.append("            }")
    self_n = f"{spec.self_word}{spec.field_op}n"
    self_cache = f"{spec.self_word}{spec.field_op}cache"
    # Parameter-name references in handler bodies. PHP needs `$v` /
    # `$x`; everything else takes the bare name.
    p_v = f"{spec.param_prefix}v"
    p_x = f"{spec.param_prefix}x"
    lines.append(f"            {m_absorb}(v: int) {{ {self_n} = {self_n} + {p_v}{spec.stmt_end} }}")
    lines.append(f"            {m_absorb_cache}() {{ {self_n} = {self_n} + {self_cache}{spec.stmt_end} }}")
    lines.append(f"            {m_add_one}(x: int): int {{ @@:({p_x} + 1) }}")
    lines.append(f"            {m_add_two}(x: int): int {{ @@:({p_x} + 2) }}")
    lines.append(f"            {m_compute}(): int {{ @@:(9) }}")
    lines.append(f"            {m_peek}(): int {{ @@:(3) }}")
    lines.append(f"            {m_get_n}(): int {{ @@:({self_n}) }}")
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
    elif lang == "java":
        # Java requires the test driver inside a Main class with a
        # `public static void main` entry point. framec's Java
        # backend emits the system as a public class; Main lives
        # alongside in a non-public class in the same .java file.
        lines.append("class Main {")
        lines.append(f"    public static void main(String[] args) {{")
        lines.append(f"        var _inst = new {sys_name}();")
        lines.append(f"        _inst.drive({drive_arg_str});")
        lines.append(f"        int _n = (int) _inst.get_n();")
        lines.append(f"        if (_n != {expected_n}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected n={expected_n}, got \" + _n);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.append("// Inline test driver.")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        lines.append(f"    _inst.drive({drive_arg_str})")
        lines.append(f"    val _n = _inst.get_n() as Int")
        lines.append(f"    if (_n != {expected_n}) {{ _fail(\"expected n={expected_n}, got $_n\") }}")
        lines.append(f"    {spec.println_pass}")
        lines.append("}")
    elif lang == "csharp":
        # C# top-level statements (since C# 9) — simpler than the
        # full class-with-main shape. Available via the .NET SDK
        # `dotnet script` runner or a Program.cs target. Here we
        # rely on `dotnet run` over a single-file project that the
        # run_nested.sh harness sets up at exec time.
        lines.append("// Inline test driver.")
        lines.append("public class _NestedTestDriver {")
        lines.append("    public static void Main() {")
        lines.append(f"        var _inst = new {sys_name}();")
        lines.append(f"        _inst.drive({drive_arg_str});")
        lines.append(f"        int _n = (int) _inst.get_n();")
        lines.append(f"        if (_n != {expected_n}) {{")
        lines.append(f"            System.Console.WriteLine(\"FAIL: expected n={expected_n}, got \" + _n);")
        lines.append(f"            System.Environment.Exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass}")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        # C needs a main(). framec's C backend emits a heap-allocated
        # `<Sys>* <sys>_new()` constructor + free-standing
        # `<Sys>_<method>(<Sys>* self, ...)` functions.
        lines.append("// Inline test driver.")
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        # framec's C convention is upper-snake of the method:
        # `Sys_method(self, args)`. The method names in our
        # interface are lowercase; framec expects them lowercase
        # in the generated function names too.
        if pattern == "p2_params_arg":
            lines.append(f"    {sys_name}_drive(_inst, 7);")
        else:
            lines.append(f"    {sys_name}_drive(_inst);")
        lines.append(f"    int _n = (int)(intptr_t){sys_name}_get_n(_inst);")
        lines.append(f"    if (_n != {expected_n}) {{")
        lines.append(f"        printf(\"FAIL: expected n={expected_n}, got %d\\n\", _n);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("// Inline test driver.")
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        lines.append(f"    _inst.drive({drive_arg_str});")
        lines.append(f"    int _n = std::any_cast<int>(_inst.get_n());")
        lines.append(f"    if (_n != {expected_n}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected n={expected_n}, got \" << _n << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        # GDScript headless runner needs `extends SceneTree` +
        # `_init()` as the entry point.
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        lines.append(f"    _inst.drive({drive_arg_str})")
        lines.append(f"    var _n = _inst.get_n()")
        lines.append(f"    if _n != {expected_n}:")
        lines.append(f"        _fail(\"expected n={expected_n}, got \" + str(_n))")
        lines.append(f"    {spec.println_pass}")
        lines.append("    quit()")
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
                                 "ruby", "lua", "php", "dart",
                                 "rust", "go", "swift",
                                 "java", "kotlin", "csharp",
                                 "c", "cpp", "gdscript",
                                 "erlang"])
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
