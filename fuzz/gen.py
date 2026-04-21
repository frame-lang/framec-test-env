#!/usr/bin/env python3
"""
Structural fuzzer for framec.

Generates small Frame systems varying structural dimensions and emits one
case per target language per configuration. The companion run.sh transpiles,
syntax-checks, and (where possible) builds each to surface codegen bugs.

Design principle: **every generated Frame source must be syntactically valid
for its target language**. The generator embeds target-native syntax for
control flow, instance-member access, literals, and no-op statements. This
means issues the fuzzer surfaces are framec codegen issues, not artifacts of
fuzz-generator laziness.

Structural axes (random-sampled to --max combinations, default 500):
    state count        : 2, 3, 5, 8
    HSM depth          : flat / 2-level / 3-level / 4-level
    push$/pop$         : on/off
    state variables    : on/off
    enter/exit handlers: on/off
    enter args         : on/off (only with HSM)
    action body kind   : none / assign / if / nested if
    handler body kind  : simple / conditional / nested if / forward (=> $^)
    return type        : void / str / int

Adding a language: add an entry to LANGS with its syntax flavor. The runner
gets a corresponding compile_check arm in run.sh.

Usage:
    python3 gen.py [--max N] [--lang <ext>] [--seed N]
"""
import argparse
import itertools
import random
from pathlib import Path

# --- Structural axes -----------------------------------------------------

STATE_COUNTS = [2, 3, 5, 8]
HSM_DEPTHS   = [0, 1, 2, 3]
PUSH_POP     = [False, True]
STATE_VARS   = [False, True]
ENTER_EXIT   = [False, True]
ENTER_ARGS   = [False, True]
ACTION_BODY  = ["none", "assign", "if", "nested_if"]
HANDLER_BODY = ["simple", "cond", "nested_if", "forward"]
RETURN_TYPE  = ["void", "str", "int"]

# --- Per-language syntax configuration -----------------------------------
#
# A LangSpec carries every piece of target-language syntax the generator
# needs. The four `if_style` flavors:
#
#   "colon"       (Python, GDScript)
#       if X:
#           body
#
#   "brace"       (Rust, Go, Erlang, Swift)
#       if X {
#           body
#       }
#
#   "paren_brace" (C, C++, Java, C#, Kotlin, Dart, PHP, TypeScript, JavaScript)
#       if (X) {
#           body
#       }
#
#   "keyword_end" (Ruby, Lua — slightly different keyword)
#       if X [then]
#           body
#       end
#
# `self_x` is the textual form of `self.x` in native code for that target.
# `stmt_end` is what ends each statement line (empty for languages that
# don't use statement terminators). `noop_stmt` is a valid do-nothing
# statement that can be safely placed in a body position.

class LangSpec:
    __slots__ = (
        "target", "ext",
        "int_type", "str_type", "bool_type",
        "int_default", "str_default", "bool_default",
        "str_lit", "self_x",
        "stmt_end", "stmt_sep",
        "if_style", "if_then_sep",
        "noop_stmt",
        "prolog",  # raw native-code prolog prepended before @@system
    )
    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k, "") if k == "prolog" else kw.get(k))


def _lua_str_lit(s): return f'"{s}"'
def _cpp_str_lit(s): return f'std::string("{s}")'
def _rust_str_lit(s): return f'"{s}".to_string()'

