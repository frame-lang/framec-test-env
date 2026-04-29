#!/usr/bin/env python3
"""
Phase 12 — control-flow embedding fuzz (Wave 1).

Frame supports native `if cond { body }` inside handler bodies via
the Oceans Model — the cond is per-target native syntax and the
body can mix native code with Frame statements (`@@:return = ...`,
`-> $S1`, `@@:self.method()`). This phase pins that contract:
does framec correctly emit the body's Frame statements regardless
of whether they're nested inside a control-flow construct?

What this exercises that earlier phases don't:
- Frame statements inside native if-bodies (transitions, self-
  calls, return-writes, dom/sv writes).
- Per-language if-syntax variation: indent (Python/GDScript),
  braces with parens (JS/TS/Java/C/C++/C#/PHP), braces no parens
  (Rust/Go/Kotlin/Swift/Dart), end-keyword (Ruby/Lua).
- Cond expressions reading domain fields.

Wave 1 design:
  Cond shapes (4):  lit_true, lit_false, dom_eq_K, dom_arith_eq_K
  Body shapes (5):  dom_w, sv_w, ret_w, sc_assign_dom, transition
  LIT values (5):   1, 5, -3, 0, 100
  Total: 4 × 5 × 5 = 100 cases per lang.

Erlang is excluded from Wave 1 — its `if X -> body ; true -> body
end` syntax is structurally too different to share a renderer with
the other 16 langs. Wave 2 candidate.

Smoke filter: one case per (cond, body) pair (LIT=1) → 20 smoke
cases per lang.

Usage:
    python3 gen_ctrl_flow.py
    python3 gen_ctrl_flow.py --langs python_3
    ./run_ctrl_flow.sh --tier=smoke --lang=python_3
"""
import argparse
from pathlib import Path

from gen_nested import LANGS, method_name


# Domain seeds. f starts at 5 so dom_eq_K with K=5 fires the if-true
# branch and K!=5 fires the if-false branch. The simulator folds
# these constants through.
DOMAIN_F_INIT = 5
SV_S_INIT = 0
COMPUTE_RETURN = 9   # @@:self.compute() returns this.

# K_HIT is the literal that, paired with `self.f == K_HIT`, makes
# the cond evaluate true. K_MISS makes it false.
K_HIT = DOMAIN_F_INIT
K_MISS = DOMAIN_F_INIT + 1

LIT_VALUES = [1, 5, -3, 0, 100]


# ---------------------------------------------------------------------
# If-syntax renderers, per language. Each takes `(cond, body)` (the
# body is a single Frame statement string already terminated as
# appropriate for the language), and returns the source text for
# `if cond { body }`.
#
# `indent` is the leading indent of the if-construct itself (16
# spaces inside a handler body). Body lines are indented +4 more.
# ---------------------------------------------------------------------

INDENT = " " * 16
BODY_INDENT = " " * 20


def _if_python(cond, body):
    # Python: `if X:\n    body`. No else for v1.
    return f"{INDENT}if {cond}:\n{BODY_INDENT}{body}"


def _if_gdscript(cond, body):
    return f"{INDENT}if {cond}:\n{BODY_INDENT}{body}"


def _if_js(cond, body):
    return f"{INDENT}if ({cond}) {{\n{BODY_INDENT}{body}\n{INDENT}}}"


def _if_typescript(cond, body):
    return _if_js(cond, body)


def _if_java(cond, body):
    return _if_js(cond, body)


def _if_c(cond, body):
    return _if_js(cond, body)


def _if_cpp(cond, body):
    return _if_js(cond, body)


def _if_csharp(cond, body):
    return _if_js(cond, body)


def _if_php(cond, body):
    return _if_js(cond, body)


def _if_rust(cond, body):
    # Rust: `if cond { body }` (no parens around cond).
    return f"{INDENT}if {cond} {{\n{BODY_INDENT}{body}\n{INDENT}}}"


def _if_go(cond, body):
    return _if_rust(cond, body)


def _if_kotlin(cond, body):
    # Kotlin requires parens around the cond.
    return _if_js(cond, body)


def _if_swift(cond, body):
    return _if_rust(cond, body)


