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

import re as _re

from gen_nested import LANGS, method_name, native_types


def ts_native_types(src: str) -> str:
    """TypeScript-only type rewrite for the strict gate. `gen_nested`'s
    `native_types` leaves TS untouched (TS is in the dynamic-target set,
    so `int` passes through verbatim). But `int` is NOT a TS type, so
    framec's verbatim passthrough emits `: int` annotations that `tsx`
    strips at runtime yet `tsc --strict --noEmit` rejects (TS2304) —
    exactly the #138 class of "runs but doesn't type-check". To make
    the new strict gate meaningful (baseline strict-clean, so it fires
    only on genuine framec regressions) we author the TS Frame source
    with `number`, the way the hand-written matrix TS fixtures do. This
    mirrors `native_types`: rewrite in type-annotation position only,
    after a `:`. No-op for non-TS sources."""
    if '@@[target("typescript")]' not in src:
        return src
    return _re.sub(r"(?<!:)(:\s*)int\b", lambda m: m.group(1) + "number", src)


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


# ---------------------------------------------------------------------
# Wave-3 constructs (if/else, nested if). Each renderer emits the
# full construct given the outer cond, then-body (already terminated),
# and either an else-body (for if_else) or an inner cond + body
# (for nested_if). Indents stack: outer body uses BODY_INDENT (+4),
# nested inner body uses INNER_INDENT (+8) below.
# ---------------------------------------------------------------------

INNER_BLOCK_INDENT = " " * 20      # indent of the inner if construct
INNER_BODY_INDENT = " " * 24       # indent of the inner if's body


def _if_else_python(cond, then_body, else_body):
    return (
        f"{INDENT}if {cond}:\n"
        f"{BODY_INDENT}{then_body}\n"
        f"{INDENT}else:\n"
        f"{BODY_INDENT}{else_body}"
    )


def _if_else_gdscript(cond, then_body, else_body):
    return _if_else_python(cond, then_body, else_body)


def _if_else_js(cond, then_body, else_body):
    return (
        f"{INDENT}if ({cond}) {{\n"
        f"{BODY_INDENT}{then_body}\n"
        f"{INDENT}}} else {{\n"
        f"{BODY_INDENT}{else_body}\n"
        f"{INDENT}}}"
    )


def _if_else_rust(cond, then_body, else_body):
    return (
        f"{INDENT}if {cond} {{\n"
        f"{BODY_INDENT}{then_body}\n"
        f"{INDENT}}} else {{\n"
        f"{BODY_INDENT}{else_body}\n"
        f"{INDENT}}}"
    )


def _if_else_ruby(cond, then_body, else_body):
    return (
        f"{INDENT}if {cond}\n"
        f"{BODY_INDENT}{then_body}\n"
        f"{INDENT}else\n"
        f"{BODY_INDENT}{else_body}\n"
        f"{INDENT}end"
    )


def _if_else_lua(cond, then_body, else_body):
    return (
        f"{INDENT}if {cond} then\n"
        f"{BODY_INDENT}{then_body}\n"
        f"{INDENT}else\n"
        f"{BODY_INDENT}{else_body}\n"
        f"{INDENT}end"
    )


def _nested_if_python(outer_cond, inner_cond, body):
    return (
        f"{INDENT}if {outer_cond}:\n"
        f"{INNER_BLOCK_INDENT}if {inner_cond}:\n"
        f"{INNER_BODY_INDENT}{body}"
    )


def _nested_if_gdscript(outer_cond, inner_cond, body):
    return _nested_if_python(outer_cond, inner_cond, body)


def _nested_if_js(outer_cond, inner_cond, body):
    return (
        f"{INDENT}if ({outer_cond}) {{\n"
        f"{INNER_BLOCK_INDENT}if ({inner_cond}) {{\n"
        f"{INNER_BODY_INDENT}{body}\n"
        f"{INNER_BLOCK_INDENT}}}\n"
        f"{INDENT}}}"
    )


def _nested_if_rust(outer_cond, inner_cond, body):
    return (
        f"{INDENT}if {outer_cond} {{\n"
        f"{INNER_BLOCK_INDENT}if {inner_cond} {{\n"
        f"{INNER_BODY_INDENT}{body}\n"
        f"{INNER_BLOCK_INDENT}}}\n"
        f"{INDENT}}}"
    )


def _nested_if_ruby(outer_cond, inner_cond, body):
    return (
        f"{INDENT}if {outer_cond}\n"
        f"{INNER_BLOCK_INDENT}if {inner_cond}\n"
        f"{INNER_BODY_INDENT}{body}\n"
        f"{INNER_BLOCK_INDENT}end\n"
        f"{INDENT}end"
    )


def _nested_if_lua(outer_cond, inner_cond, body):
    return (
        f"{INDENT}if {outer_cond} then\n"
        f"{INNER_BLOCK_INDENT}if {inner_cond} then\n"
        f"{INNER_BODY_INDENT}{body}\n"
        f"{INNER_BLOCK_INDENT}end\n"
        f"{INDENT}end"
    )


