#!/usr/bin/env python3
"""
Phase 13 — identifier shadowing fuzz (Wave 1).

Same identifier `x` is declared in three scopes simultaneously:
- domain field: `self.x` / `this.x` / etc.
- state-var: `$.x`
- handler param: `x` (passed to drive)

Different read syntaxes resolve to different scopes. This phase
pins framec's scope resolution: when you write `self.x`, you get
the domain field, not the state-var; when you write `$.x`, you get
the state-var, not the param; when you write the unqualified `x`
inside the handler, you get the param. Cross-slot reads in the
same expression (`self.x + $.x + x`) must compose correctly.

Wave 1 design:
  Shapes (10):    different read combinations
  Value tuples (10): (dom_x, sv_x, param_x, LIT) per case
  Total: 10 × 10 = 100 cases per lang × 17 langs = 1,700.

Smoke filter: one case per shape (first value tuple) → 10 smoke
cases per lang.

Usage:
    python3 gen_shadow.py
    python3 gen_shadow.py --langs python_3
    ./run_shadow.sh --tier=smoke --lang=python_3
"""
import argparse
from pathlib import Path

from gen_nested import LANGS, method_name


# ---------------------------------------------------------------------
# Shapes — each defines the read expression as a per-language string
# and a simulator function that computes the expected return given
# (dom_x, sv_x, param_x, lit).
# ---------------------------------------------------------------------

class Shape:
    __slots__ = ("name", "render", "compute")

    def __init__(self, name, render, compute):
        self.name = name
        self.render = render        # lambda(spec, lang, lit): str
        self.compute = compute      # lambda(dom_x, sv_x, param_x, lit): int


def _r_self_x(spec, lang, lit):
    return f"{spec.self_word}{spec.field_op}x"


def _r_sv_x(spec, lang, lit):
    return "$.x"


def _r_param_x(spec, lang, lit):
    # Frame-level reference to the handler param. PHP needs `$x`.
    return f"{spec.param_prefix}x"


def _r_params_obj_x(spec, lang, lit):
    # @@:params.x — Frame's params-object access (same syntax all langs).
    return "@@:params.x"


SHAPES = [
    Shape("self_only", _r_self_x,
          lambda d, s, p, lit: d),
    Shape("sv_only", _r_sv_x,
          lambda d, s, p, lit: s),
    Shape("param_only", _r_param_x,
          lambda d, s, p, lit: p),
    Shape("params_obj_only", _r_params_obj_x,
          lambda d, s, p, lit: p),
    Shape("self_plus_sv",
          lambda spec, lang, lit: f"{_r_self_x(spec, lang, lit)} + {_r_sv_x(spec, lang, lit)}",
          lambda d, s, p, lit: d + s),
    Shape("self_plus_param",
          lambda spec, lang, lit: f"{_r_self_x(spec, lang, lit)} + {_r_param_x(spec, lang, lit)}",
          lambda d, s, p, lit: d + p),
    Shape("sv_plus_param",
          lambda spec, lang, lit: f"{_r_sv_x(spec, lang, lit)} + {_r_param_x(spec, lang, lit)}",
          lambda d, s, p, lit: s + p),
    Shape("all_three",
          lambda spec, lang, lit: f"{_r_self_x(spec, lang, lit)} + {_r_sv_x(spec, lang, lit)} + {_r_param_x(spec, lang, lit)}",
          lambda d, s, p, lit: d + s + p),
    Shape("self_plus_lit",
          lambda spec, lang, lit: f"{_r_self_x(spec, lang, lit)} + {lit}",
          lambda d, s, p, lit: d + lit),
    Shape("self_minus_sv_plus_param",
          lambda spec, lang, lit: f"{_r_self_x(spec, lang, lit)} - {_r_sv_x(spec, lang, lit)} + {_r_param_x(spec, lang, lit)}",
          lambda d, s, p, lit: d - s + p),
]


# ---------------------------------------------------------------------
# Value tuples — 10 (dom_x, sv_x, param_x, lit) combinations chosen
# to exercise sign/zero edges and minimize coincidental equality.
# ---------------------------------------------------------------------

VALUE_TUPLES = [
    # (dom_x, sv_x, param_x, lit) — drive(x=param_x) and verify.
    (100, 200, 300, 1),
    (100, 200, 300, 0),
    (100, 200, 300, -1),
    (-50, 7, 1, 5),
    (0, 0, 0, 0),
    (1, -1, 1, -1),
    (999, 42, 13, 100),
    (7, -1, 5, 0),
    (1, 1, 1, 1),
    (-1, -1, -1, -1),
]


