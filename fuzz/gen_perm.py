#!/usr/bin/env python3
"""
Phase 10 — full-permutation expression fuzz.

Single-statement, depth ≤ 2 cross-product of:
  - LHS targets (v1: only @@:return)
  - Receivers (literal, domain field, state var, parameter, self-call)
  - Operators (arithmetic: +, -, *)

Each generated case carries:
  - FUZZ_EXPECTED_N: <int>          asserted by the inline driver
  - FUZZ_EQUIV_CLASS: <coarse_tag>  used by --tier=smoke filter
  - FUZZ_SMOKE: yes|no              precomputed smoke selection

The generator simulates Frame execution to compute the expected value
deterministically — no interpreter loop, just constant-folding the
known-receiver values through the operator function.

Out of scope (v1):
  - Depth-3 nesting (covered by Phase 9 p7/p8)
  - Multi-statement bodies
  - Control-flow contexts (if/while)
  - Transition placement
  - Multi-system, async, negative cases (separate phases)

Usage:
    python3 gen_perm.py --langs python_3
    python3 gen_perm.py                          # all 17
    ./run_perm.sh --tier=smoke --lang=python_3
"""
import argparse
from pathlib import Path

# Reuse Phase 9's LangSpec / method_name / op_call so per-language
# emission stays in one place. The per-pattern body in Phase 9 differs
# per pattern; here it differs per (recv1, op, recv2) triple.
from gen_nested import LANGS, method_name, op_call


# Domain + state-var seeds used by every case. These values get
# folded into the simulator below.
DOMAIN_N_INIT = 4
SV_SCACHE_INIT = 7
PARAM_X_VALUE = 6
COMPUTE_RETURN = 9


class Receiver:
    """One concrete receiver of a value, with its codegen rendering
    and its compile-time-known integer value used by the expected-
    value simulator."""
    __slots__ = ("name", "smoke_class", "value", "frame_src")

    def __init__(self, name, smoke_class, value, frame_src):
        # name: short id used in the filename and full tag.
        # smoke_class: coarsened bucket for smoke-tier selection.
        # value: integer the simulator folds into the expression.
        # frame_src: lambda(spec, sys_name) -> str. Renders the
        #   receiver in Frame source (pre-framec). Allowed to use
        #   spec.self_word, spec.field_op, spec.param_prefix and
        #   call op_call() for native passthrough cases.
        self.name = name
        self.smoke_class = smoke_class
        self.value = value
        self.frame_src = frame_src


class Operator:
    __slots__ = ("name", "src", "fn")

    def __init__(self, name, src, fn):
        # name: short id (plus, minus, times). Goes into the tag.
        # src: literal token framec passes through (`+`, `-`, `*`).
        # fn: lambda(a, b) -> int. Computes the expected value.
        self.name = name
        self.src = src
        self.fn = fn


def _r_lit(val, name):
    return Receiver(
        name=name,
        smoke_class="lit",
        value=val,
        frame_src=lambda spec, sys_name: str(val),
    )


def _r_dom_n(spec, sys_name):
    # `self.n` / `this.n` / `s.n` per backend.
    return f"{spec.self_word}{spec.field_op}n"


def _r_sv_scache(spec, sys_name):
    # `$.scache` — Frame state-var read. framec lowers per-target.
    return "$.scache"


def _r_param_x(spec, sys_name):
    # Parameter `x` from drive(x: int). PHP needs `$x`.
    return f"{spec.param_prefix}x"


def _r_selfcall_compute(spec, sys_name):
    # @@:self.compute() — interface dispatch returning 9.
    m = method_name(spec.target if spec.target != "cpp_17" else "cpp", "compute")
    return f"@@:self.{m}()"


def _r_selfcall_add_one_2(spec, sys_name):
    # @@:self.add_one(2) — selfcall with one arg.
    m = method_name(spec.target if spec.target != "cpp_17" else "cpp", "add_one")
    return f"@@:self.{m}(2)"


# Receivers cover one example per codegen path:
#   lit_*       — constant-fold path
#   dom_n       — domain field read
#   sv_scache   — state-var dict read (Dart cast bug from p11 lives here)
#   param_x     — parameter read
#   selfcall_*  — interface dispatch (Erlang p13 bug from suffix lives here)
RECEIVERS = [
    _r_lit(5, "lit5"),
    _r_lit(-3, "litn3"),
    Receiver("dom_n", "fieldread", DOMAIN_N_INIT, _r_dom_n),
    Receiver("sv_scache", "fieldread", SV_SCACHE_INIT, _r_sv_scache),
    Receiver("param_x", "fieldread", PARAM_X_VALUE, _r_param_x),
    Receiver("sc_compute", "selfcall", COMPUTE_RETURN, _r_selfcall_compute),
    Receiver("sc_addone2", "selfcall", 3, _r_selfcall_add_one_2),
]