# =====================================================================
# Wave-2 constructs: the FORMS the depth-2 if/else + nested-in-THEN
# wave (above) never reaches. These are the shapes that let real bugs
# slip through:
#
#   * else_if_chain (#124, Asteroids): an N-arm
#       `if c0 {} else if c1 {} else if c2 {} else {}` chain. The
#     Lua/Erlang block-transform lowering must thread `elseif` /
#     `else if` arms, not just a single if/else.
#   * nested_in_else (#135): a nested `if` inside the ELSE block —
#       `if c {} else { if d {} else {} }`. The wave-1 nested form
#     nests in the THEN block only; the else-side indent + statement
#     book-keeping is a different code path.
#   * chain_nested_else (#124 × #135): an else-if chain whose final
#     `else` contains a nested if/else — the deepest mix of the two.
#
# Each renderer is FAMILY-based (brace-with-paren / brace-no-paren /
# python-indent / ruby-end / lua-elseif-end) rather than 16 near-
# duplicate functions, mirroring how the wave-1 renderers already
# reuse `_if_js` across the whole C-family. A renderer takes the
# pre-rendered cond strings + already-terminated body statements and
# returns the construct source at the handler-body indent (16 spaces).
#
# `arm_conds[i]` pairs with `arm_bodies[i]`; `else_body` is the final
# trailing else (None => no else arm). For nested_in_else, the inner
# chain lives inside the outer else; we render it as a nested chain.
# =====================================================================

# Per-family delimiter config. `paren` wraps the cond; `then` is the
# opener keyword suffix (Lua `then`, Ruby ""); `endkw` closes a block.
_FAMILY = {
    # brace-with-paren: JS/TS/Java/C/C++/C#/PHP/Kotlin/Dart
    "brace_paren": dict(open='if (%s) {', elif_='}} else if (%s) {{',
                        else_='} else {', close='}', paren=True,
                        style="brace"),
    # brace-no-paren: Rust/Go/Swift
    "brace_noparen": dict(open='if %s {', elif_='}} else if %s {{',
                          else_='} else {', close='}', paren=False,
                          style="brace"),
    # python-indent: Python/GDScript
    "py": dict(style="py"),
    "ruby": dict(style="ruby"),
    "lua": dict(style="lua"),
}

# NOTE on Lua: the wave-1 Lua if-renderers emit NATIVE `if…then…
# elseif…else…end`, which framec passes through verbatim. But #124
# (`end else if`) and #135 (brace leak) are bugs in framec's Lua
# BLOCK-TRANSFORM lowering, which only fires on the BRACE form
# (`} else if c {`, `} else { if c { } }`). The native `elseif` form
# sidesteps the lowering and would NOT have caught the Asteroids bug.
# So for the Wave-2 forms Lua is routed through `brace_noparen`: the
# Frame source carries brace-style `else if` / nested-`if`-in-`else`,
# and framec's output_block_parser must lower it to `elseif` / `end`.
# This is the real #124/#135 code path. (Erlang would join here too,
# when its renderer lands.)
_LANG_FAMILY = {
    "javascript": "brace_paren", "typescript": "brace_paren",
    "java": "brace_paren", "c": "brace_paren", "cpp": "brace_paren",
    "csharp": "brace_paren", "php": "brace_paren", "kotlin": "brace_paren",
    "dart": "brace_paren",
    "rust": "brace_noparen", "go": "brace_noparen", "swift": "brace_noparen",
    "lua": "brace_noparen",
    "python_3": "py", "gdscript": "py",
    "ruby": "ruby",
}


def _chain_brace(arm_conds, arm_bodies, else_body, paren, ind, body_ind):
    """Render an else-if chain for a brace family at the given indent.
    `ind` is the indent of the `if`; `body_ind` is the arm-body indent.
    Works for both paren and no-paren brace families."""
    lines = []
    for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
        cc = f"({c})" if paren else c
        if i == 0:
            lines.append(f"{ind}if {cc} {{")
        else:
            lines.append(f"{ind}}} else if {cc} {{")
        lines.append(f"{body_ind}{b}")
    if else_body is not None:
        lines.append(f"{ind}}} else {{")
        lines.append(f"{body_ind}{else_body}")
    lines.append(f"{ind}}}")
    return "\n".join(lines)


def _chain_py(arm_conds, arm_bodies, else_body, ind, body_ind):
    lines = []
    for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
        kw = "if" if i == 0 else "elif"
        lines.append(f"{ind}{kw} {c}:")
        lines.append(f"{body_ind}{b}")
    if else_body is not None:
        lines.append(f"{ind}else:")
        lines.append(f"{body_ind}{else_body}")
    return "\n".join(lines)


def _chain_ruby(arm_conds, arm_bodies, else_body, ind, body_ind):
    lines = []
    for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
        kw = "if" if i == 0 else "elsif"
        lines.append(f"{ind}{kw} {c}")
        lines.append(f"{body_ind}{b}")
    if else_body is not None:
        lines.append(f"{ind}else")
        lines.append(f"{body_ind}{else_body}")
    lines.append(f"{ind}end")
    return "\n".join(lines)


