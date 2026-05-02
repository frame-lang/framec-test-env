#!/usr/bin/env python3
"""
Phase 20 — `const` domain fields + `@@:system.state` access fuzz (Wave 1).

Two Frame features tested:
  1. `const k: int = LIT` in the domain block — immutable field
     initialized to a literal. Read via getter; verify the value
     matches the declaration.
  2. `@@:system.state` — reads the current state name as a string.
     Tested AFTER a transition to verify the runtime updates the
     state name correctly.

Wave 1 design:
  Patterns (3): const-read, system-state-initial, system-state-after-transition.
  Value tuples (10): (LIT) per case for const tests; ignored for state tests.
  Total: 3 × 10 = 30 cases per lang × 17 langs = 510.

Smoke filter: one case per pattern (first value tuple) → 3 smoke
cases per lang.

Usage:
    python3 gen_const_sys.py
    ./run_const_sys.sh --tier=smoke
"""
from pathlib import Path

from gen_nested import LANGS, method_name


# State-name string returned by @@:system.state. Per-language
# casing may differ — framec emits the exact state name without
# the leading $. State `$S0` → "S0" verbatim across all backends.
EXPECTED_STATE_NAME = "S0"
EXPECTED_STATE_AFTER_TRANSITION = "S1"


class Pattern:
    __slots__ = ("name", "build_states", "compute", "verify_kind",
                 "pre_drive_seq")

    def __init__(self, name, build_states, compute, verify_kind,
                 pre_drive_seq):
        self.name = name
        self.build_states = build_states
        self.compute = compute  # lambda(lit) -> int OR string
        # 'int' or 'string' — selects the verify-method's return
        # type and the comparison style in the driver.
        self.verify_kind = verify_kind
        self.pre_drive_seq = pre_drive_seq


def _build_p1_const_field(spec, lang, lit):
    """P1: const domain field declared with literal initializer.
    Read via get_const(): int. Verify value == LIT."""
    m_get = method_name(lang, "get_const")
    return [
        f"        $S0 {{",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}k) }}",
        f"        }}",
    ], f"        const k: int = {lit}"


def _build_p2_system_state_initial(spec, lang, lit):
    """P2: read @@:system.state right after construction.
    Should return "S0" (initial state name, no $ prefix)."""
    m_get = method_name(lang, "get_state")
    return [
        f"        $S0 {{",
        f"            {m_get}(): str {{ @@:(@@:system.state) }}",
        f"        }}",
    ], f"        f: int = {lit}"


def _build_p3_system_state_after_transition(spec, lang, lit):
    """P3: drive() transitions to $S1; get_state() reads
    @@:system.state. Verify the runtime updates the state name to
    "S1" after the transition."""
    m_drive = method_name(lang, "drive")
    m_get = method_name(lang, "get_state")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1",
        f"            }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_get}(): str {{ @@:(@@:system.state) }}",
        f"        }}",
    ], f"        f: int = {lit}"


PATTERNS = [
    Pattern("p1_const_field",
            _build_p1_const_field,
            lambda lit: lit,
            "int",
            []),
    Pattern("p2_sys_state_initial",
            _build_p2_system_state_initial,
            lambda lit: EXPECTED_STATE_NAME,
            "string",
            []),
    Pattern("p3_sys_state_after_xfer",
            _build_p3_system_state_after_transition,
            lambda lit: EXPECTED_STATE_AFTER_TRANSITION,
            "string",
            ["drive"]),
]


VALUE_TUPLES = [
    1, 5, -3, 0, 100, 50, -7, 1, 99, -1,
]


def case_id(pattern, vt_idx):
    return f"cs_{pattern.name}__t{vt_idx}"


def equiv_class(pattern):
    return pattern.name


def enumerate_cases():
    seen = set()
    for pattern in PATTERNS:
        for idx, lit in enumerate(VALUE_TUPLES):
            cid = case_id(pattern, idx)
            cls = equiv_class(pattern)
            is_smoke = cls not in seen
            if is_smoke:
                seen.add(cls)
            expected = pattern.compute(lit)
            yield (cid, cls, expected, pattern, lit, is_smoke)