def _if_dart(cond, body):
    return _if_js(cond, body)  # Dart uses parens.


def _if_ruby(cond, body):
    # Ruby: `if cond\n  body\nend`.
    return f"{INDENT}if {cond}\n{BODY_INDENT}{body}\n{INDENT}end"


def _if_lua(cond, body):
    # Lua: `if cond then body end`.
    return f"{INDENT}if {cond} then\n{BODY_INDENT}{body}\n{INDENT}end"


IF_RENDERERS = {
    "python_3": _if_python,
    "javascript": _if_js,
    "typescript": _if_typescript,
    "ruby": _if_ruby,
    "lua": _if_lua,
    "php": _if_php,
    "dart": _if_dart,
    "rust": _if_rust,
    "go": _if_go,
    "swift": _if_swift,
    "java": _if_java,
    "kotlin": _if_kotlin,
    "csharp": _if_csharp,
    "c": _if_c,
    "cpp": _if_cpp,
    "gdscript": _if_gdscript,
}

WAVE1_LANGS = list(IF_RENDERERS.keys())   # 16; Erlang excluded.


# ---------------------------------------------------------------------
# Cond shapes — per-language render of the cond expression.
# ---------------------------------------------------------------------

class CondShape:
    __slots__ = ("name", "render", "is_true")

    def __init__(self, name, render, is_true):
        self.name = name
        self.render = render            # lambda(spec): str
        self.is_true = is_true          # bool — known truth value


def _cond_lit_true(spec):
    return "1 == 1"


def _cond_lit_false(spec):
    return "1 == 2"


def _cond_dom_eq_hit(spec):
    return f"{spec.self_word}{spec.field_op}f == {K_HIT}"


def _cond_dom_arith_eq_hit(spec):
    return f"{spec.self_word}{spec.field_op}f + 1 == {K_HIT + 1}"


CONDS = [
    CondShape("lit_true", _cond_lit_true, True),
    CondShape("lit_false", _cond_lit_false, False),
    CondShape("dom_eq_hit", _cond_dom_eq_hit, True),
    CondShape("dom_arith_eq_hit", _cond_dom_arith_eq_hit, True),
]


# ---------------------------------------------------------------------
# Body shapes — Frame source for the then-body. Body is a SINGLE
# Frame statement; for transitions there's no statement terminator.
# ---------------------------------------------------------------------

class BodyShape:
    __slots__ = ("name", "drive_returns", "verify_method",
                 "render", "post_dom", "post_sv", "post_ret",
                 "transitions")

    def __init__(self, name, drive_returns, verify_method, render,
                 post_dom, post_sv, post_ret, transitions=False):
        self.name = name
        self.drive_returns = drive_returns
        self.verify_method = verify_method
        self.render = render            # lambda(spec, lang, sys, lit): str (no stmt_end)
        self.post_dom = post_dom
        self.post_sv = post_sv
        self.post_ret = post_ret
        self.transitions = transitions  # if True, body fires a transition;
                                        # cases with transitions can't easily
                                        # verify drive return so we use get_n.


def _body_dom_w(spec, lang, sys, lit):
    return f"{spec.self_word}{spec.field_op}f = {lit}"


def _body_sv_w(spec, lang, sys, lit):
    return "$.s = " + str(lit)


def _body_ret_w(spec, lang, sys, lit):
    return f"@@:return = {lit}"


def _body_sc_assign_dom(spec, lang, sys, lit):
    m = method_name(lang, "compute")
    return f"{spec.self_word}{spec.field_op}f = @@:self.{m}()"


def _body_transition(spec, lang, sys, lit):
    return "-> $S1"


BODIES = [
    BodyShape("dom_w", False, "get_n", _body_dom_w,
              lambda s, lit: lit, None, None),
    BodyShape("sv_w", False, "get_scache", _body_sv_w,
              None, lambda s, lit: lit, None),
    BodyShape("ret_w", True, "drive", _body_ret_w,
              None, None, lambda s, lit: lit),
    BodyShape("sc_assign_dom", False, "get_n", _body_sc_assign_dom,
              lambda s, lit: COMPUTE_RETURN, None, None),
    BodyShape("transition", False, "get_n", _body_transition,
              None, None, None, transitions=True),
]