def _chain_lua(arm_conds, arm_bodies, else_body, ind, body_ind):
    lines = []
    for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
        kw = "if" if i == 0 else "elseif"
        lines.append(f"{ind}{kw} {c} then")
        lines.append(f"{body_ind}{b}")
    if else_body is not None:
        lines.append(f"{ind}else")
        lines.append(f"{body_ind}{else_body}")
    lines.append(f"{ind}end")
    return "\n".join(lines)


def render_chain(lang, arm_conds, arm_bodies, else_body,
                 ind=INDENT, body_ind=BODY_INDENT):
    """Dispatch an else-if chain to the language's family renderer."""
    fam = _LANG_FAMILY[lang]
    style = _FAMILY[fam]["style"]
    if style == "brace":
        return _chain_brace(arm_conds, arm_bodies, else_body,
                            _FAMILY[fam]["paren"], ind, body_ind)
    if style == "py":
        return _chain_py(arm_conds, arm_bodies, else_body, ind, body_ind)
    if style == "ruby":
        return _chain_ruby(arm_conds, arm_bodies, else_body, ind, body_ind)
    if style == "lua":
        return _chain_lua(arm_conds, arm_bodies, else_body, ind, body_ind)
    raise ValueError(f"no chain renderer for {lang}")


def render_nested_in_else(lang, outer_cond, then_body,
                          inner_conds, inner_bodies, inner_else_body):
    """`if outer { then } else { <chain of inner ifs> }`.

    The inner chain is itself rendered with render_chain at a +4
    deeper indent so the nested-in-ELSE indent/statement book-keeping
    (the #135 path) is exercised. `len(inner_conds)` controls depth:
    1 inner cond => 2 levels, 2 inner conds => a 3-level
    if/elseif/else inside the else."""
    fam = _LANG_FAMILY[lang]
    style = _FAMILY[fam]["style"]
    inner = render_chain(lang, inner_conds, inner_bodies, inner_else_body,
                         ind=INNER_BLOCK_INDENT, body_ind=INNER_BODY_INDENT)
    if style == "brace":
        paren = _FAMILY[fam]["paren"]
        oc = f"({outer_cond})" if paren else outer_cond
        return (
            f"{INDENT}if {oc} {{\n"
            f"{BODY_INDENT}{then_body}\n"
            f"{INDENT}}} else {{\n"
            f"{inner}\n"
            f"{INDENT}}}"
        )
    if style == "py":
        return (
            f"{INDENT}if {outer_cond}:\n"
            f"{BODY_INDENT}{then_body}\n"
            f"{INDENT}else:\n"
            f"{inner}"
        )
    if style == "ruby":
        return (
            f"{INDENT}if {outer_cond}\n"
            f"{BODY_INDENT}{then_body}\n"
            f"{INDENT}else\n"
            f"{inner}\n"
            f"{INDENT}end"
        )
    if style == "lua":
        return (
            f"{INDENT}if {outer_cond} then\n"
            f"{BODY_INDENT}{then_body}\n"
            f"{INDENT}else\n"
            f"{inner}\n"
            f"{INDENT}end"
        )
    raise ValueError(f"no nested-in-else renderer for {lang}")


def render_chain_nested_else(lang, arm_conds, arm_bodies,
                             inner_conds, inner_bodies, inner_else_body):
    """An else-if chain whose final `else` holds a nested if/else.
    The deepest mix of the chain (#124) and nested-in-else (#135)
    forms. Built by handing render_nested_in_else's inner-chain to the
    chain renderer as the `else_body` — but because the else body is a
    multi-line block, we assemble it directly per family."""
    fam = _LANG_FAMILY[lang]
    style = _FAMILY[fam]["style"]
    inner = render_chain(lang, inner_conds, inner_bodies, inner_else_body,
                         ind=INNER_BLOCK_INDENT, body_ind=INNER_BODY_INDENT)
    if style == "brace":
        paren = _FAMILY[fam]["paren"]
        lines = []
        for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
            cc = f"({c})" if paren else c
            if i == 0:
                lines.append(f"{INDENT}if {cc} {{")
            else:
                lines.append(f"{INDENT}}} else if {cc} {{")
            lines.append(f"{BODY_INDENT}{b}")
        lines.append(f"{INDENT}}} else {{")
        lines.append(inner)
        lines.append(f"{INDENT}}}")
        return "\n".join(lines)
    if style == "py":
        lines = []
        for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
            kw = "if" if i == 0 else "elif"
            lines.append(f"{INDENT}{kw} {c}:")
            lines.append(f"{BODY_INDENT}{b}")
        lines.append(f"{INDENT}else:")
        lines.append(inner)
        return "\n".join(lines)
    if style == "ruby":
        lines = []
        for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
            kw = "if" if i == 0 else "elsif"
            lines.append(f"{INDENT}{kw} {c}")
            lines.append(f"{BODY_INDENT}{b}")
        lines.append(f"{INDENT}else")
        lines.append(inner)
        lines.append(f"{INDENT}end")
        return "\n".join(lines)
    if style == "lua":
        lines = []
        for i, (c, b) in enumerate(zip(arm_conds, arm_bodies)):
            kw = "if" if i == 0 else "elseif"
            lines.append(f"{INDENT}{kw} {c} then")
            lines.append(f"{BODY_INDENT}{b}")
        lines.append(f"{INDENT}else")
        lines.append(inner)
        lines.append(f"{INDENT}end")
        return "\n".join(lines)
    raise ValueError(f"no chain-nested-else renderer for {lang}")


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