OPERATORS = [
    Operator("plus", "+", lambda a, b: a + b),
    Operator("minus", "-", lambda a, b: a - b),
    Operator("times", "*", lambda a, b: a * b),
]


class LhsTarget:
    """One LHS write target. The driver verifies via a different
    accessor depending on which slot was written:
      - ret: drive(): int → check return.
      - dom: drive() void; sets self.n; verify via get_n().
      - sv:  drive() void; sets $.scache; verify via get_scache().
    All three exercise different framec codegen paths (return-slot
    vs domain-field write vs state-var dict write). Dart's p11
    bug from this evening lived in the state-var-read path; this
    exercises the matching write path in v2."""
    __slots__ = ("name", "smoke_class", "drive_returns", "frame_lhs", "verify_method")

    def __init__(self, name, smoke_class, drive_returns, frame_lhs, verify_method):
        self.name = name
        self.smoke_class = smoke_class
        self.drive_returns = drive_returns  # bool
        self.frame_lhs = frame_lhs            # str: e.g. "@@:return", "self.n", "$.scache"
        self.verify_method = verify_method    # str: interface method name to read back

# For dom-LHS: framec passes native code through unchanged, so the
# Frame source MUST contain the per-language self-word + field-op
# (e.g., `this.n` for JS, `self->n` for C). Phase 9's gen_nested.py
# uses the same convention via `self_word + field_op`.
def _dom_lhs_frame_src(spec):
    return f"{spec.self_word}{spec.field_op}n"

LHS_TARGETS = [
    LhsTarget("ret", "ret", True, lambda spec: "@@:return", "drive"),       # @@:return is Frame syntax — same on every backend
    LhsTarget("dom", "dom", False, _dom_lhs_frame_src, "get_n"),            # native LHS — needs per-lang lowering
    LhsTarget("sv",  "sv",  False, lambda spec: "$.scache", "get_scache"),  # $. is Frame syntax — same on every backend
]


def lang_name_for_method(lang):
    """Bridge between gen_nested.LANGS keys and method_name's
    expected lang argument. Phase 9's method_name() uses 'go' as
    the only special-case branch; everything else takes the input
    verbatim. Pass through unmodified."""
    return lang


def render_receiver(recv, spec, lang, sys_name):
    """Re-render the receiver inside a target language's spec.
    Method-name casing is rebound here because Receiver lambdas
    closed over the wrong lang arg in the simple case."""
    # Re-do the selfcall renderings with the correct lang for casing.
    if recv.name == "sc_compute":
        m = method_name(lang, "compute")
        return f"@@:self.{m}()"
    if recv.name == "sc_addone2":
        m = method_name(lang, "add_one")
        return f"@@:self.{m}(2)"
    return recv.frame_src(spec, sys_name)


def case_id(lhs, recv1, op, recv2):
    """Unique ID encoding the (lhs, recv1, op, recv2) tuple."""
    return f"{lhs.name}_d2_{recv1.name}_{op.name}_{recv2.name}"


def case_id_depth1(lhs, recv):
    return f"{lhs.name}_d1_{recv.name}"


def smoke_tag_depth2(lhs, recv1, op, recv2):
    """Coarse equivalence-class tag. Smoke tier picks one case per
    unique smoke_tag, so cardinality is |lhs| * |recv_classes|^2 *
    |operators| ≈ 81 for the v2 dimension set (3 * 3 * 3 * 3)."""
    return f"{lhs.smoke_class}_d2_{recv1.smoke_class}_{op.name}_{recv2.smoke_class}"


def smoke_tag_depth1(lhs, recv):
    return f"{lhs.smoke_class}_d1_{recv.smoke_class}"


def expected_value_depth2(recv1, op, recv2):
    return op.fn(recv1.value, recv2.value)


def expected_value_depth1(recv):
    return recv.value


