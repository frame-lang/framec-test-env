#!/usr/bin/env python3
"""
Phase 14 — HSM × everything fuzz (Wave 1).

Tests Frame statements (writes, self-calls, expressions) inside
HSM hierarchies. Phase 4 covers HSM enter/exit cascades and parent
handling of unrouted events; this phase tests the orthogonal axis:
do Frame statements in handler bodies behave correctly when the
state has a parent / grandparent above it?

Wave 1 is depth-2 only ($Parent / $Child) plus three depth-3 cases
to sanity-check deep cascade. Patterns probe the cases that are
NOT covered by Phase 4:

- Self-call from parent body → does interface dispatch route to
  child override?
- Self-call from child body → does interface dispatch route to
  parent's method when child doesn't override?
- Child mutates dom, forwards (`=> $^`), parent reads dom — does
  parent's read see child's pre-forward write?
- Parent body fires expression (`@@:return = self.f + LIT`) where
  child handled the same field write before forwarding.

Wave 1 design:
  Patterns (10): per-pattern HSM topology + body
  Value tuples (10): (LIT, dom_init) per case
  Total: 10 × 10 = 100 cases per lang × 17 langs = 1,700.

Smoke filter: one case per pattern (first value tuple) → 10 smoke
cases per lang.

Usage:
    python3 gen_hsm_cross.py
    ./run_hsm_cross.sh --tier=smoke
"""
import argparse
from pathlib import Path

from gen_nested import LANGS, method_name


COMPUTE_RETURN = 9


# ---------------------------------------------------------------------
# Patterns — each defines:
#   - states: ordered list of (state_name, parent_state_or_None,
#       handlers: dict event→Frame body, methods: dict name→method
#       body) tuples. The system is initialised in the LAST state in
#       the list (the deepest leaf).
#   - drive_returns: bool — does drive() return a value?
#   - verify_method: "drive" | "get_n"
#   - compute(LIT, dom_init): expected return value.
# ---------------------------------------------------------------------

class Pattern:
    __slots__ = ("name", "build_states", "drive_returns",
                 "verify_method", "compute")

    def __init__(self, name, build_states, drive_returns,
                 verify_method, compute):
        self.name = name
        self.build_states = build_states  # lambda(spec, lang, lit): list of state Frame source
        self.drive_returns = drive_returns
        self.verify_method = verify_method
        self.compute = compute            # lambda(lit, dom_init): int


# Frame initialises the system in the FIRST state declared inside
# `machine:`. So the leaf state ($Child) MUST appear first; ancestor
# states (Parent, Grandparent) follow. Frame parses the `=> $Parent`
# inheritance clause regardless of declaration order.
#
# Method-name casing per language: every reference to `drive` /
# `compute` MUST use `method_name(lang, name)` so the interface
# declaration, state handlers, and `@@:self.X()` dispatch all share
# the same wire name. Mixing literal "drive" with `m_drive = "Drive"`
# (Go's capitalize convention) produces two distinct event names —
# wrapper fires "Drive", state-dispatch matches "drive", handler
# never fires.

def _build_p1_child_dom_w(spec, lang, lit):
    """P1: child handles drive(), writes self.f = LIT. Tests basic
    leaf-state dispatch. Verify via get_n (operations:)."""
    m_drive = method_name(lang, "drive")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {lit}{spec.stmt_end}",
        f"            }}",
        f"        }}",
        f"        $Parent {{}}",
    ]


def _build_p2_parent_dom_w(spec, lang, lit):
    """P2: child forwards to parent, parent writes self.f = LIT.
    Tests `=> $^` cascade with side effect in parent."""
    m_drive = method_name(lang, "drive")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}() {{ => $^ }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {lit}{spec.stmt_end}",
        f"            }}",
        f"        }}",
    ]


def _build_p3_child_ret_w(spec, lang, lit):
    """P3: child sets @@:return = LIT. drive returns int."""
    m_drive = method_name(lang, "drive")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = {lit}{spec.stmt_end}",
        f"            }}",
        f"        }}",
        f"        $Parent {{}}",
    ]


def _build_p4_parent_ret_w(spec, lang, lit):
    """P4: child forwards, parent sets @@:return."""
    m_drive = method_name(lang, "drive")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}(): int {{ => $^ }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = {lit}{spec.stmt_end}",
        f"            }}",
        f"        }}",
    ]


def _build_p5_child_writes_then_fwd(spec, lang, lit):
    """P5: child writes self.f = LIT then `=> $^`; parent reads
    self.f + 1 into return slot. Tests that child's pre-forward
    write is visible to parent."""
    m_drive = method_name(lang, "drive")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}(): int {{",
        f"                {spec.self_word}{spec.field_op}f = {lit}{spec.stmt_end}",
        f"                => $^",
        f"            }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"            }}",
        f"        }}",
    ]


