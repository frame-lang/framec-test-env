#!/usr/bin/env python3
"""
Phase 19 — push/pop modal stack fuzz (Wave 1).

Frame's `push$` and `-> pop$` save/restore the current compartment
on a per-system stack. The semantics:

  push$               saves current compartment to system._state_stack
  -> $S2              transitions to $S2 (after the save)
  -> pop$             restores the saved compartment (and exits $S2)

Compartment includes state_vars, so a pushed state's $.x = 5 is
restored on pop — but state_vars set in the PUSHED state (after
the push) are NOT visible after pop (those belong to a different
compartment).

Domain fields are global — modifications from any state are visible
everywhere. This phase tests the correct push/pop layering across
state-vars vs domain.

Wave 1 design:
  Patterns (4): per-pattern push/pop shape.
  Value tuples (10): (BASE, BUMP) per case.
  Total: 4 × 10 = 40 cases per lang × 17 langs = 680.

Smoke filter: one case per pattern (first value tuple) → 4 smoke
cases per lang.

Usage:
    python3 gen_pushpop.py
    ./run_pushpop.sh --tier=smoke
"""
from pathlib import Path

from gen_nested import LANGS, method_name


# ---------------------------------------------------------------------
# Pattern builders. Each pattern is a list of state declaration
# blocks (Frame source lines, properly indented). $S0 is the start
# state.
# ---------------------------------------------------------------------

class Pattern:
    __slots__ = ("name", "build_states", "compute", "pre_drive_seq")

    def __init__(self, name, build_states, compute, pre_drive_seq):
        self.name = name
        self.build_states = build_states          # lambda(spec, lang, base, bump) -> [str]
        self.compute = compute                    # lambda(base, bump) -> int
        self.pre_drive_seq = pre_drive_seq        # list of method names to call before verify


def _build_p1_dom_persists(spec, lang, base, bump):
    """P1: domain field $.f = BASE (initialized via domain default).
    drive() in $S0 pushes and transitions to $S1. $S1.bump_f bumps
    $.f by BUMP. $S1.go_back pops to $S0 (where get_f lives). Verify
    $.f == BASE+BUMP — domain is global; pop re-fires $> (Frame
    design) but $S0 has no enter handler, so domain values stick."""
    m_drive = method_name(lang, "drive")
    m_bump = method_name(lang, "bump_f")
    m_back = method_name(lang, "go_back")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                push$",
        f"                -> $S1",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {bump}{spec.stmt_end}",
        f"            }}",
        f"            {m_back}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
    ]


def _build_p2_sv_restored(spec, lang, base, bump):
    """P2: $S0 has $.x = BASE. drive() pushes from $S0 → $S1.
    $S1's set_x writes $.x = BUMP (in $S1's separate compartment,
    invisible to $S0). go_back pops to $S0. Verify $S0's $.x
    reads back BASE (saved compartment restored, $S1's writes
    discarded)."""
    m_drive = method_name(lang, "drive")
    m_back = method_name(lang, "go_back")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            $.x: int = {base}",
        f"            {m_drive}() {{",
        f"                push$",
        f"                -> $S1",
        f"            }}",
        f"            {m_get_x}(): int {{ @@:($.x) }}",
        f"        }}",
        f"        $S1 {{",
        f"            $.x: int = {bump}",
        f"            {m_back}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
    ]


