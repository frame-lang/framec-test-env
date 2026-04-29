#!/usr/bin/env python3
"""
Phase 15 — state-arg propagation × everything fuzz (Wave 1).

Frame state args are positional declarations on a state body:
    $S(x: int) { $>() { @@:return = x } }

Transitioning into the state binds the args by name in handlers:
    drive() { -> $S(42) }

Phase 4 covers HSM enter/exit cascades. Phase 14 covers HSM ×
expression / dispatch. This phase tests the orthogonal axis: do
state args flow correctly through transitions, multi-arg
declarations, HSM hierarchies, and event handlers (not just $>)?

Wave 1 design:
  Patterns (8): per-pattern transition + state-arg shape.
  Value tuples (10): (LIT, dom_init) per case.
  Total: 8 × 10 = 80 cases per lang × 17 langs = 1,360.

Smoke filter: one case per pattern (first value tuple) → 8 smoke
cases per lang.

Usage:
    python3 gen_state_args.py
    ./run_state_args.sh --tier=smoke
"""
import argparse
from pathlib import Path

from gen_nested import LANGS, method_name


COMPUTE_RETURN = 9


# ---------------------------------------------------------------------
# Pattern definitions. Each pattern is a list of state declaration
# blocks (Frame source lines, properly indented). The deepest leaf
# state — where the system initialises — comes FIRST.
# ---------------------------------------------------------------------

class Pattern:
    __slots__ = ("name", "build_states", "drive_returns",
                 "verify_method", "compute")

    def __init__(self, name, build_states, drive_returns,
                 verify_method, compute):
        self.name = name
        self.build_states = build_states  # lambda(spec, lang, lit) -> [str]
        self.drive_returns = drive_returns
        self.verify_method = verify_method
        self.compute = compute            # lambda(lit, dom_init) -> int


def _build_p1_lit_arg(spec, lang, lit):
    """P1: drive() (void) transitions to $S1 with a literal arg.
    Verify via get_x() in $S1 — state-arg `x` persists for the
    state's lifetime and is readable from any handler in that
    state. Tests basic state-arg binding."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1({lit})",
        f"            }}",
        f"        }}",
        f"        $S1(x: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x) }}",
        f"        }}",
    ]


def _build_p2_dom_arg(spec, lang, lit):
    """P2: drive() (void) writes self.f = LIT, transitions to $S1
    with self.f as the arg. Verify via get_x()."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {lit}{spec.stmt_end}",
        f"                -> $S1({spec.self_word}{spec.field_op}f)",
        f"            }}",
        f"        }}",
        f"        $S1(x: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x) }}",
        f"        }}",
    ]


def _build_p3_arith_arg(spec, lang, lit):
    """P3: drive() (void) transitions with arithmetic expression
    as the arg. Verify via get_x()."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1({lit} + 1)",
        f"            }}",
        f"        }}",
        f"        $S1(x: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x) }}",
        f"        }}",
    ]


def _build_p4_selfcall_arg(spec, lang, lit):
    """P4: drive() (void) transitions with @@:self.compute() as
    the arg. compute() returns COMPUTE_RETURN. Verify via get_x()."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    m_compute = method_name(lang, "compute")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1(@@:self.{m_compute}())",
        f"            }}",
        f"            {m_compute}(): int {{ @@:({COMPUTE_RETURN}) }}",
        f"        }}",
        f"        $S1(x: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x) }}",
        f"        }}",
    ]


def _build_p5_multi_arg(spec, lang, lit):
    """P5: $S1(x: int, y: int) — two state args. drive() (void)
    transitions with both literals. Verify via get_x() returns
    x + y."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1({lit}, {lit})",
        f"            }}",
        f"        }}",
        f"        $S1(x: int, y: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x + {spec.param_prefix}y) }}",
        f"        }}",
    ]


def _build_p6_pingpong(spec, lang, lit):
    """P6: drive() (void) → $S1(LIT). $S1.$>() transitions to
    $S2(x * 2). Verify via get_x() in $S2 returns y. Tests args
    propagating through multiple transitions."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1({lit})",
        f"            }}",
        f"        }}",
        f"        $S1(x: int) {{",
        f"            $>() {{",
        f"                -> $S2({spec.param_prefix}x * 2)",
        f"            }}",
        f"        }}",
        f"        $S2(y: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}y) }}",
        f"        }}",
    ]