# `if/else` and nested-`if` renderers reuse the brace-with-paren shape
# for every C-style language, the brace-without-paren shape for Rust/
# Go/Swift, and target-specific shapes for Python/GDScript/Ruby/Lua.
IF_ELSE_RENDERERS = {
    "python_3": _if_else_python,
    "gdscript": _if_else_gdscript,
    "javascript": _if_else_js,
    "typescript": _if_else_js,
    "java": _if_else_js,
    "c": _if_else_js,
    "cpp": _if_else_js,
    "csharp": _if_else_js,
    "php": _if_else_js,
    "kotlin": _if_else_js,
    "dart": _if_else_js,
    "rust": _if_else_rust,
    "go": _if_else_rust,
    "swift": _if_else_rust,
    "ruby": _if_else_ruby,
    "lua": _if_else_lua,
}

NESTED_IF_RENDERERS = {
    "python_3": _nested_if_python,
    "gdscript": _nested_if_gdscript,
    "javascript": _nested_if_js,
    "typescript": _nested_if_js,
    "java": _nested_if_js,
    "c": _nested_if_js,
    "cpp": _nested_if_js,
    "csharp": _nested_if_js,
    "php": _nested_if_js,
    "kotlin": _nested_if_js,
    "dart": _nested_if_js,
    "rust": _nested_if_rust,
    "go": _nested_if_rust,
    "swift": _nested_if_rust,
    "ruby": _nested_if_ruby,
    "lua": _nested_if_lua,
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
    # Constant-true but NOT literal-vs-literal: `1 == 1` makes TS strict
    # narrow both sides to the literal type `1` and reject the compare
    # as unintentional (TS2367), which the #138 strict gate would then
    # flag as a (spurious) failure. Read the domain field `f` (init 5)
    # instead — `f >= 0` is always true, never narrowed to a literal.
    return f"{spec.self_word}{spec.field_op}f >= 0"


def _cond_lit_false(spec):
    # Constant-false, strict-clean (see _cond_lit_true). `f < 0` is
    # always false for f init 5, and TS doesn't narrow it.
    return f"{spec.self_word}{spec.field_op}f < 0"


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


def case_id(cond, body, lit, construct="if_only", inner_cond=None):
    sign = "n" if lit < 0 else ""
    if construct == "if_only":
        return f"cf_{cond.name}__{body.name}__lit{sign}{abs(lit)}"
    if construct == "if_else":
        return f"cf_else_{cond.name}__{body.name}__lit{sign}{abs(lit)}"
    if construct == "nested_if":
        return (
            f"cf_nest_{cond.name}__{inner_cond.name}__{body.name}"
            f"__lit{sign}{abs(lit)}"
        )
    raise ValueError(f"unknown construct {construct}")


def equiv_class(cond, body, construct="if_only", inner_cond=None):
    if construct == "if_only":
        return f"{cond.name}__{body.name}"
    if construct == "if_else":
        return f"else_{cond.name}__{body.name}"
    if construct == "nested_if":
        return f"nest_{cond.name}__{inner_cond.name}__{body.name}"
    raise ValueError(f"unknown construct {construct}")


# ---------------------------------------------------------------------
# Wave-3 simulators.
#
# `simulate_if_else` mirrors `simulate` but the false branch fires an
# observable else-mutation rather than leaving state unchanged. The
# else mutation uses ELSE_LIT — distinct from any LIT_VALUES element
# so a missing/buggy else emit produces a wrong-but-distinguishable
# observable rather than silently matching another case.
#
# `simulate_nested_if` runs the body iff outer AND inner conds are
# both true. Same body-simulator semantics as the wave-1 `simulate`,
# just gated by a two-level conjunction.
# ---------------------------------------------------------------------

ELSE_LIT = 42       # disjoint from LIT_VALUES.


def simulate_if_else(cond, body, lit):
    """If cond is true the body's post-* fires (same as wave-1).
    Otherwise the else arm writes ELSE_LIT into the same slot the
    body would have written, so verify still observes via the body's
    verify_method."""
    ret_init = RET_SENTINEL if body.name == "ret_w" else 0
    state = {"dom": DOMAIN_F_INIT, "sv": SV_S_INIT, "ret": ret_init}
    if cond.is_true:
        if body.post_dom is not None:
            state["dom"] = body.post_dom(state, lit)
        if body.post_sv is not None:
            state["sv"] = body.post_sv(state, lit)
        if body.post_ret is not None:
            state["ret"] = body.post_ret(state, lit)
    else:
        # Else-body writes ELSE_LIT into the body's verify slot. For
        # transition bodies the else arm is a no-op (transition bodies
        # already verify via dom — let the false-cond case observe the
        # initial dom value instead of forcing a redundant write).
        if body.transitions:
            pass
        elif body.verify_method == "get_n":
            state["dom"] = ELSE_LIT
        elif body.verify_method == "get_scache":
            state["sv"] = ELSE_LIT
        elif body.drive_returns:
            state["ret"] = ELSE_LIT
    if body.drive_returns:
        return state["ret"]
    if body.verify_method == "get_n":
        return state["dom"]
    if body.verify_method == "get_scache":
        return state["sv"]
    raise ValueError(f"unhandled verify_method {body.verify_method}")


def simulate_nested_if(outer_cond, inner_cond, body, lit):
    ret_init = RET_SENTINEL if body.name == "ret_w" else 0
    state = {"dom": DOMAIN_F_INIT, "sv": SV_S_INIT, "ret": ret_init}
    if outer_cond.is_true and inner_cond.is_true:
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


def enumerate_cases():
    seen_classes = set()
    # Wave-1: if-only.
    for cond in CONDS:
        for body in BODIES:
            for lit in LIT_VALUES:
                cid = case_id(cond, body, lit, "if_only")
                cls = equiv_class(cond, body, "if_only")
                is_smoke = cls not in seen_classes
                if is_smoke:
                    seen_classes.add(cls)
                expected = simulate(cond, body, lit)
                yield (cid, cls, expected, cond, body, lit, is_smoke,
                       "if_only", None)
    # Wave-3 axis A: if/else. Same dimensions; else arm fires
    # ELSE_LIT into the body's observable slot.
    for cond in CONDS:
        for body in BODIES:
            for lit in LIT_VALUES:
                cid = case_id(cond, body, lit, "if_else")
                cls = equiv_class(cond, body, "if_else")
                is_smoke = cls not in seen_classes
                if is_smoke:
                    seen_classes.add(cls)
                expected = simulate_if_else(cond, body, lit)
                yield (cid, cls, expected, cond, body, lit, is_smoke,
                       "if_else", None)
    # Wave-3 axis B: nested if. Outer fixed lit_true so we always
    # enter the outer block; the inner cond varies. Body runs iff
    # both true. Tests whether framec correctly emits Frame
    # statements inside a doubly-nested native if — the indent and
    # statement-boundary book-keeping that single-if depth doesn't
    # exercise.
    outer = CONDS[0]   # lit_true
    for inner in CONDS:
        for body in BODIES:
            for lit in LIT_VALUES:
                cid = case_id(outer, body, lit, "nested_if", inner)
                cls = equiv_class(outer, body, "nested_if", inner)
                is_smoke = cls not in seen_classes
                if is_smoke:
                    seen_classes.add(cls)
                expected = simulate_nested_if(outer, inner, body, lit)
                yield (cid, cls, expected, outer, body, lit, is_smoke,
                       "nested_if", inner)


# ---------------------------------------------------------------------
# Per-language case emission. Largely mirrors gen_perm.py /
# gen_stmt_pair.py — drive returns int when body writes ret slot,
# else returns void and verification reads dom/sv via get_n /
# get_scache.
# ---------------------------------------------------------------------

def _else_body_src(body, spec, lit):
    """Render the Frame statement for the else arm of an if_else
    construct. Mirrors the body shape: same target slot, but writes
    ELSE_LIT instead of `lit`. Transitions become no-ops (they have
    no easy 'opposite transition' that observes a distinct slot)."""
    if body.transitions:
        return None
    if body.name == "dom_w":
        return f"{spec.self_word}{spec.field_op}f = {ELSE_LIT}"
    if body.name == "sv_w":
        return f"$.s = {ELSE_LIT}"
    if body.name == "ret_w":
        return f"@@:return = {ELSE_LIT}"
    if body.name == "sc_assign_dom":
        # The else arm doesn't need to call compute — write ELSE_LIT
        # directly so the false-cond case observes a distinct value.
        return f"{spec.self_word}{spec.field_op}f = {ELSE_LIT}"
    raise ValueError(f"unhandled body shape for else: {body.name}")


def gen_case(lang, cid, equiv, expected, cond, body, lit, is_smoke,
             construct="if_only", inner_cond=None):
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

    if construct == "if_only":
        if_construct = IF_RENDERERS[lang](cond_src, body_terminated)
    elif construct == "if_else":
        else_body_src = _else_body_src(body, spec, lit)
        if else_body_src is None:
            # Transition body in if_else degenerates to if_only (no
            # else arm). Fall back to plain if-construct so the case
            # is still emitted but observable matches the no-op else.
            if_construct = IF_RENDERERS[lang](cond_src, body_terminated)
        else:
            else_terminated = else_body_src + spec.stmt_end
            if_construct = IF_ELSE_RENDERERS[lang](
                cond_src, body_terminated, else_terminated
            )
    elif construct == "nested_if":
        inner_src = inner_cond.render(spec)
        if_construct = NESTED_IF_RENDERERS[lang](
            cond_src, inner_src, body_terminated
        )
    else:
        raise ValueError(f"unknown construct {construct}")

    lines = []
    lines.append(f'@@[target("{spec.target}")]')
    # PHP prolog: framec emits `<?php` itself (commit 12befc3)
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

    _emit_driver(lines, lang, cid, sys_name, m_drive, m_verify,
                 body.drive_returns, expected, spec, no_arg=True)
    return "\n".join(lines)


def _emit_driver(lines, lang, cid, sys_name, m_drive, m_verify,
                 drive_returns, expected, spec, no_arg=True,
                 drive_arg=""):
    """Per-language test-driver tail. Factored out of gen_case so the
    Wave-2 forms (else-if chain, nested-in-else, chain+nested) reuse
    the identical, proven driver. `drive_arg` lets a Wave-2 case pass
    a selector value to drive(); empty => zero-arg drive().

    TypeScript NOTE (the #138 gap): the TS `_fail` here must NOT depend
    on `process` (no @types/node in the strict gate) — we throw instead
    of `process.exit`. Combined with `native_types` rewriting `int`→
    `number` for TS (see ts_native_types), the generated TS is
    strict-clean BY CONSTRUCTION, so the new `tsc --strict --noEmit`
    gate fails only on a genuine framec codegen regression."""
    _drive_call_arg = drive_arg
    # C free-function drive takes `self` first; a selector arg follows
    # as `, <arg>`. Empty when no_arg.
    _c_extra = f", {drive_arg}" if drive_arg != "" else ""
    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = @@{sys_name}()")
        if drive_returns:
            lines.append(f"_ret = _inst.{m_drive}({_drive_call_arg})")
        else:
            lines.append(f"_inst.{m_drive}({_drive_call_arg})")
            lines.append(f"_ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"const _ret = _inst.{m_drive}({_drive_call_arg});")
        else:
            lines.append(f"_inst.{m_drive}({_drive_call_arg});")
            lines.append(f"const _ret = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "typescript":
        # #138 gate: this _fail must NOT reference `process` (no
        # @types/node under `tsc --strict`). Throw instead — same
        # non-zero-exit + "FAIL" stderr the runner greps for.
        lines.append('function _fail(msg: string): never { '
                     'throw new Error("FAIL: " + msg); }')
        lines.append(f"const _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"const _ret: number = _inst.{m_drive}({_drive_call_arg});")
        else:
            lines.append(f"_inst.{m_drive}({_drive_call_arg});")
            lines.append(f"const _ret: number = _inst.{m_verify}();")
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = @@{sys_name}()")
        # Ruby: paren-less call for zero-arg drive (wave-1/3); explicit
        # `drive(sel)` when a Wave-2 selector arg is present.
        _rb_drive = (f"{m_drive}({_drive_call_arg})"
                     if _drive_call_arg != "" else m_drive)
        if drive_returns:
            lines.append(f"_ret = _inst.{_rb_drive}")
        else:
            lines.append(f"_inst.{_rb_drive}")
            lines.append(f"_ret = _inst.{m_verify}")
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = @@{sys_name}()")
        if drive_returns:
            lines.append(f"local _ret = _inst:{m_drive}({_drive_call_arg})")
        else:
            lines.append(f"_inst:{m_drive}({_drive_call_arg})")
            lines.append(f"local _ret = _inst:{m_verify}()")
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"$_ret = $_inst->{m_drive}({_drive_call_arg});")
        else:
            lines.append(f"$_inst->{m_drive}({_drive_call_arg});")
            lines.append(f"$_ret = $_inst->{m_verify}();")
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"    final _ret = _inst.{m_drive}({_drive_call_arg});")
        else:
            lines.append(f"    _inst.{m_drive}({_drive_call_arg});")
            lines.append(f"    final _ret = _inst.{m_verify}();")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("}")
    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"    let _ret = _inst.{m_drive}({_drive_call_arg});")
        else:
            lines.append(f"    _inst.{m_drive}({_drive_call_arg});")
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
        lines.append(f"    sm := @@{sys_name}()")
        if drive_returns:
            lines.append(f"    ret := sm.{m_drive}({_drive_call_arg})")
        else:
            lines.append(f"    sm.{m_drive}({_drive_call_arg})")
            lines.append(f"    ret := sm.{m_verify}()")
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("}")
    elif lang == "swift":
        lines.append(spec.fail_exit_def)
        lines.append(f"var _inst = @@{sys_name}()")
        if drive_returns:
            lines.append(f"let _ret = _inst.{m_drive}({_drive_call_arg})")
        else:
            lines.append(f"_inst.{m_drive}({_drive_call_arg})")
            lines.append(f"let _ret = _inst.{m_verify}()")
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "ctrl-flow"))
    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"        int _ret = (int) _inst.{m_drive}({_drive_call_arg});")
        else:
            lines.append(f"        _inst.{m_drive}({_drive_call_arg});")
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
        lines.append(f"    val _inst = @@{sys_name}()")
        if drive_returns:
            lines.append(f"    val _ret = _inst.{m_drive}({_drive_call_arg}) as Int")
        else:
            lines.append(f"    _inst.{m_drive}({_drive_call_arg})")
            lines.append(f"    val _ret = _inst.{m_verify}() as Int")
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("}")
    elif lang == "csharp":
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"            int _ret = (int) _inst.{m_drive}({_drive_call_arg});")
        else:
            lines.append(f"            _inst.{m_drive}({_drive_call_arg});")
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
        lines.append(f"    {sys_name}* _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{m_drive}(_inst{_c_extra});")
        else:
            lines.append(f"    {sys_name}_{m_drive}(_inst{_c_extra});")
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
        lines.append(f"    auto _inst = @@{sys_name}();")
        if drive_returns:
            lines.append(f"    int _ret = std::any_cast<int>(_inst.{m_drive}({_drive_call_arg}));")
        else:
            lines.append(f"    _inst.{m_drive}({_drive_call_arg});")
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
        lines.append(f"    var _inst = @@{sys_name}()")
        if drive_returns:
            lines.append(f"    var _ret = _inst.{m_drive}({_drive_call_arg})")
        else:
            lines.append(f"    _inst.{m_drive}({_drive_call_arg})")
            lines.append(f"    var _ret = _inst.{m_verify}()")
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'ctrl-flow')}")
        lines.append("    quit()")

    return "\n".join(lines)