LANGS = {
    # ext  -> LangSpec
    "fpy": LangSpec(
        target="python_3",  ext="fpy",
        int_type="int",     str_type="str",     bool_type="bool",
        int_default="0",    str_default='""',   bool_default="False",
        str_lit=lambda s: f'"{s}"',             self_x="self.x",
        stmt_end="",        stmt_sep="",
        if_style="colon",   if_then_sep="",
        noop_stmt="pass",
    ),
    "fgd": LangSpec(
        target="gdscript",  ext="fgd",
        int_type="int",     str_type="str",     bool_type="bool",
        int_default="0",    str_default='""',   bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="self.x",
        stmt_end="",        stmt_sep="",
        if_style="colon",   if_then_sep="",
        noop_stmt="pass",
    ),
    "fts": LangSpec(
        target="typescript", ext="fts",
        int_type="number",   str_type="string", bool_type="boolean",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="this.x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "fjs": LangSpec(
        target="javascript", ext="fjs",
        int_type="number",   str_type="string", bool_type="boolean",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="this.x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "frs": LangSpec(
        target="rust",       ext="frs",
        int_type="i32",      str_type="String", bool_type="bool",
        int_default="0",     str_default='"".to_string()', bool_default="false",
        str_lit=_rust_str_lit,                  self_x="self.x",
        stmt_end=";",        stmt_sep="",
        if_style="brace",    if_then_sep="",
        noop_stmt="",
    ),
    "fc": LangSpec(
        target="c",          ext="fc",
        int_type="int",      str_type="char*",  bool_type="int",
        int_default="0",     str_default='""',  bool_default="0",
        str_lit=lambda s: f'"{s}"',             self_x="self->x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "fcpp": LangSpec(
        target="cpp_23",     ext="fcpp",
        int_type="int",      str_type="std::string", bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=_cpp_str_lit,                   self_x="this->x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "fcs": LangSpec(
        target="csharp",     ext="fcs",
        int_type="int",      str_type="string", bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="this.x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "fjava": LangSpec(
        target="java",       ext="fjava",
        int_type="int",      str_type="String", bool_type="boolean",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="this.x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "fkt": LangSpec(
        target="kotlin",     ext="fkt",
        int_type="Int",      str_type="String", bool_type="Boolean",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="this.x",
        stmt_end="",         stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "fswift": LangSpec(
        target="swift",      ext="fswift",
        int_type="Int",      str_type="String", bool_type="Bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="self.x",
        stmt_end="",         stmt_sep="",
        if_style="brace",    if_then_sep="",
        noop_stmt="",
    ),
    "fgo": LangSpec(
        target="go",         ext="fgo",
        int_type="int",      str_type="string", bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="s.x",
        stmt_end="",         stmt_sep="",
        if_style="brace",    if_then_sep="",
        # Go vet warns on `s.x = s.x` as self-assignment; use a blank-
        # identifier read instead, which is syntactically valid and
        # semantically a no-op.
        noop_stmt="_ = s.x",
        # Go is a "whole file" language — framec needs the `package main`
        # declaration to live in the prolog region (Oceans Model: native
        # code outside @@system passes through verbatim). Without it, the
        # emitted file is a fragment, not a compilable translation unit.
        prolog="package main\n",
    ),
    "fphp": LangSpec(
        target="php",        ext="fphp",
        int_type="int",      str_type="string", bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="$this->x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "frb": LangSpec(
        target="ruby",       ext="frb",
        int_type="int",      str_type="str",    bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="@x",
        stmt_end="",         stmt_sep="",
        if_style="keyword_end", if_then_sep="",
        noop_stmt="nil",
    ),
    "flua": LangSpec(
        target="lua",        ext="flua",
        int_type="int",      str_type="str",    bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=_lua_str_lit,                   self_x="self.x",
        stmt_end="",         stmt_sep="",
        if_style="keyword_end", if_then_sep="then",
        noop_stmt="",
    ),
    "fdart": LangSpec(
        target="dart",       ext="fdart",
        int_type="int",      str_type="String", bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="this.x",
        stmt_end=";",        stmt_sep="",
        if_style="paren_brace", if_then_sep="",
        noop_stmt="",
    ),
    "ferl": LangSpec(
        target="erlang",     ext="ferl",
        int_type="int",      str_type="str",    bool_type="bool",
        int_default="0",     str_default='""',  bool_default="false",
        str_lit=lambda s: f'"{s}"',             self_x="self.x",
        stmt_end="",         stmt_sep=",",
        if_style="brace",    if_then_sep="",
        noop_stmt="ok",
    ),
}


# --- If-statement rendering ----------------------------------------------
#
# Each target language has its own idea of how an if/else chain looks. We
# render a two- or three-arm if here; callers must be able to reason about
# which arm a transition or `@@:(...)` goes in.

def render_if_two_arm(spec, cond, then_stmt, else_stmt, outer_indent):
    """Render `if cond { then } else { else }` in the target language.

    `outer_indent` is applied uniformly to the `if` line, the `else` line,
    and the closing `}`/`end`. Body lines are one step (4 spaces) deeper.
    The returned string is complete — the first line already carries the
    opening indent, so callers should append it directly without adding
    any further prefix.
    """
    body_indent = outer_indent + "    "
    if spec.if_style == "colon":
        return (
            f"{outer_indent}if {cond}:\n"
            f"{body_indent}{then_stmt}\n"
            f"{outer_indent}else:\n"
            f"{body_indent}{else_stmt}\n"
        )
    if spec.if_style == "brace":
        return (
            f"{outer_indent}if {cond} {{\n"
            f"{body_indent}{then_stmt}\n"
            f"{outer_indent}}} else {{\n"
            f"{body_indent}{else_stmt}\n"
            f"{outer_indent}}}\n"
        )
    if spec.if_style == "paren_brace":
        return (
            f"{outer_indent}if ({cond}) {{\n"
            f"{body_indent}{then_stmt}\n"
            f"{outer_indent}}} else {{\n"
            f"{body_indent}{else_stmt}\n"
            f"{outer_indent}}}\n"
        )
    if spec.if_style == "keyword_end":
        then_kw = f" {spec.if_then_sep}" if spec.if_then_sep else ""
        return (
            f"{outer_indent}if {cond}{then_kw}\n"
            f"{body_indent}{then_stmt}\n"
            f"{outer_indent}else\n"
            f"{body_indent}{else_stmt}\n"
            f"{outer_indent}end\n"
        )
    raise ValueError(spec.if_style)


def render_if_three_arm(spec, cond_a, stmt_a, cond_b, stmt_b, stmt_c,
                        outer_indent):
    """Render three-arm if: `if A { a } elif B { b } else { c }`.

    Complete with first-line indent baked in — see render_if_two_arm."""
    body_indent = outer_indent + "    "
    if spec.if_style == "colon":
        return (
            f"{outer_indent}if {cond_a}:\n"
            f"{body_indent}{stmt_a}\n"
            f"{outer_indent}elif {cond_b}:\n"
            f"{body_indent}{stmt_b}\n"
            f"{outer_indent}else:\n"
            f"{body_indent}{stmt_c}\n"
        )
    if spec.if_style == "brace":
        return (
            f"{outer_indent}if {cond_a} {{\n"
            f"{body_indent}{stmt_a}\n"
            f"{outer_indent}}} else if {cond_b} {{\n"
            f"{body_indent}{stmt_b}\n"
            f"{outer_indent}}} else {{\n"
            f"{body_indent}{stmt_c}\n"
            f"{outer_indent}}}\n"
        )
    if spec.if_style == "paren_brace":
        return (
            f"{outer_indent}if ({cond_a}) {{\n"
            f"{body_indent}{stmt_a}\n"
            f"{outer_indent}}} else if ({cond_b}) {{\n"
            f"{body_indent}{stmt_b}\n"
            f"{outer_indent}}} else {{\n"
            f"{body_indent}{stmt_c}\n"
            f"{outer_indent}}}\n"
        )
    if spec.if_style == "keyword_end":
        then_kw = f" {spec.if_then_sep}" if spec.if_then_sep else ""
        elif_kw = "elsif" if spec.target == "ruby" else "elseif"
        return (
            f"{outer_indent}if {cond_a}{then_kw}\n"
            f"{body_indent}{stmt_a}\n"
            f"{outer_indent}{elif_kw} {cond_b}{then_kw}\n"
            f"{body_indent}{stmt_b}\n"
            f"{outer_indent}else\n"
            f"{body_indent}{stmt_c}\n"
            f"{outer_indent}end\n"
        )
    raise ValueError(spec.if_style)


# --- Handler and action body generation ----------------------------------

def _return_stmt(spec, ret_type, seed):
    """`@@:(literal)` for non-void, empty string for void."""
    if ret_type == "void":
        return ""
    if ret_type == "int":
        return f"@@:({seed})"
    return f"@@:({spec.str_lit(f'v{seed}')})"


def _leaf_stmt(spec, ret_type, seed):
    """A valid non-empty leaf statement: `@@:(...)` when there's a return
    type, otherwise a target-appropriate no-op that doesn't trip linters.

    This avoids `{}` (invalid in Swift), bare `;` (lint noise), self-
    assignment (Go vet flags `s.x = s.x`), and empty statements (Python
    indent errors).
    """
    ret = _return_stmt(spec, ret_type, seed)
    if ret:
        return ret
    if spec.noop_stmt:
        return spec.noop_stmt
    # Languages without an explicit no-op get a self-increment — always
    # valid and avoids self-assignment lints.
    return f"{spec.self_x} = {spec.self_x} + 0{spec.stmt_end}"


HANDLER_INDENT = "                "  # 16 spaces — handler-body level


def gen_handler_body(idx, n_states, handler_kind, ret_type, spec,
                     use_push=False, use_enter_args=False, is_child=False):
    """Produce target-valid handler-body text with HANDLER_INDENT (16 spaces)
    baked into every line including the first. Callers append the returned
    string verbatim — no additional indent prefix.
    """
    next_state = f"$S{(idx + 1) % n_states}"
    ret = _return_stmt(spec, ret_type, idx)
    leaf = _leaf_stmt(spec, ret_type, idx)
    ind = HANDLER_INDENT

    # push$/pop$ variant on simple handlers — only when 2+ states.
    if handler_kind == "simple" and use_push and idx % 2 == 0 and n_states >= 2:
        if idx + 1 < n_states:
            enter_arg = "(42) " if (use_enter_args and is_child) else ""
            if ret:
                return f"{ind}{ret}\n{ind}push$\n{ind}-> {enter_arg}{next_state}\n"
            return f"{ind}push$\n{ind}-> {enter_arg}{next_state}\n"
        if ret:
            return f"{ind}{ret}\n{ind}-> pop$\n"
        return f"{ind}-> pop$\n"

    if handler_kind == "simple":
        if idx % 2 == 0 and idx + 1 < n_states:
            if ret:
                return f"{ind}{ret}\n{ind}-> {next_state}\n"
            return f"{ind}-> {next_state}\n"
        return f"{ind}{leaf}\n"

    if handler_kind == "cond":
        then_stmt = f"-> {next_state}"
        return render_if_two_arm(spec, f"{spec.self_x} > 0",
                                 then_stmt, leaf, outer_indent=ind)

    if handler_kind == "nested_if":
        then_stmt = f"-> {next_state}"
        return render_if_three_arm(
            spec, f"{spec.self_x} > 0", then_stmt,
            f"{spec.self_x} < 0", leaf, leaf,
            outer_indent=ind,
        )

    if handler_kind == "forward":
        return f"{ind}=> $^\n"

    return f"{ind}{leaf}\n"


ACTION_BODY_INDENT = "            "   # 12 spaces — inside `act_0() { ... }`
ACTION_BRACE_INDENT = "        "      # 8 spaces — for the closing brace


def gen_action_body(kind, spec):
    """Produce `{ body }` text for an action declaration. The returned
    string opens with `{`, the body (indented at 12 spaces), and closes
    with `}` at 8 spaces — matching the action-declaration layout in
    gen_system."""
    if kind == "none":
        return "{}"

    selfx = spec.self_x
    stmt_end = spec.stmt_end

    if kind == "assign":
        return "{ " + f"{selfx} = {selfx} + 1{stmt_end}" + " }"

    if kind == "if":
        body = render_if_two_arm(
            spec, f"{selfx} > 0",
            f"{selfx} = 0{stmt_end}",
            _leaf_stmt(spec, "void", 0),
            outer_indent=ACTION_BODY_INDENT,
        )
        return "{\n" + body + ACTION_BRACE_INDENT + "}"

    if kind == "nested_if":
        body = render_if_three_arm(
            spec, f"{selfx} > 0",
            f"{selfx} = 0{stmt_end}",
            f"{selfx} > 10",
            f"{selfx} = 1{stmt_end}",
            f"{selfx} = 2{stmt_end}",
            outer_indent=ACTION_BODY_INDENT,
        )
        return "{\n" + body + ACTION_BRACE_INDENT + "}"

    raise ValueError(kind)


# --- System generation ---------------------------------------------------

def gen_system(case_id, params, spec):
    n          = params["n_states"]
    hsm_depth  = params["hsm_depth"]
    use_push   = params["use_push"]
    use_sv     = params["use_state_vars"]
    use_ee     = params["use_enter_exit"]
    use_ea     = params["use_enter_args"]
    act_kind   = params["action_body"]
    hnd_kind   = params["handler_body"]
    rt         = params["return_type"]

    if use_push and n < 2:
        use_push = False

    sys_name = f"Fuzz{case_id:04d}"
    lines = []
    lines.append(f"@@target {spec.target}")
    lines.append("")
    if spec.prolog:
        lines.append(spec.prolog.rstrip("\n"))
        lines.append("")
    lines.append(f"@@system {sys_name} {{")

    # Interface
    lines.append("    interface:")
    for i in range(n):
        if rt == "void":
            ret_ann = ""
        elif rt == "int":
            ret_ann = f": {spec.int_type}"
        else:
            ret_ann = f": {spec.str_type}"
        lines.append(f"        evt_{i}(){ret_ann}")
    lines.append("")

    # Machine
    lines.append("    machine:")
    for i in range(n):
        state = f"$S{i}"
        has_parent = hsm_depth > 0 and 0 < i <= hsm_depth
        if has_parent:
            parent = f"$S{0}"
            lines.append(f"        {state} => {parent} {{")
        else:
            lines.append(f"        {state} {{")

        # Enter/exit handlers
        if use_ee and i > 0:
            selfx = spec.self_x
            if use_sv:
                assign = f"{selfx} = {selfx} + 1{spec.stmt_end}"
            else:
                assign = spec.noop_stmt or f"{selfx} = {selfx}{spec.stmt_end}"
            if use_ea and has_parent:
                if use_sv:
                    body = f"{selfx} = {selfx} + arg0{spec.stmt_end}"
                else:
                    body = assign
                lines.append(f"            $>(arg0: {spec.int_type}) {{ {body} }}")
            else:
                lines.append(f"            $>() {{ {assign} }}")
            lines.append(f"            <$() {{ {assign} }}")

        # Event handlers
        for j in range(n):
            emit_here = (i == 0 and j == 0) or ((i + j) % 2 == 0)
            if not emit_here:
                continue
            if rt == "void":
                ret_ann = ""
            elif rt == "int":
                ret_ann = f": {spec.int_type}"
            else:
                ret_ann = f": {spec.str_type}"
            effective_hnd = hnd_kind if (hnd_kind != "forward" or has_parent) else "simple"
            body = gen_handler_body(
                (i if i == 0 and j == 0 else j),
                n, effective_hnd, rt, spec,
                use_push=use_push, use_enter_args=use_ea,
                is_child=has_parent,
            )
            lines.append(f"            evt_{j}(){ret_ann} {{")
            # `body` carries its own 16-space indent; append verbatim.
            lines.append(body.rstrip("\n"))
            lines.append(f"            }}")

        if has_parent:
            lines.append("            => $^")
        lines.append("        }")
    lines.append("")

    # Actions
    if act_kind != "none":
        lines.append("    actions:")
        lines.append(f"        act_0() {gen_action_body(act_kind, spec)}")
        lines.append("")

    # Domain
    lines.append("    domain:")
    lines.append(f"        x: {spec.int_type} = {spec.int_default}")
    lines.append("}")
    return "\n".join(lines) + "\n"


# --- Driver --------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=500)
    p.add_argument("--lang", type=str, default=None,
                   help="Filter to a single language by ext (e.g. fpy)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path,
                   default=Path(__file__).parent / "cases")
    args = p.parse_args()

    random.seed(args.seed)

    axes = list(itertools.product(
        STATE_COUNTS, HSM_DEPTHS, PUSH_POP, STATE_VARS,
        ENTER_EXIT, ENTER_ARGS, ACTION_BODY, HANDLER_BODY, RETURN_TYPE,
    ))
    random.shuffle(axes)
    axes = axes[:args.max]

    langs = [args.lang] if args.lang else list(LANGS.keys())
    args.out.mkdir(parents=True, exist_ok=True)
    for lang_key in langs:
        if lang_key not in LANGS:
            print(f"unknown lang: {lang_key}")
            continue
        spec = LANGS[lang_key]
        lang_dir = args.out / spec.target
        lang_dir.mkdir(exist_ok=True)
        for cid, (n, d, push, sv, ee, ea, act, hnd, rt) in enumerate(axes):
            params = dict(
                n_states=n, hsm_depth=d, use_push=push,
                use_state_vars=sv, use_enter_exit=ee, use_enter_args=ea,
                action_body=act, handler_body=hnd, return_type=rt,
            )
            (lang_dir / f"case_{cid:04d}.{spec.ext}").write_text(
                gen_system(cid, params, spec))
        print(f"Generated {len(axes)} cases for {spec.target}")


if __name__ == "__main__":
    main()