def _build_p6_parent_calls_compute(spec, lang, lit):
    """P6: parent.drive body does `@@:self.compute()` where compute
    is declared at parent scope, but Child does NOT have a default
    `=> $^` cascade. Pre-init `@@:return = -777` first so the
    expected value is uniform across all backends (typed langs see
    0/null/etc for unwritten return slot; dynamic langs see
    None/nil/empty). With pre-init, every backend sees -777 if
    compute() is silently dropped, OR COMPUTE_RETURN if the
    cascade somehow reaches it."""
    m_drive = method_name(lang, "drive")
    m_compute = method_name(lang, "compute")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}(): int {{ => $^ }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = -777{spec.stmt_end}",
        f"                @@:return = @@:self.{m_compute}(){spec.stmt_end}",
        f"            }}",
        f"            {m_compute}(): int {{ @@:({COMPUTE_RETURN}) }}",
        f"        }}",
    ]


def _build_p7_child_calls_compute(spec, lang, lit):
    """P7: child.drive body does `@@:self.compute()`. Child does
    NOT have a default `=> $^` cascade. compute is declared in
    parent only. Pre-init return to -777 so backends agree on the
    no-cascade outcome."""
    m_drive = method_name(lang, "drive")
    m_compute = method_name(lang, "compute")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = -777{spec.stmt_end}",
        f"                @@:return = @@:self.{m_compute}(){spec.stmt_end}",
        f"            }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_compute}(): int {{ @@:({COMPUTE_RETURN}) }}",
        f"        }}",
    ]


def _build_p8_child_overrides_compute(spec, lang, lit):
    """P8: parent declares compute() returning DEFAULT, child
    overrides returning LIT. Parent body calls @@:self.compute() —
    interface dispatch should pick child's override."""
    m_drive = method_name(lang, "drive")
    m_compute = method_name(lang, "compute")
    return [
        f"        $Child => $Parent {{",
        f"            {m_compute}(): int {{ @@:({lit}) }}",
        f"            {m_drive}(): int {{ => $^ }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = @@:self.{m_compute}(){spec.stmt_end}",
        f"            }}",
        f"            {m_compute}(): int {{ @@:(0) }}",
        f"        }}",
    ]