# =====================================================================
# Wave-2 case generation: else-if chain, nested-in-else, chain+nested.
#
# These are self-contained (own enumerate / simulate / emit) so the
# wave-1/wave-3 regression set above is untouched. Each case fixes ONE
# selector value, so exactly one arm fires and is independently
# asserted — a wrong arm => wrong observable => FAIL. Together the
# per-arm cases prove every arm is reachable & distinct.
#
# Mechanics: `drive(sel: int)` carries the selector; each arm writes a
# distinct literal to domain `f` (arm i => ARM_VALUE(i); the trailing
# else => ELSE_VALUE). Verify via get_n (domain read), the same proven
# void-drive-then-getter shape the other waves use.
# =====================================================================

ELSE_VALUE = 99            # value written by a trailing `else`.
INNER_ELSE_VALUE = 88      # nested-in-else inner trailing `else`.
THEN_VALUE = 7             # nested-in-else outer THEN arm value.


def arm_value(i):
    """Distinct per-arm observable: arm 0=>10, 1=>20, 2=>30, 3=>40."""
    return 10 * (i + 1)


def _sel_cond(spec, k):
    """`sel == k` in the target's native spelling (sel is the handler
    param; PHP needs `$sel`)."""
    return f"{spec.param_prefix}sel == {k}"


