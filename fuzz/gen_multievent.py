#!/usr/bin/env python3
"""
Phase 17 — multi-event traces fuzz (Wave 1).

Tests state-machine behavior across event sequences. Most other
phases test ONE event invocation in isolation. Multi-event surfaces
ordering bugs, state-mutation cascades, and inter-event timing issues
that single-event tests can't see.

Wave 1 design:
  Patterns (4): per-pattern event sequence shape.
  Value tuples (10): (LIT_A, LIT_B) per case.
  Total: 4 × 10 = 40 cases per lang × 17 langs = 680.

Smoke filter: one case per pattern (first value tuple) → 4 smoke
cases per lang.

Usage:
    python3 gen_multievent.py
    ./run_multievent.sh --tier=smoke
"""
from pathlib import Path

from gen_nested import LANGS, method_name


class Pattern:
    __slots__ = ("name", "build_states", "compute", "pre_drive_seq")

    def __init__(self, name, build_states, compute, pre_drive_seq):
        self.name = name
        self.build_states = build_states
        self.compute = compute
        self.pre_drive_seq = pre_drive_seq


def _build_p1_three_event_same_state(spec, lang, lit_a, lit_b):
    """P1: three events fired in sequence on the same state, each
    bumping $.f by a different literal. Verify $.f reflects all
    three bumps. Tests state-mutation accumulation across event
    invocations within a single state."""
    m_a = method_name(lang, "bump_a")
    m_b = method_name(lang, "bump_b")
    m_c = method_name(lang, "bump_c")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_a}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {m_b}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_b}{spec.stmt_end}",
        f"            }}",
        f"            {m_c}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p2_event_then_transition(spec, lang, lit_a, lit_b):
    """P2: 2-event sequence with a transition between. Event A in
    $S0 transitions to $S1; event B in $S1 bumps $.f. Tests that
    state-machine identity (current state) is preserved across
    event boundaries — the second event must dispatch to $S1's
    handler, not $S0's."""
    m_drive = method_name(lang, "drive")
    m_bump = method_name(lang, "bump_in_s1")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1",
        f"            }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p3_chain_three_states(spec, lang, lit_a, lit_b):
    """P3: 4-event sequence chaining transitions across three
    states. drive_a → $S1; bump_a in $S1 (bumps $.f += LIT_A);
    drive_b → $S2; bump_b in $S2 (bumps $.f += LIT_B); get_f
    reads from $S2. Final $.f = BASE + LIT_A + LIT_B."""
    m_drive_a = method_name(lang, "drive_a")
    m_drive_b = method_name(lang, "drive_b")
    m_bump_a = method_name(lang, "bump_a")
    m_bump_b = method_name(lang, "bump_b")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive_a}() {{",
        f"                -> $S1",
        f"            }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_bump_a}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {m_drive_b}() {{",
        f"                -> $S2",
        f"            }}",
        f"        }}",
        f"        $S2 {{",
        f"            {m_bump_b}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_b}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p5_five_event_same_state(spec, lang, lit_a, lit_b):
    """P5 (wave-3): five events fired against the same state.
    bump_a/b/c/d/e each add a literal to $.f. Verifies no per-event
    handler-state corruption across longer chains than wave-1's
    3-event P1."""
    methods = ["bump_a", "bump_b", "bump_c", "bump_d", "bump_e"]
    m_get = method_name(lang, "get_f")
    lines = [f"        $S0 {{"]
    # Lits cycle through (lit_a, lit_b, lit_a, lit_b, lit_a) so the
    # final $.f = 3*lit_a + 2*lit_b.
    lit_seq = [lit_a, lit_b, lit_a, lit_b, lit_a]
    for m, lit in zip(methods, lit_seq):
        mn = method_name(lang, m)
        lines.append(f"            {mn}() {{")
        lines.append(
            f"                {spec.self_word}{spec.field_op}f = "
            f"{spec.self_word}{spec.field_op}f + {lit}{spec.stmt_end}"
        )
        lines.append(f"            }}")
    lines.append(f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}")
    lines.append(f"        }}")
    return lines


def _build_p6_five_state_chain(spec, lang, lit_a, lit_b):
    """P6 (wave-3): five-state linear transition chain. drive_to_n
    transitions $S(n-1) → $S(n); each $Si has its own bump_n that
    adds lit_a to $.f. Sequence: drive_to_1, bump_1, drive_to_2,
    bump_2, drive_to_3, bump_3, drive_to_4, bump_4. Final $.f =
    4*lit_a. lit_b unused — but keeping signature uniform."""
    m_get = method_name(lang, "get_f")
    lines = []
    # $S0 declares all "drive" methods because Frame's interface
    # has to be uniform across states; same shape as wave-1 patterns.
    # Each $Si has its own bump_i (only) — the verifier picks the
    # last state's get_f.
    for i in range(5):
        lines.append(f"        $S{i} {{")
        if i < 4:
            mn_drive = method_name(lang, f"drive_to_{i+1}")
            lines.append(f"            {mn_drive}() {{")
            lines.append(f"                -> $S{i+1}")
            lines.append(f"            }}")
        if i >= 1:
            mn_bump = method_name(lang, f"bump_{i}")
            lines.append(f"            {mn_bump}() {{")
            lines.append(
                f"                {spec.self_word}{spec.field_op}f = "
                f"{spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}"
            )
            lines.append(f"            }}")
        if i == 4:
            lines.append(f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}")
        lines.append(f"        }}")
    return lines


def _build_p7_alternating_transition_bump(spec, lang, lit_a, lit_b):
    """P7 (wave-3): six events alternating transition + bump across
    three states. drive_a → $S1, bump_a (lit_a), drive_b → $S2, bump_b
    (lit_b), drive_c → $S3, bump_c (lit_a). Final $.f = 2*lit_a + lit_b.
    Tests interleaving of state-mutation events with transition events
    over a 6-event sequence."""
    m_get = method_name(lang, "get_f")
    states = []
    states.append([
        f"        $S0 {{",
        f"            {method_name(lang, 'drive_a')}() {{",
        f"                -> $S1",
        f"            }}",
        f"        }}",
    ])
    states.append([
        f"        $S1 {{",
        f"            {method_name(lang, 'bump_a')}() {{",
        f"                {spec.self_word}{spec.field_op}f = "
        f"{spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {method_name(lang, 'drive_b')}() {{",
        f"                -> $S2",
        f"            }}",
        f"        }}",
    ])
    states.append([
        f"        $S2 {{",
        f"            {method_name(lang, 'bump_b')}() {{",
        f"                {spec.self_word}{spec.field_op}f = "
        f"{spec.self_word}{spec.field_op}f + {lit_b}{spec.stmt_end}",
        f"            }}",
        f"            {method_name(lang, 'drive_c')}() {{",
        f"                -> $S3",
        f"            }}",
        f"        }}",
    ])
    states.append([
        f"        $S3 {{",
        f"            {method_name(lang, 'bump_c')}() {{",
        f"                {spec.self_word}{spec.field_op}f = "
        f"{spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ])
    out = []
    for st in states:
        out.extend(st)
    return out


def _build_p8_ten_same_event(spec, lang, lit_a, lit_b):
    """P8 (wave-3): ten consecutive invocations of the same event in
    one state. bump_a fires ten times, each adding lit_a. Final $.f
    = 10*lit_a. Verifies handler reentry has no per-call state
    leak (e.g., that the handler's local context-stack frame is
    properly popped after each invocation). lit_b unused."""
    mn = method_name(lang, "bump_a")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {mn}() {{",
        f"                {spec.self_word}{spec.field_op}f = "
        f"{spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p4_event_in_hsm_chain(spec, lang, lit_a, lit_b):
    """P4: events fired in HSM hierarchy across a transition.
    drive_to_child transitions $S0 → $Child (HSM child of $Parent).
    bump_child fires bump on $Child (handled by $Child); fwd_bump
    fires bump that $Child forwards to $Parent (=> $^), where
    $Parent handles it. Verify $.f reflects both handlers' work.

    NOTE: Phase 14 covers HSM forwards in single-event tests; this
    phase tests the SEQUENCE of events with mixed direct/forwarded
    handling."""
    m_drive = method_name(lang, "drive")
    m_bump_a = method_name(lang, "bump_a")
    m_fwd_bump = method_name(lang, "fwd_bump")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $Child",
        f"            }}",
        f"        }}",
        f"        $Child => $Parent {{",
        f"            {m_bump_a}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_a}{spec.stmt_end}",
        f"            }}",
        f"            {m_fwd_bump}() {{",
        f"                => $^",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_fwd_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + {lit_b}{spec.stmt_end}",
        f"            }}",
        f"        }}",
    ]


PATTERNS = [
    Pattern("p1_three_event_same_state",
            _build_p1_three_event_same_state,
            lambda a, b: a + b + a,  # bump_a + bump_b + bump_c (uses lit_a)
            ["bump_a", "bump_b", "bump_c"]),
    Pattern("p2_event_then_transition",
            _build_p2_event_then_transition,
            lambda a, b: a,
            ["drive", "bump_in_s1"]),
    Pattern("p3_chain_three_states",
            _build_p3_chain_three_states,
            lambda a, b: a + b,
            ["drive_a", "bump_a", "drive_b", "bump_b"]),
    Pattern("p4_event_in_hsm_chain",
            _build_p4_event_in_hsm_chain,
            lambda a, b: a + b,
            ["drive", "bump_a", "fwd_bump"]),
    Pattern("p5_five_event_same_state",
            _build_p5_five_event_same_state,
            lambda a, b: 3 * a + 2 * b,  # lit cycle: a,b,a,b,a
            ["bump_a", "bump_b", "bump_c", "bump_d", "bump_e"]),
    Pattern("p6_five_state_chain",
            _build_p6_five_state_chain,
            lambda a, b: 4 * a,  # bump_1..bump_4 each adds lit_a
            ["drive_to_1", "bump_1", "drive_to_2", "bump_2",
             "drive_to_3", "bump_3", "drive_to_4", "bump_4"]),
    Pattern("p7_alternating_transition_bump",
            _build_p7_alternating_transition_bump,
            lambda a, b: 2 * a + b,
            ["drive_a", "bump_a", "drive_b", "bump_b", "drive_c", "bump_c"]),
    Pattern("p8_ten_same_event",
            _build_p8_ten_same_event,
            lambda a, b: 10 * a,
            ["bump_a"] * 10),
]


VALUE_TUPLES = [
    (1, 2), (5, 7), (-3, 4), (10, -1),
    (0, 100), (50, 50), (-7, -3), (1, 0),
    (99, 1), (-1, 1),
]


def case_id(pattern, vt_idx):
    return f"me_{pattern.name}__t{vt_idx}"


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
            lit_a, lit_b = vt
            # Domain seed is 0; expected = compute output. We
            # initialize $.f = 0 in the domain block so the bumps
            # accumulate from a known baseline.
            expected = pattern.compute(lit_a, lit_b)
            yield (cid, cls, expected, pattern, vt, is_smoke)


def gen_case(lang, cid, equiv, expected, pattern, vt, is_smoke):
    spec = LANGS[lang]
    sys_name = f"MultiEvent_{cid}"
    lit_a, lit_b = vt

    m_get_f = method_name(lang, "get_f")
    verify = m_get_f

    state_lines = pattern.build_states(spec, lang, lit_a, lit_b)

    # Interface: the union of all methods named in pre_drive_seq
    # plus get_f. Sorted for deterministic emission.
    interface_methods = set()
    for m in pattern.pre_drive_seq:
        interface_methods.add(method_name(lang, m))
    interface_methods.add(verify)

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
    lines.append(f"        f: int = 0")
    lines.append("}")
    lines.append("")

    seq_calls = [method_name(lang, m) for m in pattern.pre_drive_seq]

    # Driver — same structure as gen_pushpop.py.
    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"_ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "multievent"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "multievent"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"_inst.{c}();")
        lines.append(f"const _ret: number = _inst.{verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "multievent"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        for c in seq_calls:
            lines.append(f"_inst.{c}")
        lines.append(f"_ret = _inst.{verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "multievent"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        for c in seq_calls:
            lines.append(f"_inst:{c}()")
        lines.append(f"local _ret = _inst:{verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "multievent"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        for c in seq_calls:
            lines.append(f"$_inst->{c}();")
        lines.append(f"$_ret = $_inst->{verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "multievent"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    final _ret = _inst.{verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'multievent')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        for c in seq_calls:
            lines.append(f"    _inst.{c}();")
        lines.append(f"    let _ret = _inst.{verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'multievent')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'multievent')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        for c in seq_calls:
            lines.append(f"_inst.{c}()")
        lines.append(f"let _ret = _inst.{verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "multievent"))
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
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'multievent')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'multievent')}")
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
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'multievent')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'multievent')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'multievent')}")
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
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'multievent')}")
        lines.append("    quit()")
    elif lang == "erlang":
        pass

    return "\n".join(lines) + "\n"


def main():
    out_dir = Path(__file__).parent / "cases_multievent"
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