def _build_p3_depth_two(spec, lang, base, bump):
    """P3: depth-2 push. $S0 push → $S1 push → $S2. $S2.bump_f
    bumps $.f by BUMP. Two pops to get back to $S0, verify $.f.
    Domain initialized to BASE (no $> handlers — those would re-
    fire on pop and break the test). Final $.f = BASE + BUMP."""
    m_drive = method_name(lang, "drive")
    m_to_s2 = method_name(lang, "to_s2")
    m_bump = method_name(lang, "bump_f")
    m_pop1 = method_name(lang, "pop1")
    m_pop2 = method_name(lang, "pop2")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                push$",
        f"                -> $S1",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_to_s2}() {{",
        f"                push$",
        f"                -> $S2",
        f"            }}",
        f"            {m_pop2}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
        f"        $S2 {{",
        f"            {m_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {bump}{spec.stmt_end}",
        f"            }}",
        f"            {m_pop1}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
    ]


def _build_p5_push_from_hsm_child(spec, lang, base, bump):
    """P5: HSM child pushed, then popped back. $S0 push → $Child
    (which has $Parent as HSM ancestor). $Child.bump_f bumps $.f
    by BUMP. $Child.back pops back to $S0. The push saves $Child's
    compartment (with parent_compartment pointing at $Parent's
    chain layer); pop must restore the whole chain. Verify $.f
    from $S0: should be BASE + BUMP. Tests that push/pop preserves
    HSM compartment topology."""
    m_drive = method_name(lang, "drive")
    m_bump = method_name(lang, "bump_f")
    m_back = method_name(lang, "go_back")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                push$",
        f"                -> $Child",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $Child => $Parent {{",
        f"            {m_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {bump}{spec.stmt_end}",
        f"            }}",
        f"            {m_back}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
        f"        $Parent {{}}",
    ]


def _build_p6_push_into_hsm_chain(spec, lang, base, bump):
    """P6: push from HSM leaf; verify push/pop preserves the saved
    leaf's parent chain. $S0 transitions (no push) to $Child (which
    has $Parent as ancestor). $Child.go_push pushes the current
    compartment ($Child with chain → $Parent). $Child.bump_f bumps
    $.f. $Child.back pops back. Now $Child is restored — verify by
    calling $Child.bump_f again (proves Child's handlers still
    dispatch). Final $.f = BASE + BUMP + BUMP."""
    m_drive = method_name(lang, "drive")
    m_push = method_name(lang, "go_push")
    m_bump = method_name(lang, "bump_f")
    m_back = method_name(lang, "go_back")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $Child",
        f"            }}",
        f"        }}",
        f"        $Child => $Parent {{",
        f"            {m_push}() {{",
        f"                push$",
        f"                -> $Sibling",
        f"            }}",
        f"            {m_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {bump}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $Sibling {{",
        f"            {m_back}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
        f"        $Parent {{}}",
    ]


def _build_p4_pop_then_event(spec, lang, base, bump):
    """P4: After pop, the restored state's handlers respond to
    subsequent events with the saved state-var values. This tests
    that pop$ doesn't just visit the saved state but reactivates it
    as the current state.

    $S0 has $.x = base. drive() pushes from $S0 → $S1. $S1's
    handler set_x writes $.x = bump (in $S1's compartment). $S1's
    go_back pops to $S0. Then read_x in $S0 returns $S0's $.x
    which should still be base (the original value, unchanged by
    $S1's writes)."""
    m_drive = method_name(lang, "drive")
    m_back = method_name(lang, "go_back")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            $.x: int = {base}",
        f"            {m_drive}() {{",
        f"                push$",
        f"                -> $S1",
        f"            }}",
        f"            {m_get_x}(): int {{ @@:($.x) }}",
        f"        }}",
        f"        $S1 {{",
        f"            $.x: int = {bump}",
        f"            {m_back}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
    ]


# Pattern registry. Each pattern's `compute` returns the expected
# value of the verified getter after the pre_drive_seq is run.
PATTERNS = [
    Pattern("p1_dom_persists",
            _build_p1_dom_persists,
            lambda base, bump: base + bump,
            ["drive", "bump_f", "go_back"]),
    Pattern("p2_sv_restored",
            _build_p2_sv_restored,
            lambda base, bump: base,
            ["drive", "go_back"]),
    Pattern("p3_depth_two",
            _build_p3_depth_two,
            lambda base, bump: base + bump,
            ["drive", "to_s2", "bump_f", "pop1", "pop2"]),
    Pattern("p4_pop_then_event",
            _build_p4_pop_then_event,
            lambda base, bump: base,
            ["drive", "go_back"]),
    # Wave 2: HSM × push/pop cross-product. P5 push from HSM child
    # tests that push/pop preserves the HSM parent chain. P6 push
    # from leaf, transition to sibling, pop back, then bump_f again
    # — tests Child's handlers still dispatch after restoration.
    Pattern("p5_push_from_hsm_child",
            _build_p5_push_from_hsm_child,
            lambda base, bump: base + bump,
            ["drive", "bump_f", "go_back"]),
    Pattern("p6_push_into_hsm_chain",
            _build_p6_push_into_hsm_chain,
            lambda base, bump: base + bump + bump,
            ["drive", "bump_f", "go_push", "go_back", "bump_f"]),
]