def _build_p7_child_hsm_arg(spec, lang, lit):
    """P7: $Child => $Parent(x: int) — child state has args via
    parent-decl form. drive() (void) transitions to $Child(LIT).
    Verify via get_x() in $Child returns x.
    Note: state args go AFTER the parent declaration; the
    `$Child(x: int) => $Parent` form in HSM_TEST_PLAN.md is not
    supported by the current parser."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $Child({lit})",
        f"            }}",
        f"        }}",
        f"        $Child => $Parent(x: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x) }}",
        f"        }}",
        f"        $Parent {{}}",
    ]


def _build_p9_three_level_uniform(spec, lang, lit):
    """P9: 3-level HSM uniform — all three layers declare their own
    `(x: int)` so every StateContext variant is tuple-shaped.
    Frame's parser reads `(x: int)` AFTER a `=> $Parent` clause as
    the LEFT state's params; the root state declares its params
    inline. drive() transitions to $Leaf(LIT). Rust's tuple-variant
    ancestor walk writes at all three depths. Verify via get_x()
    in $Leaf."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $Leaf({lit})",
        f"            }}",
        f"        }}",
        f"        $Leaf => $Mid(x: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x) }}",
        f"        }}",
        f"        $Mid => $Root(x: int) {{",
        f"        }}",
        f"        $Root(x: int) {{",
        f"        }}",
    ]


def _build_p10_three_level_mixed(spec, lang, lit):
    """P10: 3-level HSM mixed-shape — Leaf has args, Mid is unit,
    Root has args. drive() → $Leaf(LIT). Tests the Rust ancestor
    walk's conditional skip path: walk past $Mid (unit variant —
    no `if let StateContext::Mid(...)` would compile, E0532) and
    write to $Root (tuple variant) at depth 2. Verify via get_x()
    in $Leaf."""
    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $Leaf({lit})",
        f"            }}",
        f"        }}",
        f"        $Leaf => $Mid(x: int) {{",
        f"            {m_get_x}(): int {{ @@:({spec.param_prefix}x) }}",
        f"        }}",
        f"        $Mid => $Root {{",
        f"        }}",
        f"        $Root(x: int) {{",
        f"        }}",
    ]


def _build_p8_arg_in_event(spec, lang, lit):
    """P8: $S1(x: int) declares the arg, but the read happens
    in a regular event handler (not $>). drive() in $S0 transitions
    to $S1(LIT). $S1's $>() does nothing. Then drive2() event reads
    x. Tests arg persistence — the arg is stored on the compartment
    and survives across event dispatches.

    Note: drive() declared `void` (not `: int`) — the typed-int
    return on a transition-only handler triggers Java/C# NPE on
    int unboxing per the documented Frame contract (return slot
    is null when no @@:return is written). drive() doesn't need a
    return value here; drive2() carries the test value."""
    m_drive = method_name(lang, "drive")
    m_drive2 = method_name(lang, "drive2")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                -> $S1({lit})",
        f"            }}",
        f"        }}",
        f"        $S1(x: int) {{",
        f"            {m_drive2}(): int {{",
        f"                @@:return = {spec.param_prefix}x{spec.stmt_end}",
        f"            }}",
        f"        }}",
    ]