def gen_case(lang, cid, equiv, expected, pattern, lit, is_smoke):
    spec = LANGS[lang]
    sys_name = f"ConstSys_{cid}"

    if pattern.verify_kind == "int":
        m_verify = method_name(lang, "get_const")
    elif pattern.name == "p2_sys_state_initial":
        m_verify = method_name(lang, "get_state")
    else:
        m_verify = method_name(lang, "get_state")

    state_lines, domain_line = pattern.build_states(spec, lang, lit)

    interface_methods = set()
    for m in pattern.pre_drive_seq:
        interface_methods.add(method_name(lang, m))
    interface_methods.add(m_verify)

    lines = []
    lines.append(f'@@[target("{spec.target}")]')
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_VAL: {expected}")
        lines.append(f"%% FUZZ_VERIFY_KIND: {pattern.verify_kind}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        lines.append(f"%% FUZZ_VERIFY_METHOD: {m_verify}")
        if pattern.pre_drive_seq:
            lines.append(f"%% FUZZ_PRE_DRIVE_SEQ: {','.join(method_name(lang, m) for m in pattern.pre_drive_seq)}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    for m in sorted(interface_methods):
        if m == m_verify:
            ret_type = "int" if pattern.verify_kind == "int" else "str"
            lines.append(f"        {m}(): {ret_type}")
        else:
            lines.append(f"        {m}()")
    lines.append("")
    lines.append("    machine:")
    lines.extend(state_lines)
    lines.append("")
    lines.append("    domain:")
    lines.append(domain_line)
    lines.append("}")
    lines.append("")

    seq_calls = [method_name(lang, m) for m in pattern.pre_drive_seq]
    is_int = pattern.verify_kind == "int"
    expected_str = expected if is_int else f'"{expected}"'

    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"_ret = _inst.{m_verify}()")
        lines.append(f"_expected = {expected_str}")
        lines.append("if _ret != _expected:")
        lines.append("    _fail('expected ret=' + repr(_expected) + ', got ' + repr(_ret))")
        lines.append(spec.println_pass.replace("nested-frame", "const-sys"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret = _inst.{m_verify}();")
        lines.append(f"const _expected = {expected_str};")
        lines.append(f"if (_ret !== _expected) {{ _fail(\"expected=\" + _expected + \", got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "const-sys"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        ret_decl = "number" if is_int else "string"
        lines.append(f"const _ret: {ret_decl} = _inst.{m_verify}();")
        lines.append(f"const _expected: {ret_decl} = {expected_str};")
        lines.append(f"if (_ret !== _expected) {{ _fail(\"expected=\" + _expected + \", got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "const-sys"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        for c in seq_calls:
            lines.append(f"_inst.{c}")
        lines.append(f"_ret = _inst.{m_verify}")
        lines.append(f"_expected = {expected_str}")
        lines.append("_fail(\"expected=#{_expected}, got #{_ret}\") unless _ret == _expected")
        lines.append(spec.println_pass.replace("nested-frame", "const-sys"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        for c in seq_calls:
            lines.append(f"_inst:{c}()")
        lines.append(f"local _ret = _inst:{m_verify}()")
        lines.append(f"local _expected = {expected_str}")
        lines.append("if _ret ~= _expected then _fail(\"expected=\" .. tostring(_expected) .. \", got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "const-sys"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"$_inst->{c}();")
        lines.append(f"$_ret = $_inst->{m_verify}();")
        lines.append(f"$_expected = {expected_str};")
        lines.append("if ($_ret !== $_expected) { _fail(\"expected=\" . $_expected . \", got \" . $_ret); }")
        lines.append(spec.println_pass.replace("nested-frame", "const-sys"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    final _ret = _inst.{m_verify}();")
        lines.append(f"    final _expected = {expected_str};")
        lines.append("    if (_ret != _expected) { _fail(\"expected=$_expected, got $_ret\"); }")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        if is_int:
            lines.append(f"    let _ret = _inst.{m_verify}();")
            lines.append(f"    let _expected = {expected_str};")
            lines.append("    if _ret != _expected { _fail(&format!(\"expected={}, got {}\", _expected, _ret)); }")
        else:
            lines.append(f"    let _ret: String = _inst.{m_verify}();")
            lines.append(f"    let _expected = {expected_str}.to_string();")
            lines.append("    if _ret != _expected { _fail(&format!(\"expected={:?}, got {:?}\", _expected, _ret)); }")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("}")
    elif lang == "go":
        lines.insert(2, "package main")
        lines.insert(3, "")
        lines.insert(4, 'import "fmt"')
        lines.insert(5, 'import "os"')
        lines.insert(6, "")
        lines.append(spec.fail_exit_def)
        lines.append("func main() {")
        lines.append(f"    sm := New{sys_name}()")
        for c in seq_calls:
            method_pasc = c[:1].upper() + c[1:]
            lines.append(f"    sm.{method_pasc}()")
        verify_pasc = m_verify[:1].upper() + m_verify[1:]
        lines.append(f"    ret := sm.{verify_pasc}()")
        lines.append(f"    expected := {expected_str}")
        lines.append("    if ret != expected { _fail(fmt.Sprintf(\"expected=%v, got %v\", expected, ret)) }")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"let _ret = _inst.{m_verify}()")
        lines.append(f"let _expected = {expected_str}")
        lines.append("if _ret != _expected { _fail(\"expected=\\(_expected), got \\(_ret)\") }")
        lines.append(spec.println_pass.replace("nested-frame", "const-sys"))
    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"        _inst.{c}();")
        if is_int:
            lines.append(f"        int _ret = (int) _inst.{m_verify}();")
            lines.append(f"        int _expected = {expected_str};")
            lines.append("        if (_ret != _expected) {")
        else:
            lines.append(f"        String _ret = (String) _inst.{m_verify}();")
            lines.append(f"        String _expected = {expected_str};")
            lines.append("        if (!_ret.equals(_expected)) {")
        lines.append("            System.out.println(\"FAIL: expected=\" + _expected + \", got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{cid}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"    _inst.{c}()")
        if is_int:
            lines.append(f"    val _ret = _inst.{m_verify}() as Int")
            lines.append(f"    val _expected: Int = {expected_str}")
        else:
            lines.append(f"    val _ret = _inst.{m_verify}() as String")
            lines.append(f"    val _expected: String = {expected_str}")
        lines.append("    if (_ret != _expected) { _fail(\"expected=$_expected, got $_ret\") }")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"            _inst.{c}();")
        if is_int:
            lines.append(f"            int _ret = (int) _inst.{m_verify}();")
            lines.append(f"            int _expected = {expected_str};")
        else:
            lines.append(f"            string _ret = (string) _inst.{m_verify}();")
            lines.append(f"            string _expected = {expected_str};")
        lines.append("            if (_ret != _expected) {")
        lines.append("                throw new System.Exception(\"FAIL: expected=\" + _expected + \", got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("#include <string.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        for c in seq_calls:
            lines.append(f"    {sys_name}_{c}(_inst);")
        if is_int:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_verify}(_inst);")
            lines.append(f"    int _expected = {expected_str};")
            lines.append("    if (_ret != _expected) {")
            lines.append("        printf(\"FAIL: expected=%d, got %d\\n\", _expected, _ret);")
        else:
            lines.append(f"    char* _ret = (char*){sys_name}_{m_verify}(_inst);")
            lines.append(f"    const char* _expected = {expected_str};")
            lines.append("    if (strcmp(_ret, _expected) != 0) {")
            lines.append("        printf(\"FAIL: expected=%s, got %s\\n\", _expected, _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("#include <string>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        if is_int:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_verify}());")
            lines.append(f"    int _expected = {expected_str};")
        else:
            lines.append(f"    std::string _ret = std::any_cast<std::string>(_inst.{m_verify}());")
            lines.append(f"    std::string _expected = {expected_str};")
        lines.append("    if (_ret != _expected) {")
        lines.append("        std::cerr << \"FAIL: expected=\" << _expected << \", got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        for c in seq_calls:
            lines.append(f"    _inst.{c}()")
        lines.append(f"    var _ret = _inst.{m_verify}()")
        lines.append(f"    var _expected = {expected_str}")
        lines.append("    if _ret != _expected:")
        lines.append("        _fail(\"expected=\" + str(_expected) + \", got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'const-sys')}")
        lines.append("    quit()")
    elif lang == "erlang":
        pass

    return "\n".join(lines) + "\n"


def main():
    out_dir = Path(__file__).parent / "cases_const_sys"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_lines = ["lang\tcase_id\tequiv_class\tsmoke\texpected\n"]

    cases_per_lang = {lang: 0 for lang in LANGS}
    smoke_per_lang = {lang: 0 for lang in LANGS}

    for cid, equiv, expected, pattern, lit, is_smoke in enumerate_cases():
        for lang in LANGS:
            spec = LANGS[lang]
            ext = spec.ext
            text = gen_case(lang, cid, equiv, expected, pattern, lit, is_smoke)
            (out_dir / f"{cid}.{ext}").write_text(text)
            cases_per_lang[lang] += 1
            if is_smoke:
                smoke_per_lang[lang] += 1
            index_lines.append(
                f"{lang}\t{cid}\t{equiv}\t{'yes' if is_smoke else 'no'}\t{expected}\n"
            )

    (out_dir / "_index.tsv").write_text("".join(index_lines))
    print(f"Generated cases in {out_dir}/")
    for lang in LANGS:
        print(f"  {lang}: {cases_per_lang[lang]} cases, {smoke_per_lang[lang]} smoke")


if __name__ == "__main__":
    main()
