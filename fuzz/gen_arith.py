#!/usr/bin/env python3
"""
Phase 21 — int arithmetic edge cases fuzz (Wave 1).

Frame has no type system: types are opaque strings passed through to
the target. For arithmetic, the target language's semantics apply
(integer division, modulo, signed/unsigned overflow, etc). This
phase tests the SUBSET of arithmetic that Frame guarantees portable
across backends: standard int + - * / and % on values that fit
within signed-32-bit range.

Wave 1 design:
  Patterns (4): per-pattern arithmetic shape.
  Value tuples (10): (a, b) input pairs covering edge cases.
  Total: 4 × 10 = 40 cases per lang × 17 langs = 680.

Smoke filter: one case per pattern (first value tuple) → 4 smoke
cases per lang.

Usage:
    python3 gen_arith.py
    ./run_arith.sh --tier=smoke
"""
from pathlib import Path

from gen_nested import LANGS, method_name


class Pattern:
    __slots__ = ("name", "build_states", "compute")

    def __init__(self, name, build_states, compute):
        self.name = name
        self.build_states = build_states
        self.compute = compute


def _build_p1_add_chain(spec, lang, a, b):
    """P1: chained addition. drive() sets $.f = a + b + a + b + a.
    Tests that Frame's expression passthrough handles 4-operator
    chains identically across backends."""
    m_drive = method_name(lang, "drive")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {a} + {b} + {a} + {b} + {a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p2_precedence(spec, lang, a, b):
    """P2: operator precedence — `a + b * a`. Tests that Frame
    pass-through respects the target's standard precedence rules
    (multiplication before addition). Result = a + (b * a)."""
    m_drive = method_name(lang, "drive")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {a} + {b} * {a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p3_subtraction(spec, lang, a, b):
    """P3: subtraction left-to-right associativity. Tests that
    `a - b - a` evaluates as `(a - b) - a`, not `a - (b - a)`."""
    m_drive = method_name(lang, "drive")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {a} - {b} - {a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p4_paren_grouping(spec, lang, a, b):
    """P4: explicit parenthesisation. `(a + b) * a` should evaluate
    paren-first regardless of target. Tests that Frame doesn't
    drop or rewrite parens during expression passthrough."""
    m_drive = method_name(lang, "drive")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = ({a} + {b}) * {a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


PATTERNS = [
    Pattern("p1_add_chain",
            _build_p1_add_chain,
            lambda a, b: a + b + a + b + a),
    Pattern("p2_precedence",
            _build_p2_precedence,
            lambda a, b: a + b * a),
    Pattern("p3_subtraction",
            _build_p3_subtraction,
            lambda a, b: a - b - a),
    Pattern("p4_paren_grouping",
            _build_p4_paren_grouping,
            lambda a, b: (a + b) * a),
]


# Value pairs covering: simple, negatives, zero, mixed signs.
# Sticking to values whose results fit in signed-32-bit so all
# backends agree (no platform-dependent overflow).
VALUE_TUPLES = [
    (3, 5), (10, -2), (0, 7), (-4, 6),
    (1, 1), (-3, -3), (100, 50), (-1, 1),
    (7, 0), (-7, 7),
]


def case_id(pattern, vt_idx):
    return f"ar_{pattern.name}__t{vt_idx}"


def equiv_class(pattern):
    return pattern.name


def enumerate_cases():
    seen = set()
    for pattern in PATTERNS:
        for idx, vt in enumerate(VALUE_TUPLES):
            cid = case_id(pattern, idx)
            cls = equiv_class(pattern)
            is_smoke = cls not in seen
            if is_smoke:
                seen.add(cls)
            a, b = vt
            expected = pattern.compute(a, b)
            yield (cid, cls, expected, pattern, vt, is_smoke)


def gen_case(lang, cid, equiv, expected, pattern, vt, is_smoke):
    spec = LANGS[lang]
    sys_name = f"Arith_{cid}"
    a, b = vt

    m_drive = method_name(lang, "drive")
    m_get_f = method_name(lang, "get_f")
    verify = m_get_f

    state_lines = pattern.build_states(spec, lang, a, b)

    lines = []
    lines.append(f'@@[target("{spec.target}")]')
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        lines.append(f"%% FUZZ_VERIFY_METHOD: {verify}")
        lines.append(f"%% FUZZ_PRE_DRIVE: {m_drive}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append(f"        {m_drive}()")
    lines.append(f"        {verify}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.extend(state_lines)
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = 0")
    lines.append("}")
    lines.append("")

    seq_calls = [m_drive]

    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"_ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "arith"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "arith"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret: number = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "arith"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        for c in seq_calls:
            lines.append(f"_inst.{c}")
        lines.append(f"_ret = _inst.{verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "arith"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        for c in seq_calls:
            lines.append(f"_inst:{c}()")
        lines.append(f"local _ret = _inst:{verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "arith"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"$_inst->{c}();")
        lines.append(f"$_ret = $_inst->{verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "arith"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    final _ret = _inst.{verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'arith')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    let _ret = _inst.{verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'arith')}")
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
        verify_pasc = verify[:1].upper() + verify[1:]
        lines.append(f"    ret := sm.{verify_pasc}()")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'arith')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"let _ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "arith"))
    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"        _inst.{c}();")
        lines.append(f"        int _ret = (int) _inst.{verify}();")
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'arith')}")
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
        lines.append(f"    val _ret = _inst.{verify}() as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'arith')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"            _inst.{c}();")
        lines.append(f"            int _ret = (int) _inst.{verify}();")
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'arith')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        for c in seq_calls:
            lines.append(f"    {sys_name}_{c}(_inst);")
        lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{verify}(_inst);")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'arith')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    int _ret = std::any_cast<int>(_inst.{verify}());")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'arith')}")
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
        lines.append(f"    var _ret = _inst.{verify}()")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'arith')}")
        lines.append("    quit()")
    elif lang == "erlang":
        pass

    return "\n".join(lines) + "\n"


def main():
    out_dir = Path(__file__).parent / "cases_arith"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_lines = ["lang\tcase_id\tequiv_class\tsmoke\texpected\n"]

    cases_per_lang = {lang: 0 for lang in LANGS}
    smoke_per_lang = {lang: 0 for lang in LANGS}

    for cid, equiv, expected, pattern, vt, is_smoke in enumerate_cases():
        for lang in LANGS:
            spec = LANGS[lang]
            ext = spec.ext
            text = gen_case(lang, cid, equiv, expected, pattern, vt, is_smoke)
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
