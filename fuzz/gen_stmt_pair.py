#!/usr/bin/env python3
"""
Phase 11 — statement-pair sequencing fuzz (Wave 1).

Two-statement handler bodies. Each case is `S1; S2;` where S1 writes
to one of {self.f, $.s, @@:return} (or fires a self-call) and S2
either reads what S1 wrote or writes a different slot. The
generator simulates the resulting state to compute the expected
return value (or expected get_n / get_scache value).

What this exercises that Phase 9/10 don't:
- Read-after-write within a single handler: does S2 see S1's write?
- Write-after-write across slots: do dom/sv/return slots stay
  independent? Last-write-wins on the same slot.
- Self-call result flowing through a domain field: `self.f =
  @@:self.compute()` then `@@:return = self.f + LIT`.
- @@:return survival when subsequent statements modify domain/sv.
- Cross-statement transition guard: no transitions in Wave 1, but
  the harness leaves room for a transition-bearing v2.

Wave 1 design:
  S1 ∈ {dom_w, sv_w, ret_w, sc_bare, sc_assign_dom}        (5)
  S2 ∈ {dom_to_ret, sv_to_ret, dom_plus_lit, sv_plus_lit,
        dom_w_lit}                                          (5)
  LIT ∈ {1, 5, -3, 0}                                       (4)
  Total: 5 × 5 × 4 = 100 cases per lang.

Smoke filter: one case per (S1, S2) pair (LIT=1) → 25 smoke cases.

Drive returns int unless S2 = dom_w_lit (then drive is void and
verify uses get_n).

Usage:
    python3 gen_stmt_pair.py
    python3 gen_stmt_pair.py --langs python_3
    ./run_stmt_pair.sh --tier=smoke --lang=python_3
"""
import argparse
from pathlib import Path

# Reuse Phase 9's per-language scaffolding (LangSpec, method_name,
# op_call). Phase 11 doesn't introduce new languages — only new
# Frame source patterns — so the existing LANGS table is
# authoritative.
from gen_nested import LANGS, method_name


# Domain + state-var seeds. Both start at 0 so that any non-zero
# return value tells us S1 actually executed and S2 read its write.
DOMAIN_F_INIT = 0
SV_S_INIT = 0
PARAM_X_VALUE = 7
COMPUTE_RETURN = 9   # @@:self.compute() returns this.


# LIT values used in S1 (when S1 writes a literal) and S2 (when S2
# adds a literal to a read). Picked to surface arithmetic-sign and
# zero-handling bugs.
LIT_VALUES = [1, 5, -3, 0]


# ---------------------------------------------------------------------
# Statement kinds
# ---------------------------------------------------------------------

class S1Kind:
    """First statement. Records what slot it writes and the
    post-condition the simulator should apply."""
    __slots__ = ("name", "writes_dom", "writes_sv", "writes_ret",
                 "render", "post_dom", "post_sv", "post_ret")

    def __init__(self, name, writes_dom, writes_sv, writes_ret,
                 render, post_dom, post_sv, post_ret):
        self.name = name
        self.writes_dom = writes_dom
        self.writes_sv = writes_sv
        self.writes_ret = writes_ret
        self.render = render          # lambda(spec, lang, sys, lit): str (Frame source)
        self.post_dom = post_dom      # lambda(state, lit): new_dom_value or None
        self.post_sv = post_sv        # lambda(state, lit): new_sv_value or None
        self.post_ret = post_ret      # lambda(state, lit): new_ret_value or None


class S2Kind:
    """Second statement. Records what it reads and writes plus how
    the driver verifies the outcome."""
    __slots__ = ("name", "writes_dom", "writes_sv", "writes_ret",
                 "drive_returns", "verify_method", "render",
                 "post_dom", "post_sv", "post_ret")

    def __init__(self, name, writes_dom, writes_sv, writes_ret,
                 drive_returns, verify_method, render,
                 post_dom, post_sv, post_ret):
        self.name = name
        self.writes_dom = writes_dom
        self.writes_sv = writes_sv
        self.writes_ret = writes_ret
        self.drive_returns = drive_returns   # bool
        self.verify_method = verify_method   # str: "drive" if drive returns else "get_n"/"get_scache"
        self.render = render                  # lambda(spec, lang, sys, lit): str
        self.post_dom = post_dom              # lambda(state, lit): new or None
        self.post_sv = post_sv
        self.post_ret = post_ret