PATTERNS = [
    # All patterns: drive() is void and transitions; verify via
    # get_x() in the destination state. This sidesteps Erlang's
    # gen_statem reply-before-enter model (frame_transition__'s
    # reply fires before the destination's $> handler runs, so
    # destination's @@:return can't propagate back to drive()).
    # By splitting drive (transition) from get_x (read state-arg),
    # we test the actual axis (state-args persist) without needing
    # synchronous return-value propagation through transitions.
    Pattern("p1_lit_arg", _build_p1_lit_arg, False, "get_x",
            lambda lit, di: lit),
    Pattern("p2_dom_arg", _build_p2_dom_arg, False, "get_x",
            lambda lit, di: lit),
    Pattern("p3_arith_arg", _build_p3_arith_arg, False, "get_x",
            lambda lit, di: lit + 1),
    Pattern("p4_selfcall_arg", _build_p4_selfcall_arg, False, "get_x",
            lambda lit, di: COMPUTE_RETURN),
    Pattern("p5_multi_arg", _build_p5_multi_arg, False, "get_x",
            lambda lit, di: lit + lit),
    Pattern("p6_pingpong", _build_p6_pingpong, False, "get_x",
            lambda lit, di: lit * 2),
    Pattern("p7_child_hsm_arg", _build_p7_child_hsm_arg, False, "get_x",
            lambda lit, di: lit),
    # P8 reads via drive2 in event-handler context (no transition
    # before read) — same get-after-drive shape but with a custom
    # second event name.
    Pattern("p8_arg_in_event", _build_p8_arg_in_event, False, "drive2",
            lambda lit, di: lit),
    # Wave 2: 3-level HSM cross-product. P9 uniform (all 3 layers
    # tuple variant), P10 mixed (leaf tuple, mid unit, root tuple).
    Pattern("p9_three_lvl_uniform", _build_p9_three_level_uniform,
            False, "get_x", lambda lit, di: lit),
    Pattern("p10_three_lvl_mixed", _build_p10_three_level_mixed,
            False, "get_x", lambda lit, di: lit),
]


VALUE_TUPLES = [
    (1, 0), (5, 0), (-3, 0), (0, 0),
    (100, 50), (7, 13), (-50, 100), (1, -1),
    (999, -777), (-1, 1),
]


def case_id(pattern, vt_idx):
    return f"sa_{pattern.name}__t{vt_idx}"


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
            lit, dom_init = vt
            expected = pattern.compute(lit, dom_init)
            yield (cid, cls, expected, pattern, vt, is_smoke)


