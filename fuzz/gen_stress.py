#!/usr/bin/env python3
"""
Phase 18 — stress / boundary fuzz (Wave 1).

Verifies framec-generated state machines endure many event
dispatches / transitions / push-pop cycles without crashing,
leaking memory, or breaking stack discipline. Frame's dispatch
loop should be O(1) per event; this exercises the loop at
modest N to catch obvious regressions.

This phase tests RUNTIME endurance. Most other phases verify
single-event correctness. Phase 18 doesn't test new framec
codegen paths — it stresses the existing ones.

Wave 1 design:
  Patterns (3): per-pattern stress shape.
  Stress levels: smoke N=10 (sanity), full N=100 (actual stress).
  Total: 3 × 1 (smoke) + 3 × 1 (full extra) = ~6 cases per lang × 17.

Usage:
    python3 gen_stress.py
    ./run_stress.sh --tier=smoke    # N=10
    ./run_stress.sh --tier=full     # N=100
"""
from pathlib import Path

from gen_nested import LANGS, method_name


# Stress level per tier. Capped to keep test wall-clock < 5s/backend.
STRESS_LEVELS = {"smoke": 10, "full": 100}


class Pattern:
    __slots__ = ("name", "build_states", "compute", "build_seq")

    def __init__(self, name, build_states, compute, build_seq):
        self.name = name
        self.build_states = build_states
        self.compute = compute  # lambda(N) -> int
        self.build_seq = build_seq  # lambda(lang, N) -> list[str]


def _build_p1_many_dispatches(spec, lang):
    """P1: $S0.bump() bumps domain.f by 1. Driver calls bump() N
    times. Tests event-dispatch loop endurance — no transitions,
    just repeated handler invocation."""
    m_bump = method_name(lang, "bump")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p2_transition_pingpong(spec, lang):
    """P2: alternating transitions $S0 ↔ $S1, each bumping domain.
    Driver calls drive() N times. Tests transition-loop endurance —
    enter/exit cascades fire each call, exercising the kernel
    transition pipeline."""
    m_drive = method_name(lang, "drive")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                -> $S1",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                -> $S0",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p3_push_pop_depth(spec, lang):
    """P3: deep push/pop stack. Driver pushes N times then pops N
    times. Tests modal-stack endurance and that the stack discipline
    holds at depth (no integer overflow on indices, no allocation
    bug on grow). Domain bumped each push."""
    m_push = method_name(lang, "push_then")
    m_pop = method_name(lang, "go_back")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_push}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                push$",
        f"                -> $S1",
        f"            }}",
        f"            {m_pop}() {{",
        f"                -> pop$",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_push}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                push$",
        f"                -> $S0",
        f"            }}",
        f"            {m_pop}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
    ]


PATTERNS = [
    Pattern("p1_many_dispatches",
            _build_p1_many_dispatches,
            lambda n: n,
            lambda lang, n: [method_name(lang, "bump")] * n),
    Pattern("p2_transition_pingpong",
            _build_p2_transition_pingpong,
            lambda n: n,
            lambda lang, n: [method_name(lang, "drive")] * n),
    Pattern("p3_push_pop_depth",
            _build_p3_push_pop_depth,
            lambda n: n,  # f bumped on each push only
            lambda lang, n: [method_name(lang, "push_then")] * n + [method_name(lang, "go_back")] * n),
]


def case_id(pattern, tier):
    return f"st_{pattern.name}__{tier}"


def equiv_class(pattern):
    return pattern.name


def enumerate_cases():
    """For each pattern, emit one smoke case and one full case
    (same shape, different stress level)."""
    for pattern in PATTERNS:
        for tier_name, n in STRESS_LEVELS.items():
            cid = case_id(pattern, tier_name)
            cls = equiv_class(pattern)
            is_smoke = (tier_name == "smoke")
            expected = pattern.compute(n)
            yield (cid, cls, expected, pattern, n, is_smoke)


def gen_case(lang, cid, equiv, expected, pattern, n, is_smoke):
    spec = LANGS[lang]
    sys_name = f"Stress_{cid}"

    m_get_f = method_name(lang, "get_f")
    verify = m_get_f

    state_lines = pattern.build_states(spec, lang)
    seq_calls = pattern.build_seq(lang, n)

    # Interface methods are the union of all invoked methods.
    interface_methods = set(seq_calls)
    interface_methods.add(verify)

    lines = []
    lines.append(f"@@target {spec.target}")
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        lines.append(f"%% FUZZ_VERIFY_METHOD: {verify}")
        if seq_calls:
            lines.append(f"%% FUZZ_PRE_DRIVE_SEQ: {','.join(seq_calls)}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    for m in sorted(interface_methods):
        if m == verify:
            lines.append(f"        {m}(): int")
        else:
            lines.append(f"        {m}()")
    lines.append("")
    lines.append("    machine:")
    lines.extend(state_lines)
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = 0")
    lines.append("}")
    lines.append("")

    # Per-language drivers: emit a tight loop or unrolled call list.
    # For modest N (≤100), unroll. Avoids generator-side complexity
    # of language-specific loop syntax. Generated source is verbose
    # at N=100 (~100 lines per case) but compiles cleanly.

    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"_ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "stress"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "stress"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret: number = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "stress"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        for c in seq_calls:
            lines.append(f"_inst.{c}")
        lines.append(f"_ret = _inst.{verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "stress"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        for c in seq_calls:
            lines.append(f"_inst:{c}()")
        lines.append(f"local _ret = _inst:{verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "stress"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"$_inst->{c}();")
        lines.append(f"$_ret = $_inst->{verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "stress"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    final _ret = _inst.{verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stress')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    let _ret = _inst.{verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stress')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stress')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"let _ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "stress"))
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
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'stress')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stress')}")
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
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'stress')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stress')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stress')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stress')}")
        lines.append("    quit()")
    elif lang == "erlang":
        pass

    return "\n".join(lines) + "\n"


def main():
    out_dir = Path(__file__).parent / "cases_stress"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_lines = ["lang\tcase_id\tequiv_class\tsmoke\texpected\n"]

    cases_per_lang = {lang: 0 for lang in LANGS}
    smoke_per_lang = {lang: 0 for lang in LANGS}

    for cid, equiv, expected, pattern, n, is_smoke in enumerate_cases():
        for lang in LANGS:
            spec = LANGS[lang]
            ext = spec.ext
            text = gen_case(lang, cid, equiv, expected, pattern, n, is_smoke)
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