def gen_case(lang, case_id_str, smoke_tag, expected, frame_expr,
             recv_tokens, is_smoke, lhs, drive_arg=PARAM_X_VALUE):
    """Emit one .f<ext> source for a (lang, lhs, case) tuple. The
    drive() handler writes `<lhs.frame_lhs> = expr`. If the LHS is
    @@:return, drive returns int; otherwise drive is void and the
    inline driver verifies via lhs.verify_method (get_n /
    get_scache)."""
    spec = LANGS[lang]
    sys_name = f"FuzzPerm_{case_id_str}"

    m_drive = method_name(lang, "drive")
    m_compute = method_name(lang, "compute")
    m_add_one = method_name(lang, "add_one")
    m_get_n = method_name(lang, "get_n")
    m_get_scache = method_name(lang, "get_scache")
    m_verify = method_name(lang, lhs.verify_method)

    drive_sig = f"{m_drive}(x: int): int" if lhs.drive_returns else f"{m_drive}(x: int)"

    lines = []
    lines.append(f"@@target {spec.target}")
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {smoke_tag}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        lines.append(f"%% FUZZ_DRIVE_ARG: {drive_arg}")
        lines.append(f"%% FUZZ_VERIFY_METHOD: {m_verify}")
        lines.append(f"%% FUZZ_DRIVE_RETURNS: {'yes' if lhs.drive_returns else 'no'}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append(f"        {drive_sig}")
    lines.append(f"        {m_compute}(): int")
    lines.append(f"        {m_add_one}(x: int): int")
    lines.append(f"        {m_get_n}(): int")
    lines.append(f"        {m_get_scache}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $S0 {")
    lines.append(f"            $.scache: int = {SV_SCACHE_INIT}")
    lines.append(f"            {drive_sig} {{")
    # Frame source LHS: `@@:return` and `$.scache` are Frame syntax
    # framec lowers per-target; native dom LHS (`this.n` / `self->n`)
    # passes through unchanged so it must be pre-substituted here.
    lhs_src = lhs.frame_lhs(spec)
    lines.append(f"                {lhs_src} = {frame_expr}{spec.stmt_end}")
    lines.append(f"            }}")
    lines.append(f"            {m_compute}(): int {{ @@:({COMPUTE_RETURN}) }}")
    lines.append(f"            {m_add_one}(x: int): int {{ @@:({spec.param_prefix}x + 1) }}")
    lines.append(f"            {m_get_n}(): int {{ @@:({spec.self_word}{spec.field_op}n) }}")
    lines.append(f"            {m_get_scache}(): int {{ @@:($.scache) }}")
    lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        n: int = {DOMAIN_N_INIT}")
    lines.append("}")
    lines.append("")

    # Inline driver per language. The drive call always passes the
    # parameter; the verification step is either drive's own return
    # (lhs.drive_returns=True) or a separate read-back call to
    # lhs.verify_method.
    drive_arg_str = str(drive_arg)
    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        if lhs.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str})")
            lines.append(f"_ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "perm-fuzz"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if lhs.drive_returns:
            lines.append(f"const _ret = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str});")
            lines.append(f"const _ret = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "perm-fuzz"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if lhs.drive_returns:
            lines.append(f"const _ret: number = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str});")
            lines.append(f"const _ret: number = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "perm-fuzz"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        if lhs.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str})")
            lines.append(f"_ret = _inst.{m_verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "perm-fuzz"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        if lhs.drive_returns:
            lines.append(f"local _ret = _inst:{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst:{m_drive}({drive_arg_str})")
            lines.append(f"local _ret = _inst:{m_verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "perm-fuzz"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        if lhs.drive_returns:
            lines.append(f"$_ret = $_inst->{m_drive}({drive_arg_str});")
        else:
            lines.append(f"$_inst->{m_drive}({drive_arg_str});")
            lines.append(f"$_ret = $_inst->{m_verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "perm-fuzz"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        if lhs.drive_returns:
            lines.append(f"    final _ret = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str});")
            lines.append(f"    final _ret = _inst.{m_verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        if lhs.drive_returns:
            lines.append(f"    let _ret = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str});")
            lines.append(f"    let _ret = _inst.{m_verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
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
        if lhs.drive_returns:
            lines.append(f"    ret := sm.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"    sm.{m_drive}({drive_arg_str})")
            lines.append(f"    ret := sm.{m_verify}()")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        if lhs.drive_returns:
            lines.append(f"let _ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str})")
            lines.append(f"let _ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "perm-fuzz"))
    elif lang == "java":
        lines.append("class Main {")
        lines.append(f"    public static void main(String[] args) {{")
        lines.append(f"        var _inst = new {sys_name}();")
        if lhs.drive_returns:
            lines.append(f"        int _ret = (int) _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"        _inst.{m_drive}({drive_arg_str});")
            lines.append(f"        int _ret = (int) _inst.{m_verify}();")
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{case_id_str}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        if lhs.drive_returns:
            lines.append(f"    val _ret = _inst.{m_drive}({drive_arg_str}) as Int")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str})")
            lines.append(f"    val _ret = _inst.{m_verify}() as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{case_id_str} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        if lhs.drive_returns:
            lines.append(f"            int _ret = (int) _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"            _inst.{m_drive}({drive_arg_str});")
            lines.append(f"            int _ret = (int) _inst.{m_verify}();")
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        if lhs.drive_returns:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_drive}(_inst, {drive_arg_str});")
        else:
            lines.append(f"    {sys_name}_{m_drive}(_inst, {drive_arg_str});")
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_verify}(_inst);")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        if lhs.drive_returns:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_drive}({drive_arg_str}));")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str});")
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_verify}());")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        if lhs.drive_returns:
            lines.append(f"    var _ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str})")
            lines.append(f"    var _ret = _inst.{m_verify}()")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perm-fuzz')}")
        lines.append("    quit()")
    elif lang == "erlang":
        # Erlang external escript driver — consumes FUZZ_VERIFY_METHOD
        # + FUZZ_DRIVE_RETURNS in addition to the v1 metadata.
        pass

    return "\n".join(lines)


def _is_self_assign_d1(lhs, recv):
    """Detect literal `LHS = LHS` cases where LHS and recv are the
    same memory cell. These are semantic no-ops that add no codegen
    coverage and Swift's compiler explicitly rejects them
    (D3 in DEFECTS.md). Filter applies only at depth-1 — depth-2
    expressions like `self.n = self.n + 5` are NOT self-assigns."""
    if lhs.name == "dom" and recv.name == "dom_n":
        return True
    if lhs.name == "sv" and recv.name == "sv_scache":
        return True
    return False


def enumerate_cases():
    """Yield (case_id, smoke_tag, expected, frame_expr_template,
    is_smoke, lhs) for every (lhs, depth-1|depth-2, recv1, op,
    recv2) cell in deterministic order. is_smoke is True for the
    FIRST occurrence of each smoke_tag."""
    seen_smoke_tags = set()

    for lhs in LHS_TARGETS:
        # Depth-1: just `recv` as the expression.
        for recv in RECEIVERS:
            if _is_self_assign_d1(lhs, recv):
                continue
            cid = case_id_depth1(lhs, recv)
            stag = smoke_tag_depth1(lhs, recv)
            is_smoke = stag not in seen_smoke_tags
            if is_smoke:
                seen_smoke_tags.add(stag)
            yield (cid, stag, recv.value, ("d1", recv, None, None), is_smoke, lhs)

        # Depth-2: recv1 op recv2.
        for recv1 in RECEIVERS:
            for op in OPERATORS:
                for recv2 in RECEIVERS:
                    cid = case_id(lhs, recv1, op, recv2)
                    stag = smoke_tag_depth2(lhs, recv1, op, recv2)
                    is_smoke = stag not in seen_smoke_tags
                    if is_smoke:
                        seen_smoke_tags.add(stag)
                    expected = expected_value_depth2(recv1, op, recv2)
                    yield (cid, stag, expected, ("d2", recv1, op, recv2), is_smoke, lhs)


def render_frame_expr(template, lang, spec, sys_name):
    """Materialise the expression template into a Frame source
    snippet for the target language. For depth-1 it's the receiver
    text; for depth-2 it's `<recv1> <op_src> <recv2>`."""
    kind = template[0]
    if kind == "d1":
        _, recv, _, _ = template
        return render_receiver(recv, spec, lang, sys_name)
    elif kind == "d2":
        _, recv1, op, recv2 = template
        sys_name_ignored = sys_name
        r1 = render_receiver(recv1, spec, lang, sys_name_ignored)
        r2 = render_receiver(recv2, spec, lang, sys_name_ignored)
        return f"{r1} {op.src} {r2}"
    else:
        raise ValueError(f"unknown template kind {kind}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir",
                        default=str(Path(__file__).parent / "cases_perm"))
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

    # Sidecar index: one row per case across all langs. Runner's
    # smoke filter reads this. Format:
    #   lang    case_id    equiv_class    smoke    expected
    index_rows = ["lang\tcase_id\tequiv_class\tsmoke\texpected"]

    total = 0
    smoke_count_by_lang = {}
    for lang in args.langs:
        spec = LANGS[lang]
        smoke_count = 0
        for cid, smoke_tag, expected, template, is_smoke, lhs in enumerate_cases():
            sys_name = f"FuzzPerm_{cid}"
            expr = render_frame_expr(template, lang, spec, sys_name)
            src = gen_case(lang, cid, smoke_tag, expected, expr,
                           None, is_smoke, lhs)
            path = out / f"{cid}.{spec.ext}"
            path.write_text(src)
            index_rows.append(
                f"{lang}\t{cid}\t{smoke_tag}\t{'yes' if is_smoke else 'no'}\t{expected}"
            )
            total += 1
            if is_smoke:
                smoke_count += 1
        smoke_count_by_lang[lang] = smoke_count

    (out / "_index.tsv").write_text("\n".join(index_rows) + "\n")

    print(f"generated {total} cases across {len(args.langs)} langs into {out}")
    for lang, cnt in smoke_count_by_lang.items():
        cases_for_lang = total // len(args.langs)
        print(f"  {lang}: {cases_for_lang} cases, {cnt} smoke")


if __name__ == "__main__":
    main()