# --- S1 renderers -----------------------------------------------------

def _s1_dom_w(spec, lang, sys, lit):
    return f"{spec.self_word}{spec.field_op}f = {lit}"


def _s1_sv_w(spec, lang, sys, lit):
    return f"$.s = {lit}"


def _s1_ret_w(spec, lang, sys, lit):
    return f"@@:return = {lit}"


def _s1_sc_bare(spec, lang, sys, lit):
    # Bare self-call. compute() returns 9 but we discard it.
    m = method_name(lang, "compute")
    return f"@@:self.{m}()"


def _s1_sc_assign_dom(spec, lang, sys, lit):
    # self.f = @@:self.compute() — self-call result flowing into
    # domain field. Tests D1 fix (defer transition guard until
    # end-of-statement).
    m = method_name(lang, "compute")
    return f"{spec.self_word}{spec.field_op}f = @@:self.{m}()"


S1_KINDS = [
    S1Kind("dom_w", True, False, False, _s1_dom_w,
           lambda st, lit: lit, None, None),
    S1Kind("sv_w", False, True, False, _s1_sv_w,
           None, lambda st, lit: lit, None),
    S1Kind("ret_w", False, False, True, _s1_ret_w,
           None, None, lambda st, lit: lit),
    S1Kind("sc_bare", False, False, False, _s1_sc_bare,
           None, None, None),
    S1Kind("sc_assign_dom", True, False, False, _s1_sc_assign_dom,
           lambda st, lit: COMPUTE_RETURN, None, None),
]


# --- S2 renderers -----------------------------------------------------

def _s2_dom_to_ret(spec, lang, sys, lit):
    return f"@@:return = {spec.self_word}{spec.field_op}f"


def _s2_sv_to_ret(spec, lang, sys, lit):
    return "@@:return = $.s"


def _s2_dom_plus_lit(spec, lang, sys, lit):
    return f"@@:return = {spec.self_word}{spec.field_op}f + {lit}"


def _s2_sv_plus_lit(spec, lang, sys, lit):
    return f"@@:return = $.s + {lit}"


def _s2_dom_w_lit(spec, lang, sys, lit):
    # Drive is void; verify reads dom field via get_n.
    return f"{spec.self_word}{spec.field_op}f = {lit}"


S2_KINDS = [
    S2Kind("dom_to_ret", False, False, True, True, "drive",
           _s2_dom_to_ret,
           None, None,
           lambda st, lit: st["dom"]),
    S2Kind("sv_to_ret", False, False, True, True, "drive",
           _s2_sv_to_ret,
           None, None,
           lambda st, lit: st["sv"]),
    S2Kind("dom_plus_lit", False, False, True, True, "drive",
           _s2_dom_plus_lit,
           None, None,
           lambda st, lit: st["dom"] + lit),
    S2Kind("sv_plus_lit", False, False, True, True, "drive",
           _s2_sv_plus_lit,
           None, None,
           lambda st, lit: st["sv"] + lit),
    S2Kind("dom_w_lit", True, False, False, False, "get_n",
           _s2_dom_w_lit,
           lambda st, lit: lit, None, None),
]


# ---------------------------------------------------------------------
# Simulator
# ---------------------------------------------------------------------