# ---------------------------------------------------------------------
# Simulator
# ---------------------------------------------------------------------

# Sentinel pre-init for ret slot. When body=ret_w and cond=false,
# the body is skipped; the unwritten return slot's default differs
# per language (None/null/0/undefined). Pre-initializing to RET_SENTINEL
# in handler line #1 makes the post-state predictable across all langs.
RET_SENTINEL = -777


def simulate(cond, body, lit):
    """Compute the value the driver should observe."""
    # ret slot: if body is ret_w we pre-init to RET_SENTINEL; else
    # we don't need a starting value (no body here writes ret).
    ret_init = RET_SENTINEL if body.name == "ret_w" else 0
    state = {"dom": DOMAIN_F_INIT, "sv": SV_S_INIT, "ret": ret_init}
    if cond.is_true:
        if body.post_dom is not None:
            state["dom"] = body.post_dom(state, lit)
        if body.post_sv is not None:
            state["sv"] = body.post_sv(state, lit)
        if body.post_ret is not None:
            state["ret"] = body.post_ret(state, lit)
    if body.drive_returns:
        return state["ret"]
    if body.verify_method == "get_n":
        return state["dom"]
    if body.verify_method == "get_scache":
        return state["sv"]
    raise ValueError(f"unhandled verify_method {body.verify_method}")


def case_id(cond, body, lit):
    sign = "n" if lit < 0 else ""
    return f"cf_{cond.name}__{body.name}__lit{sign}{abs(lit)}"


def equiv_class(cond, body):
    return f"{cond.name}__{body.name}"


def enumerate_cases():
    seen_classes = set()
    for cond in CONDS:
        for body in BODIES:
            for lit in LIT_VALUES:
                cid = case_id(cond, body, lit)
                cls = equiv_class(cond, body)
                is_smoke = cls not in seen_classes
                if is_smoke:
                    seen_classes.add(cls)
                expected = simulate(cond, body, lit)
                yield (cid, cls, expected, cond, body, lit, is_smoke)


# ---------------------------------------------------------------------
# Per-language case emission. Largely mirrors gen_perm.py /
# gen_stmt_pair.py — drive returns int when body writes ret slot,
# else returns void and verification reads dom/sv via get_n /
# get_scache.
# ---------------------------------------------------------------------