def _w2_body_dom_w(spec, value):
    """Arm body: write `value` to domain f."""
    return f"{spec.self_word}{spec.field_op}f = {value}"


# Chain widths to generate: N=3 and N=4 ARMS (excluding the trailing
# else). N=3 chain => if/else-if/else-if + else.
CHAIN_WIDTHS = [3, 4]

# nested-in-else inner-chain depths: 1 inner cond (=> if/else, a
# 2-level total nest) and 2 inner conds (=> if/elif/else, 3-level).
NESTED_ELSE_DEPTHS = [1, 2]


def w2_enumerate():
    """Yield Wave-2 cases as dicts. Each picks one firing arm so the
    observable is unambiguous."""
    # --- else-if chain (#124) ---
    for n in CHAIN_WIDTHS:
        # sel in 1..n hits arm (sel-1); sel=0 hits the trailing else.
        for sel in list(range(1, n + 1)) + [0]:
            if sel == 0:
                expected = ELSE_VALUE
                arm_tag = "else"
            else:
                expected = arm_value(sel - 1)
                arm_tag = f"arm{sel - 1}"
            cid = f"cf_chain{n}__sel{sel}_{arm_tag}"
            cls = f"chain{n}__{arm_tag}"
            yield dict(kind="chain", n=n, sel=sel, cid=cid, cls=cls,
                       expected=expected)
    # --- nested-in-else (#135) ---
    # Outer cond `sel == 9` selects the THEN arm; else holds an inner
    # chain over sel in 1..depth, with a trailing inner else.
    for depth in NESTED_ELSE_DEPTHS:
        sel_values = [9] + list(range(1, depth + 1)) + [0]
        for sel in sel_values:
            if sel == 9:
                expected, arm_tag = THEN_VALUE, "then"
            elif sel == 0:
                expected, arm_tag = INNER_ELSE_VALUE, "inner_else"
            else:
                expected, arm_tag = arm_value(sel - 1), f"inner_arm{sel - 1}"
            cid = f"cf_nelse{depth}__sel{sel}_{arm_tag}"
            cls = f"nelse{depth}__{arm_tag}"
            yield dict(kind="nested_else", depth=depth, sel=sel, cid=cid,
                       cls=cls, expected=expected)
    # --- chain + nested-in-else mix (#124 × #135) ---
    # An N=3 chain whose trailing `else` holds a 2-arm inner chain.
    # sel 1..3 hit the outer arms; sel 4/5 hit the inner arms; sel 0
    # hits the inner trailing else.
    OUTER_N = 3
    INNER_N = 2
    for sel in [1, 2, 3, 4, 5, 0]:
        if 1 <= sel <= OUTER_N:
            expected, arm_tag = arm_value(sel - 1), f"outer_arm{sel - 1}"
        elif OUTER_N < sel <= OUTER_N + INNER_N:
            inner_idx = sel - OUTER_N - 1
            expected, arm_tag = arm_value(OUTER_N + inner_idx), \
                f"inner_arm{inner_idx}"
        else:  # sel == 0
            expected, arm_tag = INNER_ELSE_VALUE, "inner_else"
        cid = f"cf_mix__sel{sel}_{arm_tag}"
        cls = f"mix__{arm_tag}"
        yield dict(kind="mix", outer_n=OUTER_N, inner_n=INNER_N, sel=sel,
                   cid=cid, cls=cls, expected=expected)