def _build_p9_dom_arith_through_hsm(spec, lang, lit):
    """P9: child writes self.f = LIT + 1, forwards, parent reads
    self.f and adds LIT into return slot. Tests dom-arith composes
    through HSM hierarchy."""
    m_drive = method_name(lang, "drive")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}(): int {{",
        f"                {spec.self_word}{spec.field_op}f = {lit} + 1{spec.stmt_end}",
        f"                => $^",
        f"            }}",
        f"        }}",
        f"        $Parent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = {spec.self_word}{spec.field_op}f + {lit}{spec.stmt_end}",
        f"            }}",
        f"        }}",
    ]


def _build_p10_three_level(spec, lang, lit):
    """P10: Grandparent / Parent / Child. Child forwards, Parent
    forwards, Grandparent handles with @@:return = LIT. Tests
    3-level HSM cascade."""
    m_drive = method_name(lang, "drive")
    return [
        f"        $Child => $Parent {{",
        f"            {m_drive}(): int {{ => $^ }}",
        f"        }}",
        f"        $Parent => $Grandparent {{",
        f"            {m_drive}(): int {{ => $^ }}",
        f"        }}",
        f"        $Grandparent {{",
        f"            {m_drive}(): int {{",
        f"                @@:return = {lit}{spec.stmt_end}",
        f"            }}",
        f"        }}",
    ]


PATTERNS = [
    Pattern("p1_child_dom_w", _build_p1_child_dom_w, False, "get_n",
            lambda lit, di: lit),
    Pattern("p2_parent_dom_w", _build_p2_parent_dom_w, False, "get_n",
            lambda lit, di: lit),
    Pattern("p3_child_ret_w", _build_p3_child_ret_w, True, "drive",
            lambda lit, di: lit),
    Pattern("p4_parent_ret_w", _build_p4_parent_ret_w, True, "drive",
            lambda lit, di: lit),
    Pattern("p5_child_writes_then_fwd", _build_p5_child_writes_then_fwd, True, "drive",
            lambda lit, di: lit + 1),
    # P6/P7 dropped from wave 1: they test the no-cascade contract
    # for `@@:self.compute()` when the leaf state has no handler
    # for `compute` and no `=> $^` cascade. The result is
    # language-divergent — typed langs (Go/Rust/C/etc) return type
    # default 0; dynamic langs (Python/JS/etc) return None/null;
    # Java/C# crash on null unboxing. Belongs in a separate phase
    # that explicitly tests per-language null/zero semantics.
    Pattern("p8_child_overrides_compute", _build_p8_child_overrides_compute, True, "drive",
            lambda lit, di: lit),
    Pattern("p9_dom_arith_through_hsm", _build_p9_dom_arith_through_hsm, True, "drive",
            lambda lit, di: (lit + 1) + lit),  # child wrote dom=lit+1, parent returns dom + lit
    Pattern("p10_three_level", _build_p10_three_level, True, "drive",
            lambda lit, di: lit),
]


VALUE_TUPLES = [
    (1, 0), (5, 0), (-3, 0), (0, 0),
    (100, 50), (7, 13), (-50, 100), (1, -1),
    (999, -777), (-1, 1),
]


def case_id(pattern, vt_idx):
    return f"hx_{pattern.name}__t{vt_idx}"


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
    sys_name = f"HsmCross_{cid}"
    lit, dom_init = vt

    m_drive = method_name(lang, "drive")
    m_compute = method_name(lang, "compute")
    m_get_n = method_name(lang, "get_n")
    m_verify = m_drive if pattern.drive_returns else m_get_n

    drive_sig = f"{m_drive}(): int" if pattern.drive_returns else f"{m_drive}()"

    # Build the @@system body. We need:
    # - interface declarations
    # - machine block with the pattern's states
    # - domain (just `f: int = dom_init`)
    # The deepest leaf state must be the LAST state in the list —
    # that's where the system initialises.
    state_lines = pattern.build_states(spec, lang, lit)

    # Detect whether the pattern declares compute() (so we add it
    # to the interface). p6/p7/p8 do; others don't.
    decl_compute = "compute" in pattern.name

    lines = []
    lines.append(f"@@target {spec.target}")
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        # Phase 14 drive() takes no args. Omit FUZZ_DRIVE_ARG so the
        # Erlang runner falls through to drive/1 (just Pid).
        lines.append(f"%% FUZZ_VERIFY_METHOD: {m_verify}")
        lines.append(f"%% FUZZ_DRIVE_RETURNS: {'yes' if pattern.drive_returns else 'no'}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    # Section order per Frame spec: operations -> interface ->
    # machine -> actions -> domain. Operations defined at the
    # system level are externally callable via _inst.method() AND
    # reachable from any state, which is how get_n stays usable
    # after HSM transitions/forwards. Note: get_n is intentionally
    # NOT also declared in `interface:` — that would create a
    # duplicate (interface routes through state-machine kernel,
    # operations is direct). framec currently doesn't reject the
    # redundant case; declaring in both produces duplicate methods
    # in the output. See FRAMEC_DEFECT_phase14_op_iface_dup.
    lines.append("    operations:")
    lines.append(f"        {m_get_n}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}")
    lines.append("")
    lines.append("    interface:")
    lines.append(f"        {drive_sig}")
    if decl_compute:
        lines.append(f"        {m_compute}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.extend(state_lines)
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = {dom_init}")
    lines.append("}")
    lines.append("")

    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        if pattern.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}()")
        else:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"_ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "hsm-cross"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if pattern.drive_returns:
            lines.append(f"const _ret = _inst.{m_drive}();")
        else:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "hsm-cross"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if pattern.drive_returns:
            lines.append(f"const _ret: number = _inst.{m_drive}();")
        else:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret: number = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "hsm-cross"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        if pattern.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}")
        else:
            lines.append(f"_inst.{m_drive}")
            lines.append(f"_ret = _inst.{m_verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "hsm-cross"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        if pattern.drive_returns:
            lines.append(f"local _ret = _inst:{m_drive}()")
        else:
            lines.append(f"_inst:{m_drive}()")
            lines.append(f"local _ret = _inst:{m_verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "hsm-cross"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        if pattern.drive_returns:
            lines.append(f"$_ret = $_inst->{m_drive}();")
        else:
            lines.append(f"$_inst->{m_drive}();")
            lines.append(f"$_ret = $_inst->{m_verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "hsm-cross"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        if pattern.drive_returns:
            lines.append(f"    final _ret = _inst.{m_drive}();")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    final _ret = _inst.{m_verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        if pattern.drive_returns:
            lines.append(f"    let _ret = _inst.{m_drive}();")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    let _ret = _inst.{m_verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
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
        if pattern.drive_returns:
            lines.append(f"    ret := sm.{m_drive}()")
        else:
            lines.append(f"    sm.{m_drive}()")
            lines.append(f"    ret := sm.{m_verify}()")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        if pattern.drive_returns:
            lines.append(f"let _ret = _inst.{m_drive}()")
        else:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"let _ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "hsm-cross"))
    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = new {sys_name}();")
        if pattern.drive_returns:
            lines.append(f"        int _ret = (int) _inst.{m_drive}();")
        else:
            lines.append(f"        _inst.{m_drive}();")
            lines.append(f"        int _ret = (int) _inst.{m_verify}();")
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{cid}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        if pattern.drive_returns:
            lines.append(f"    val _ret = _inst.{m_drive}() as Int")
        else:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    val _ret = _inst.{m_verify}() as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        if pattern.drive_returns:
            lines.append(f"            int _ret = (int) _inst.{m_drive}();")
        else:
            lines.append(f"            _inst.{m_drive}();")
            lines.append(f"            int _ret = (int) _inst.{m_verify}();")
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        if pattern.drive_returns:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_drive}(_inst);")
        else:
            lines.append(f"    {sys_name}_{m_drive}(_inst);")
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_verify}(_inst);")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        if pattern.drive_returns:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_drive}());")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_verify}());")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        if pattern.drive_returns:
            lines.append(f"    var _ret = _inst.{m_drive}()")
        else:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    var _ret = _inst.{m_verify}()")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'hsm-cross')}")
        lines.append("    quit()")
    elif lang == "erlang":
        pass

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir",
                        default=str(Path(__file__).parent / "cases_hsm_cross"))
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