def gen_case(lang, cid, equiv, expected, cond, body, lit, is_smoke):
    spec = LANGS[lang]
    sys_name = f"CtrlFlow_{cid}"

    m_drive = method_name(lang, "drive")
    m_compute = method_name(lang, "compute")
    m_get_n = method_name(lang, "get_n")
    m_get_scache = method_name(lang, "get_scache")
    m_verify = m_drive if body.drive_returns else (
        m_get_n if body.verify_method == "get_n" else m_get_scache
    )

    drive_sig = (
        f"{m_drive}(): int" if body.drive_returns
        else f"{m_drive}()"
    )

    cond_src = cond.render(spec)
    body_src = body.render(spec, lang, sys_name, lit)
    if body.transitions:
        # Transition target must be declared. Generated body is a
        # bare `-> $S1`; no stmt_end.
        body_terminated = body_src
    else:
        body_terminated = body_src + spec.stmt_end

    if_construct = IF_RENDERERS[lang](cond_src, body_terminated)

    lines = []
    lines.append(f"@@target {spec.target}")
    if lang == "php":
        lines.append("<?php")
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
    if body.name == "ret_w":
        # Pre-init return slot so the false-cond branch is observable
        # uniformly across langs (see RET_SENTINEL comment).
        lines.append(f"                @@:return = {RET_SENTINEL}{spec.stmt_end}")
    lines.append(if_construct)
    lines.append(f"            }}")
    lines.append(f"            {m_compute}(): int {{ @@:({COMPUTE_RETURN}) }}")
    lines.append(f"            {m_get_n}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}")
    lines.append(f"            {m_get_scache}(): int {{ @@:($.s) }}")
    lines.append("        }")
    if body.transitions:
        # $S1 must implement get_n so post-transition driver verify
        # works. State vars are state-scoped — $S1 can't read $S0's
        # `$.s`. The transition body's verify_method is always
        # `get_n` (domain read), so we only emit that handler.
        lines.append("        $S1 {")
        lines.append(f"            {m_get_n}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}")
        lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = {DOMAIN_F_INIT}")
    lines.append("}")
    lines.append("")

    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        if body.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}()")
        else:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"_ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if body.drive_returns:
            lines.append(f"const _ret = _inst.{m_drive}();")
        else:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        if body.drive_returns:
            lines.append(f"const _ret: number = _inst.{m_drive}();")
        else:
            lines.append(f"_inst.{m_drive}();")
            lines.append(f"const _ret: number = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        if body.drive_returns:
            lines.append(f"_ret = _inst.{m_drive}")
        else:
            lines.append(f"_inst.{m_drive}")
            lines.append(f"_ret = _inst.{m_verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        if body.drive_returns:
            lines.append(f"local _ret = _inst:{m_drive}()")
        else:
            lines.append(f"_inst:{m_drive}()")
            lines.append(f"local _ret = _inst:{m_verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        if body.drive_returns:
            lines.append(f"$_ret = $_inst->{m_drive}();")
        else:
            lines.append(f"$_inst->{m_drive}();")
            lines.append(f"$_ret = $_inst->{m_verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        if body.drive_returns:
            lines.append(f"    final _ret = _inst.{m_drive}();")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    final _ret = _inst.{m_verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        if body.drive_returns:
            lines.append(f"    let _ret = _inst.{m_drive}();")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    let _ret = _inst.{m_verify}();")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
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
        if body.drive_returns:
            lines.append(f"    ret := sm.{m_drive}()")
        else:
            lines.append(f"    sm.{m_drive}()")
            lines.append(f"    ret := sm.{m_verify}()")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        if body.drive_returns:
            lines.append(f"let _ret = _inst.{m_drive}()")
        else:
            lines.append(f"_inst.{m_drive}()")
            lines.append(f"let _ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = new {sys_name}();")
        if body.drive_returns:
            lines.append(f"        int _ret = (int) _inst.{m_drive}();")
        else:
            lines.append(f"        _inst.{m_drive}();")
            lines.append(f"        int _ret = (int) _inst.{m_verify}();")
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{cid}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        if body.drive_returns:
            lines.append(f"    val _ret = _inst.{m_drive}() as Int")
        else:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    val _ret = _inst.{m_verify}() as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        if body.drive_returns:
            lines.append(f"            int _ret = (int) _inst.{m_drive}();")
        else:
            lines.append(f"            _inst.{m_drive}();")
            lines.append(f"            int _ret = (int) _inst.{m_verify}();")
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        if body.drive_returns:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_drive}(_inst);")
        else:
            lines.append(f"    {sys_name}_{m_drive}(_inst);")
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_verify}(_inst);")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        if body.drive_returns:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_drive}());")
        else:
            lines.append(f"    _inst.{m_drive}();")
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_verify}());")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        if body.drive_returns:
            lines.append(f"    var _ret = _inst.{m_drive}()")
        else:
            lines.append(f"    _inst.{m_drive}()")
            lines.append(f"    var _ret = _inst.{m_verify}()")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("    quit()")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir",
                        default=str(Path(__file__).parent / "cases_ctrl_flow"))
    parser.add_argument("--langs", nargs="+", default=WAVE1_LANGS)
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*"):
        f.unlink()

    index_rows = ["lang\tcase_id\tequiv_class\tsmoke\texpected"]
    smoke_count_by_lang = {}
    cases_per_lang = 0
    for lang in args.langs:
        if lang not in IF_RENDERERS:
            print(f"  skipping {lang}: no if-renderer (Erlang excluded for v1)")
            continue
        spec = LANGS[lang]
        smoke_count = 0
        per_lang = 0
        for cid, equiv, expected, cond, body, lit, is_smoke in enumerate_cases():
            src = gen_case(lang, cid, equiv, expected, cond, body, lit, is_smoke)
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