def simulate(s1, s2, lit):
    """Simulate the case. Returns the value the driver should
    observe (drive return for ret-writing S2, get_n value for
    dom-writing S2)."""
    state = {"dom": DOMAIN_F_INIT, "sv": SV_S_INIT, "ret": 0}

    # Apply S1 effects.
    if s1.post_dom is not None:
        state["dom"] = s1.post_dom(state, lit)
    if s1.post_sv is not None:
        state["sv"] = s1.post_sv(state, lit)
    if s1.post_ret is not None:
        state["ret"] = s1.post_ret(state, lit)

    # Apply S2 effects (S2 reads happen against the post-S1 state).
    if s2.post_ret is not None:
        state["ret"] = s2.post_ret(state, lit)
    if s2.post_dom is not None:
        state["dom"] = s2.post_dom(state, lit)
    if s2.post_sv is not None:
        state["sv"] = s2.post_sv(state, lit)

    if s2.drive_returns:
        return state["ret"]
    if s2.verify_method == "get_n":
        return state["dom"]
    if s2.verify_method == "get_scache":
        return state["sv"]
    raise ValueError(f"unhandled verify_method {s2.verify_method}")


def case_id(s1, s2, lit):
    sign = "n" if lit < 0 else ""
    return f"sp_{s1.name}__{s2.name}__lit{sign}{abs(lit)}"


def equiv_class(s1, s2):
    """Smoke uses one case per (s1, s2) pair — LIT variation is the
    long tail; the structural shape is what matters at smoke."""
    return f"{s1.name}__{s2.name}"


def enumerate_cases():
    seen_classes = set()
    for s1 in S1_KINDS:
        for s2 in S2_KINDS:
            for lit in LIT_VALUES:
                cid = case_id(s1, s2, lit)
                cls = equiv_class(s1, s2)
                is_smoke = cls not in seen_classes
                if is_smoke:
                    seen_classes.add(cls)
                expected = simulate(s1, s2, lit)
                yield (cid, cls, expected, s1, s2, lit, is_smoke)


# ---------------------------------------------------------------------
# Per-language case emission. Most boilerplate mirrors gen_perm.py
# but the handler body is two statements instead of one. Drivers are
# kept inline rather than imported so the two phases stay
# independently editable.
# ---------------------------------------------------------------------