def gen_case(lang, cid, equiv, expected, pattern, vt, is_smoke):
    spec = LANGS[lang]
    sys_name = f"StateArgs_{cid}"
    lit, dom_init = vt

    m_drive = method_name(lang, "drive")
    m_drive2 = method_name(lang, "drive2")
    m_compute = method_name(lang, "compute")
    m_get_x = method_name(lang, "get_x")

    # P8 verifies via drive2 (event handler in destination state).
    # Other patterns verify via get_x (interface method in
    # destination state). All patterns: drive() is void (just
    # transitions), so the typed-int return-NPE on Java/C# is
    # avoided.
    is_p8 = pattern.name == "p8_arg_in_event"
    needs_compute = pattern.name == "p4_selfcall_arg"

    drive_sig = f"{m_drive}()"
    drive2_sig = f"{m_drive2}(): int"

    state_lines = pattern.build_states(spec, lang, lit)

    lines = []
    lines.append(f"@@target {spec.target}")
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        verify = m_drive2 if is_p8 else m_get_x
        lines.append(f"%% FUZZ_VERIFY_METHOD: {verify}")
        lines.append(f"%% FUZZ_DRIVE_RETURNS: no")
        # All patterns: drive() first transitions, then verify
        # method reads the persisted state-arg. Pre-drive marker
        # tells the runner to call drive() before verify.
        lines.append(f"%% FUZZ_PRE_DRIVE: {m_drive}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append(f"        {drive_sig}")
    if is_p8:
        lines.append(f"        {drive2_sig}")
    else:
        lines.append(f"        {m_get_x}(): int")
    if needs_compute:
        lines.append(f"        {m_compute}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.extend(state_lines)
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = {dom_init}")
    lines.append("}")
    lines.append("")

    # Driver: for normal patterns, just `_inst.drive()`. For P8,
    # call drive() first (transitions), then drive2() (reads the
    # arg) — drive2's return is the test value.
    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        if is_p8:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"_ret = _inst.{m_drive2}()")
        else:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"_ret = _inst.{m_get_x}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "state-args"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if is_p8:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret = _inst.{m_drive2}();")
        else:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret = _inst.{m_get_x}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "state-args"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if is_p8:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret: number = _inst.{m_drive2}();")
        else:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret: number = _inst.{m_get_x}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "state-args"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        if is_p8:
            lines.append(f"_inst.{m_drive}")
            lines.append(f"_ret = _inst.{m_drive2}")
        else:
            lines.append(f"_inst.{m_drive}")
            lines.append(f"_ret = _inst.{m_get_x}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "state-args"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        if is_p8:
            lines.append(f"_inst:{m_drive}()")
            lines.append(f"local _ret = _inst:{m_drive2}()")
        else:
            lines.append(f"_inst:{m_drive}()")
            lines.append(f"local _ret = _inst:{m_get_x}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "state-args"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        if is_p8:
            lines.append(f"$_inst->{m_drive}();")
            lines.append(f"$_ret = $_inst->{m_drive2}();")
        else:
            lines.append(f"$_inst->{m_drive}();")
            lines.append(f"$_ret = $_inst->{m_get_x}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "state-args"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        if is_p8:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    final _ret = _inst.{m_drive2}();")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    final _ret = _inst.{m_get_x}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        if is_p8:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    let _ret = _inst.{m_drive2}();")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    let _ret = _inst.{m_get_x}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'state-args')}")
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
        if is_p8:
            lines.append(f"    sm.{m_drive}()")
            lines.append(f"    ret := sm.{m_drive2}()")
        else:
            lines.append(f"    sm.{m_drive}()")
            lines.append(f"    ret := sm.{m_get_x}()")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        if is_p8:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"let _ret = _inst.{m_drive2}()")
        else:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"let _ret = _inst.{m_get_x}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "state-args"))
    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = new {sys_name}();")
        if is_p8:
            lines.append(f"        _inst.{m_drive}();")
            lines.append(f"        int _ret = (int) _inst.{m_drive2}();")
        else:
            lines.append(f"        _inst.{m_drive}();")
            lines.append(f"        int _ret = (int) _inst.{m_get_x}();")
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{cid}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        if is_p8:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    val _ret = _inst.{m_drive2}() as Int")
        else:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    val _ret = _inst.{m_get_x}() as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        if is_p8:
            lines.append(f"            _inst.{m_drive}();")
            lines.append(f"            int _ret = (int) _inst.{m_drive2}();")
        else:
            lines.append(f"            _inst.{m_drive}();")
            lines.append(f"            int _ret = (int) _inst.{m_get_x}();")
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        lines.append(f"    {sys_name}_{m_drive}(_inst);")
        if is_p8:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_drive2}(_inst);")
        else:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_get_x}(_inst);")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        lines.append(f"    _inst.{m_drive}();")
        if is_p8:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_drive2}());")
        else:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_get_x}());")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        if is_p8:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    var _ret = _inst.{m_drive2}()")
        else:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    var _ret = _inst.{m_get_x}()")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'state-args')}")
        lines.append("    quit()")
    elif lang == "erlang":
        pass

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir",
                        default=str(Path(__file__).parent / "cases_state_args"))
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
    for f in out.glob("*"):
        f.unlink()

    index_rows = ["lang\tcase_id\tequiv_class\tsmoke\texpected"]
    smoke_count_by_lang = {}
    cases_per_lang = 0
    for lang in args.langs:
        spec = LANGS[lang]
        smoke_count = 0
        per_lang = 0
        for cid, equiv, expected, pattern, vt, is_smoke in enumerate_cases():
            src = gen_case(lang, cid, equiv, expected, pattern, vt, is_smoke)
            path = out / f"{cid}.{spec.ext}"
            path.write_text(src)
            index_rows.append(
                f"{lang}\t{cid}\t{equiv}\t{'yes' if is_smoke else 'no'}\t{expected}"
            )
            per_lang += 1
            if is_smoke:
                smoke_count += 1
        smoke_count_by_lang[lang] = smoke_count
        cases_per_lang = per_lang

    (out / "_index.tsv").write_text("\n".join(index_rows) + "\n")

    print(f"generated {cases_per_lang} cases × {len(smoke_count_by_lang)} langs into {out}")
    for lang, cnt in smoke_count_by_lang.items():
        print(f"  {lang}: {cases_per_lang} cases, {cnt} smoke")


if __name__ == "__main__":
    main()