def _w2_construct_src(lang, spec, case):
    """Build the control-flow construct source for a Wave-2 case."""
    stmt_end = spec.stmt_end
    kind = case["kind"]
    if kind == "chain":
        n = case["n"]
        conds = [_sel_cond(spec, k + 1) for k in range(n)]
        bodies = [_w2_body_dom_w(spec, arm_value(k)) + stmt_end
                  for k in range(n)]
        else_body = _w2_body_dom_w(spec, ELSE_VALUE) + stmt_end
        return render_chain(lang, conds, bodies, else_body)
    if kind == "nested_else":
        depth = case["depth"]
        outer_cond = _sel_cond(spec, 9)
        then_body = _w2_body_dom_w(spec, THEN_VALUE) + stmt_end
        inner_conds = [_sel_cond(spec, k + 1) for k in range(depth)]
        inner_bodies = [_w2_body_dom_w(spec, arm_value(k)) + stmt_end
                        for k in range(depth)]
        inner_else = _w2_body_dom_w(spec, INNER_ELSE_VALUE) + stmt_end
        return render_nested_in_else(lang, outer_cond, then_body,
                                     inner_conds, inner_bodies, inner_else)
    if kind == "mix":
        on, inn = case["outer_n"], case["inner_n"]
        outer_conds = [_sel_cond(spec, k + 1) for k in range(on)]
        outer_bodies = [_w2_body_dom_w(spec, arm_value(k)) + stmt_end
                        for k in range(on)]
        inner_conds = [_sel_cond(spec, on + k + 1) for k in range(inn)]
        inner_bodies = [_w2_body_dom_w(spec, arm_value(on + k)) + stmt_end
                        for k in range(inn)]
        inner_else = _w2_body_dom_w(spec, INNER_ELSE_VALUE) + stmt_end
        return render_chain_nested_else(lang, outer_conds, outer_bodies,
                                        inner_conds, inner_bodies, inner_else)
    raise ValueError(f"unknown wave-2 kind {kind}")