def case_id(shape, vt_idx):
    return f"sh_{shape.name}__t{vt_idx}"


def equiv_class(shape):
    return shape.name


def enumerate_cases():
    seen = set()
    for shape in SHAPES:
        for idx, vt in enumerate(VALUE_TUPLES):
            cid = case_id(shape, idx)
            cls = equiv_class(shape)
            is_smoke = cls not in seen
            if is_smoke:
                seen.add(cls)
            dom_x, sv_x, param_x, lit = vt
            expected = shape.compute(dom_x, sv_x, param_x, lit)
            yield (cid, cls, expected, shape, vt, is_smoke)


# ---------------------------------------------------------------------
# Per-language case emission. Same boilerplate shape as Phase 11/12;
# only the handler body differs.
# ---------------------------------------------------------------------

def gen_case(lang, cid, equiv, expected, shape, vt, is_smoke):
    spec = LANGS[lang]
    sys_name = f"Shadow_{cid}"
    dom_x, sv_x, param_x, lit = vt

    m_drive = method_name(lang, "drive")
    m_get_x = method_name(lang, "get_x")
    m_get_sx = method_name(lang, "get_sx")

    drive_sig = f"{m_drive}(x: int): int"
    expr = shape.render(spec, lang, lit)

    lines = []
    lines.append(f"@@target {spec.target}")
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        lines.append(f"%% FUZZ_DRIVE_ARG: {param_x}")
        lines.append(f"%% FUZZ_VERIFY_METHOD: {m_drive}")
        lines.append(f"%% FUZZ_DRIVE_RETURNS: yes")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append(f"        {drive_sig}")
    lines.append(f"        {m_get_x}(): int")
    lines.append(f"        {m_get_sx}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $S0 {")
    lines.append(f"            $.x: int = {sv_x}")
    lines.append(f"            {drive_sig} {{")
    lines.append(f"                @@:return = {expr}{spec.stmt_end}")
    lines.append(f"            }}")
    lines.append(f"            {m_get_x}(): int {{ @@:({spec.self_word}{spec.field_op}x) }}")
    lines.append(f"            {m_get_sx}(): int {{ @@:($.x) }}")
    lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        x: int = {dom_x}")
    lines.append("}")
    lines.append("")

    drive_arg_str = str(param_x)
    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}()")
        lines.append(f"_ret = _inst.{m_drive}({drive_arg_str})")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "shadow"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        lines.append(f"const _ret = _inst.{m_drive}({drive_arg_str});")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "shadow"))
    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        lines.append(f"const _ret: number = _inst.{m_drive}({drive_arg_str});")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "shadow"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        lines.append(f"_ret = _inst.{m_drive}({drive_arg_str})")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "shadow"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        lines.append(f"local _ret = _inst:{m_drive}({drive_arg_str})")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "shadow"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        lines.append(f"$_ret = $_inst->{m_drive}({drive_arg_str});")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "shadow"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        lines.append(f"    final _ret = _inst.{m_drive}({drive_arg_str});")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        lines.append(f"    let _ret = _inst.{m_drive}({drive_arg_str});")
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'shadow')}")
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
        lines.append(f"    ret := sm.{m_drive}({drive_arg_str})")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        lines.append(f"let _ret = _inst.{m_drive}({drive_arg_str})")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "shadow"))
    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = new {sys_name}();")
        lines.append(f"        int _ret = (int) _inst.{m_drive}({drive_arg_str});")
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("    }")
        lines.append("}")
    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{cid}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        lines.append(f"    val _ret = _inst.{m_drive}({drive_arg_str}) as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        lines.append(f"            int _ret = (int) _inst.{m_drive}({drive_arg_str});")
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_drive}(_inst, {drive_arg_str});")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_drive}({drive_arg_str}));")
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("    return 0;")
        lines.append("}")
    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        lines.append(f"    var _ret = _inst.{m_drive}({drive_arg_str})")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'shadow')}")
        lines.append("    quit()")
    elif lang == "erlang":
        pass

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir",
                        default=str(Path(__file__).parent / "cases_shadow"))
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
        for cid, equiv, expected, shape, vt, is_smoke in enumerate_cases():
            src = gen_case(lang, cid, equiv, expected, shape, vt, is_smoke)
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