def gen_case(lang, cid, equiv, expected, s1, s2, lit, is_smoke):
    spec = LANGS[lang]
    sys_name = f"StmtPair_{cid}"

    m_drive = method_name(lang, "drive")
    m_compute = method_name(lang, "compute")
    m_get_n = method_name(lang, "get_n")
    m_get_scache = method_name(lang, "get_scache")
    m_verify = m_drive if s2.drive_returns else (
        m_get_n if s2.verify_method == "get_n" else m_get_scache
    )

    drive_sig = (
        f"{m_drive}(x: int): int" if s2.drive_returns
        else f"{m_drive}(x: int)"
    )

    s1_src = s1.render(spec, lang, sys_name, lit)
    s2_src = s2.render(spec, lang, sys_name, lit)

    lines = []
    lines.append(f'@@[target("{spec.target}")]')
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        lines.append(f"%% FUZZ_DRIVE_ARG: {PARAM_X_VALUE}")
        lines.append(f"%% FUZZ_VERIFY_METHOD: {m_verify}")
        lines.append(f"%% FUZZ_DRIVE_RETURNS: {'yes' if s2.drive_returns else 'no'}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append(f"        {drive_sig}")
    lines.append(f"        {m_compute}(): int")
    lines.append(f"        {m_get_n}(): int")
    lines.append(f"        {m_get_scache}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $S0 {")
    lines.append(f"            $.s: int = {SV_S_INIT}")
    lines.append(f"            {drive_sig} {{")
    lines.append(f"                {s1_src}{spec.stmt_end}")
    lines.append(f"                {s2_src}{spec.stmt_end}")
    lines.append(f"            }}")
    lines.append(f"            {m_compute}(): int {{ @@:({COMPUTE_RETURN}) }}")
    lines.append(f"            {m_get_n}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}")
    lines.append(f"            {m_get_scache}(): int {{ @@:($.s) }}")
    lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = {DOMAIN_F_INIT}")
    lines.append("}")
    lines.append("")

    drive_arg_str = str(PARAM_X_VALUE)
    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        if s2.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str})")
            lines.append(f"_ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "stmt-pair"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if s2.drive_returns:
            lines.append(f"const _ret = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str});")
            lines.append(f"const _ret = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "stmt-pair"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if s2.drive_returns:
            lines.append(f"const _ret: number = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str});")
            lines.append(f"const _ret: number = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "stmt-pair"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        if s2.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str})")
            lines.append(f"_ret = _inst.{m_verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "stmt-pair"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        if s2.drive_returns:
            lines.append(f"local _ret = _inst:{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst:{m_drive}({drive_arg_str})")
            lines.append(f"local _ret = _inst:{m_verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "stmt-pair"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        if s2.drive_returns:
            lines.append(f"$_ret = $_inst->{m_drive}({drive_arg_str});")
        else:
            lines.append(f"$_inst->{m_drive}({drive_arg_str});")
            lines.append(f"$_ret = $_inst->{m_verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "stmt-pair"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        if s2.drive_returns:
            lines.append(f"    final _ret = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str});")
            lines.append(f"    final _ret = _inst.{m_verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        if s2.drive_returns:
            lines.append(f"    let _ret = _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str});")
            lines.append(f"    let _ret = _inst.{m_verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
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
        if s2.drive_returns:
            lines.append(f"    ret := sm.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"    sm.{m_drive}({drive_arg_str})")
            lines.append(f"    ret := sm.{m_verify}()")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        if s2.drive_returns:
            lines.append(f"let _ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"_inst.{m_drive}({drive_arg_str})")
            lines.append(f"let _ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "stmt-pair"))
    elif lang == "java":
        # Mirror gen_perm.py: package-private `class Driver`,
        # package prepended via sed in batch_java.
        lines.append(f"class Driver {{")
        lines.append(f"    public static void main(String[] args) {{")
        lines.append(f"        var _inst = new {sys_name}();")
        if s2.drive_returns:
            lines.append(f"        int _ret = (int) _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"        _inst.{m_drive}({drive_arg_str});")
            lines.append(f"        int _ret = (int) _inst.{m_verify}();")
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{cid}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        if s2.drive_returns:
            lines.append(f"    val _ret = _inst.{m_drive}({drive_arg_str}) as Int")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str})")
            lines.append(f"    val _ret = _inst.{m_verify}() as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        if s2.drive_returns:
            lines.append(f"            int _ret = (int) _inst.{m_drive}({drive_arg_str});")
        else:
            lines.append(f"            _inst.{m_drive}({drive_arg_str});")
            lines.append(f"            int _ret = (int) _inst.{m_verify}();")
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        if s2.drive_returns:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_drive}(_inst, {drive_arg_str});")
        else:
            lines.append(f"    {sys_name}_{m_drive}(_inst, {drive_arg_str});")
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_verify}(_inst);")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        if s2.drive_returns:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_drive}({drive_arg_str}));")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str});")
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_verify}());")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        if s2.drive_returns:
            lines.append(f"    var _ret = _inst.{m_drive}({drive_arg_str})")
        else:
            lines.append(f"    _inst.{m_drive}({drive_arg_str})")
            lines.append(f"    var _ret = _inst.{m_verify}()")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'stmt-pair')}")
        lines.append("    quit()")
    elif lang == "erlang":
        # Erlang external escript driver — same pattern as Phase 10.
        # Metadata is embedded in source comments above and the
        # runner generates the escript from FUZZ_* lines.
        pass

    return "\n".join(lines)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir",
                        default=str(Path(__file__).parent / "cases_stmt_pair"))
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
        for cid, equiv, expected, s1, s2, lit, is_smoke in enumerate_cases():
            src = gen_case(lang, cid, equiv, expected, s1, s2, lit, is_smoke)
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

    print(f"generated {cases_per_lang} cases × {len(args.langs)} langs into {out}")
    for lang, cnt in smoke_count_by_lang.items():
        print(f"  {lang}: {cases_per_lang} cases, {cnt} smoke")


if __name__ == "__main__":
    main()