VALUE_TUPLES = [
    (1, 2), (5, 7), (-3, 4), (10, -1),
    (0, 100), (50, 50), (-7, -3), (1, 0),
    (99, 1), (-1, 1),
]


def case_id(pattern, vt_idx):
    return f"pp_{pattern.name}__t{vt_idx}"


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
            base, bump = vt
            expected = pattern.compute(base, bump)
            yield (cid, cls, expected, pattern, vt, is_smoke)


def gen_case(lang, cid, equiv, expected, pattern, vt, is_smoke):
    spec = LANGS[lang]
    sys_name = f"PushPop_{cid}"
    base, bump = vt

    m_drive = method_name(lang, "drive")
    m_bump_f = method_name(lang, "bump_f")
    m_back = method_name(lang, "go_back")
    m_back1 = method_name(lang, "back1")
    m_get_f = method_name(lang, "get_f")
    m_get_x = method_name(lang, "get_x")

    # Verify method depends on pattern.
    if pattern.name in ("p1_dom_persists", "p3_depth_two",
                        "p5_push_from_hsm_child",
                        "p6_push_into_hsm_chain"):
        verify = m_get_f
    else:
        verify = m_get_x

    state_lines = pattern.build_states(spec, lang, base, bump)

    # Determine interface signatures based on pattern's pre-drive
    # sequence. We declare every method the pattern uses.
    interface_methods = set()
    for m in pattern.pre_drive_seq:
        interface_methods.add(method_name(lang, m))
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
        lines.append(f"%% FUZZ_PRE_DRIVE_SEQ: {','.join(method_name(lang, m) for m in pattern.pre_drive_seq)}")
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
    lines.append(f"        f: int = {base}")
    lines.append("}")
    lines.append("")

    # Test driver: call pre_drive_seq then verify. Per-language
    # idioms borrowed from gen_state_args.py to ensure each language
    # toolchain (Java's class-name rule, Kotlin's @file:JvmName,
    # GDScript's SceneTree extension, Go's package main + imports,
    # etc.) gets the right shape.
    seq_calls = [method_name(lang, m) for m in pattern.pre_drive_seq]

    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"_ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "pushpop"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "pushpop"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret: number = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "pushpop"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        for c in seq_calls:
            lines.append(f"_inst.{c}")
        lines.append(f"_ret = _inst.{verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "pushpop"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        for c in seq_calls:
            lines.append(f"_inst:{c}()")
        lines.append(f"local _ret = _inst:{verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "pushpop"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"$_inst->{c}();")
        lines.append(f"$_ret = $_inst->{verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "pushpop"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    final _ret = _inst.{verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'pushpop')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    let _ret = _inst.{verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'pushpop')}")
        lines.append("}")
    elif lang == "go":
        # Go: prepend package + imports BEFORE the @@target line.
        # gen_state_args's approach is to insert at indices 2/3/4/5
        # so the `package main` lands above the @@system block.
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'pushpop')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"let _ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "pushpop"))
    elif lang == "java":
        # Java: class Driver (not public) — javac requires a public
        # class to be in a file named after the class, but a non-
        # public top-level class can live in any file.
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
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'pushpop')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        # Kotlin: @file:JvmName forces the JVM class name to Driver,
        # and the package keeps each test isolated from the others.
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'pushpop')}")
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
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'pushpop')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'pushpop')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'pushpop')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        # GDScript: extends SceneTree + _init() entry. quit() at end
        # cleans up the scene tree so the test harness can detect the
        # exit code (no Cannot find member "exit_code" because we
        # use SceneTree's quit() and don't touch OS.exit_code).
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'pushpop')}")
        lines.append("    quit()")
    elif lang == "erlang":
        # Erlang runner uses FUZZ_PRE_DRIVE_SEQ metadata; no driver
        # in the source.
        pass

    return "\n".join(lines) + "\n"


def main():
    out_dir = Path(__file__).parent / "cases_pushpop"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Index for the runner: lang, case_id, equiv_class, smoke flag,
    # expected. Per-lang rows so the runner's smoke filter can scan
    # by language.
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