def gen_case_w2(lang, case):
    """Emit one Wave-2 .f<ext> source. Reuses _emit_driver — drive(sel)
    is void, verify via get_n (domain read)."""
    spec = LANGS[lang]
    cid = case["cid"]
    sys_name = f"CtrlFlow_{cid}"
    expected = case["expected"]
    sel = case["sel"]

    m_drive = method_name(lang, "drive")
    m_get_n = method_name(lang, "get_n")
    drive_sig = f"{m_drive}(sel: int)"

    construct = _w2_construct_src(lang, spec, case)

    lines = []
    lines.append(f'@@[target("{spec.target}")]')
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    lines.append(f"        {drive_sig}")
    lines.append(f"        {m_get_n}(): int")
    lines.append("")
    lines.append("    machine:")
    lines.append("        $S0 {")
    lines.append(f"            {drive_sig} {{")
    lines.append(construct)
    lines.append("            }")
    lines.append(f"            {m_get_n}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}")
    lines.append("        }")
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = 0")
    lines.append("}")
    lines.append("")

    _emit_driver(lines, lang, cid, sys_name, m_drive, m_get_n,
                 drive_returns=False, expected=expected, spec=spec,
                 no_arg=False, drive_arg=str(sel))
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
        for (cid, equiv, expected, cond, body, lit, is_smoke,
             construct, inner_cond) in enumerate_cases():
            src = gen_case(
                lang, cid, equiv, expected, cond, body, lit, is_smoke,
                construct=construct, inner_cond=inner_cond,
            )
            path = out / f"{cid}.{spec.ext}"
            path.write_text(ts_native_types(native_types(src)))
            index_rows.append(
                f"{lang}\t{cid}\t{equiv}\t{'yes' if is_smoke else 'no'}\t{expected}"
            )
            per_lang += 1
            if is_smoke:
                smoke_count += 1
        # --- Wave-2: else-if chain / nested-in-else / chain+nested ---
        # All 22 are high-value forms; tag them all smoke so the smoke
        # tier (every iteration) exercises #124/#135 coverage.
        for case in w2_enumerate():
            src = gen_case_w2(lang, case)
            path = out / f"{case['cid']}.{spec.ext}"
            path.write_text(ts_native_types(native_types(src)))
            index_rows.append(
                f"{lang}\t{case['cid']}\t{case['cls']}\tyes\t{case['expected']}"
            )
            per_lang += 1
            smoke_count += 1
        smoke_count_by_lang[lang] = smoke_count
        cases_per_lang = per_lang

    (out / "_index.tsv").write_text("\n".join(index_rows) + "\n")

    print(f"generated {cases_per_lang} cases × {len(smoke_count_by_lang)} langs into {out}")
    for lang, cnt in smoke_count_by_lang.items():
        print(f"  {lang}: {cases_per_lang} cases, {cnt} smoke")


if __name__ == "__main__":
    main()
