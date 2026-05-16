#!/usr/bin/env python3
"""
Port a robotics .fpy fixture to all 16 non-Python backends.

**STATUS: SCAFFOLD, NOT A FINISHED CODEMOD.**

Drafted 2026-05-16 against the robotics-port arc. Validated against
`14_fleet_robot.fpy` and confirmed to produce reasonable starts for
each backend, but several real-world gaps remain (see *Limitations*
below). The script is committed as a starting point so future port
work can extend it incrementally rather than re-deriving the
splitting / per-language metadata logic from scratch.

Input: a .fpy fixture matching the robotics convention —
    @@[target("python_3")]
    <comments>
    @@system Name(...) { interface / machine / domain }
    <Python driver: helper fn(s), if __name__ == '__main__': body>

Output: 16 sibling files (.frs/.fjava/.fkt/.fcs/.fswift/.fgo/.fjs/.fts/
.frb/.flua/.fphp/.fdart/.fgd/.fc/.fcpp/.ferl + .escript) in the same
directory.

What works today:
1. Splits the .fpy into target / comments / @@system block / driver
   (brace-balanced; handles nested HSM).
2. Per-language `self.field` substitution: `this.field` /
   `$this->field` / `s.field` / `self->field` / `self.field`.
3. Per-language type substitution: int → i32 / Int / number / int;
   str → String / string; bool → boolean / Boolean / bool.
4. Driver emitter for Rust and JS/TS — recognizes `var = @@Sys(args)`,
   `var.method(args)`, and `check("label", var.method(args), "expected")`
   patterns and emits idiomatic per-language drivers.

What this script does NOT yet handle (per-recipe manual finishing
still required for most backends):

- **Handler-body syntactic rewriting**: Python's `if x:` block,
  bare statements without terminators, Python's `import sys`, etc.,
  are NOT rewritten for backends that need braces and `;`. The Frame
  source spec is mostly language-agnostic, but handler bodies are
  pass-through native — they MUST match the target's syntax.
- **String ownership idioms (Rust)**: hand-written Rust port uses
  `String::from("literal")` and `.clone()`; this script emits the
  raw Frame source.
- **Per-target prologue blocks**: Go's `package main` + imports at
  file head, Dart's `import 'dart:io'` at top, C's `#include`
  declarations, GDScript's `extends SceneTree`, Erlang's separate
  `.escript` driver — none of these are emitted automatically.
- **Driver emitters for Java/C#/Kotlin/Swift/Dart/Go/PHP/Ruby/Lua/
  C/C++/GDScript/Erlang**: only Rust + JS/TS have full driver
  templates. The others produce stub comments listing the parsed ops
  for the user to translate.

Realistic per-recipe time savings with this scaffold:
- Without: ~1.5 hours per recipe across 16 backends.
- With this scaffold (Rust + JS/TS auto-generated correctly,
  others as stubs): ~1.0-1.2 hours, mostly via the .fpy split +
  self-substitution + type-substitution saving copy-paste churn.

Real acceleration (to ~20 min per recipe) requires extending the
driver emitters AND adding handler-body syntactic rewriters for each
target. That's a multi-session script-development effort in its own
right.

Usage:
    scripts/port_recipe.py tests/common/positive/robotics/14_fleet_robot.fpy

The .fpy file is left untouched; sibling files are written if missing
and overwritten if present.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------
# Per-backend metadata
# ---------------------------------------------------------------------
# Each entry: (extension, target_annotation, self_token, type_map_fn,
#              driver_template, prologue_lines)

BACKENDS = [
    "rust", "java", "kotlin", "csharp", "swift", "go", "javascript",
    "typescript", "ruby", "lua", "php", "dart", "gdscript", "c", "cpp",
    "erlang",
]

EXT = {
    "rust": "frs", "java": "fjava", "kotlin": "fkt", "csharp": "fcs",
    "swift": "fswift", "go": "fgo", "javascript": "fjs",
    "typescript": "fts", "ruby": "frb", "lua": "flua", "php": "fphp",
    "dart": "fdart", "gdscript": "fgd", "c": "fc", "cpp": "fcpp",
    "erlang": "ferl",
}

TARGET = {
    "rust": "rust", "java": "java", "kotlin": "kotlin",
    "csharp": "csharp", "swift": "swift", "go": "go",
    "javascript": "javascript", "typescript": "typescript",
    "ruby": "ruby", "lua": "lua", "php": "php", "dart": "dart",
    "gdscript": "gdscript", "c": "c", "cpp": "cpp", "erlang": "erlang",
}

# self → target's instance-reference; None means leave `self` alone.
SELF_FORM = {
    "rust": None, "java": "this", "kotlin": "this", "csharp": "this",
    "swift": None, "go": "s", "javascript": "this",
    "typescript": "this", "ruby": None, "lua": None,
    "php": "$this->", "dart": "this", "gdscript": None,
    "c": "self->", "cpp": "this->", "erlang": None,
}

# Type map. Frame source uses Python-ish type names (int/str/bool/list);
# backend codegen mostly translates, but some sources hardcode Python
# names and the per-language ports use idiomatic spellings. Map captured
# from existing fixtures.
TYPE_MAP = {
    "rust": {"int": "i32", "str": "String", "bool": "bool"},
    "java": {"int": "int", "str": "String", "bool": "boolean"},
    "kotlin": {"int": "Int", "str": "String", "bool": "Boolean"},
    "csharp": {"int": "int", "str": "string", "bool": "bool"},
    "swift": {"int": "Int", "str": "String", "bool": "Bool"},
    "go": {"int": "int", "str": "string", "bool": "bool"},
    "javascript": {"int": "number", "str": "string", "bool": "boolean"},
    "typescript": {"int": "number", "str": "string", "bool": "boolean"},
    "ruby": {"int": "int", "str": "string", "bool": "bool"},
    "lua": {"int": "int", "str": "string", "bool": "bool"},
    "php": {"int": "int", "str": "string", "bool": "bool"},
    "dart": {"int": "int", "str": "String", "bool": "bool"},
    "gdscript": {"int": "int", "str": "String", "bool": "bool"},
    "c": {"int": "int", "str": "string", "bool": "bool"},
    "cpp": {"int": "int", "str": "string", "bool": "bool"},
    "erlang": {"int": "int", "str": "string", "bool": "bool"},
}


def split_fpy(src: str) -> tuple[str, list[str], str, str]:
    """
    Split a .fpy file into (target_line, leading_comment_lines,
    system_block, driver_block).

    The system_block includes the `@@system ... { ... }` braces.
    The driver_block starts at the first `def ` or `import ` after
    the system block; it's the Python harness that exercises the system.
    """
    lines = src.splitlines(keepends=True)
    target_line = ""
    out_comments: list[str] = []
    i = 0
    n = len(lines)
    # Header: target + comments until first @@system
    while i < n:
        line = lines[i]
        if line.lstrip().startswith("@@[target("):
            target_line = line
            i += 1
            continue
        if line.lstrip().startswith("@@system"):
            break
        out_comments.append(line)
        i += 1
    # System block: balance braces from current line
    sys_start = i
    depth = 0
    started = False
    while i < n:
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        i += 1
        if started and depth == 0:
            break
    system_block = "".join(lines[sys_start:i])
    driver_block = "".join(lines[i:])
    return target_line, out_comments, system_block, driver_block


def parse_system_header(system_block: str) -> tuple[str, str]:
    """Return (system_name, param_list_text). param_list_text is
    everything inside `(...)` after the name, or empty if no params."""
    m = re.match(r"\s*@@system\s+(\w+)(?:\s*\(([^)]*)\))?", system_block)
    if not m:
        raise ValueError("Couldn't find @@system header")
    return m.group(1), (m.group(2) or "").strip()


def rewrite_self_in_system(system_block: str, backend: str) -> str:
    """Apply per-language self-reference substitution INSIDE handler
    bodies. Keep `self.name = x` in the domain initializer references
    alone (the codegen handles those) — only handler bodies need it.

    Heuristic: replace `self.` with the target's prefix everywhere
    inside the system block. The domain initializer's `seed: int = seed`
    pattern is OK because `seed` doesn't have `self.` prefix.
    """
    form = SELF_FORM[backend]
    if form is None or form == "self":
        return system_block
    # `self.x` → `<form>x` (note: form may end with `.` or `->`)
    # Java/C#/etc: this.x — replacement should be "this." not "this"
    # Go: s.x — replacement should be "s."
    # PHP: $this->x — replacement should be "$this->"
    # C: self->x — replacement should be "self->"
    # Cpp: this->x — replacement should be "this->"
    if form in ("this", "s"):
        replacement = f"{form}."
    elif form.endswith("->") or form.endswith("."):
        replacement = form
    else:
        replacement = f"{form}."
    return re.sub(r"\bself\.", replacement, system_block)


def rewrite_types_in_system(system_block: str, backend: str) -> str:
    """Replace bare type names: int, str, bool. Only within type-position
    contexts (after `:` and after `->` in method returns, or as the type
    annotation in domain fields `name: type = ...`).
    """
    type_map = TYPE_MAP[backend]
    out = system_block
    # Method-arg / return / domain-field type positions: `: int`, `: str`, etc.
    # Also `): int` for method return type.
    for src, dst in type_map.items():
        if src == dst:
            continue
        out = re.sub(rf"(?<=:\s)\b{src}\b", dst, out)
        out = re.sub(rf"(?<=->\s)\b{src}\b", dst, out)
    return out


def parse_python_driver(driver: str, system_name: str) -> dict:
    """
    Parse a Python driver block into a structured form.

    Returns a dict:
        {
            "ctor_args_by_var": {"r": "\"bot-1\"", "r2": "\"bot-2\""},
            "ctor_var_type": system name,
            "ops": [op...],
        }
    where op is one of:
        ("inst", var, args_text)             — var = @@System(args)
        ("call", var, method, args_text)     — var.method(args)
        ("check", label, var, method, args_text, expected)
              — check("label", var.method(args), "expected")

    Lines that don't match are passed through as ("raw", text).
    """
    ops: list = []
    ctor_args_by_var: dict[str, str] = {}

    re_check_call = re.compile(
        rf'check\("([^"]+)",\s*(\w+)\.(\w+)\(([^)]*)\),\s*"([^"]*)"\)\s*$'
    )
    re_check_call_int = re.compile(
        rf'check\("([^"]+)",\s*(\w+)\.(\w+)\(([^)]*)\),\s*(\d+)\)\s*$'
    )
    re_inst = re.compile(rf'(\w+)\s*=\s*@@{system_name}\(([^)]*)\)')
    re_call = re.compile(rf'(\w+)\.(\w+)\(([^)]*)\)\s*;?\s*$')

    for raw_line in driver.splitlines():
        line = raw_line.strip()
        if (
            not line
            or line.startswith("#")
            or line.startswith("def ")
            or line.startswith("import ")
            or line.startswith("import sys")
            or line.startswith("if __name__")
            or line.startswith("print(")
        ):
            continue
        # Handle compound `r.a(); r.b()` on one source line
        for sub in re.split(r"\s*;\s*", line):
            sub = sub.strip()
            if not sub or sub.startswith("#"):
                continue
            m_ck = re_check_call.match(sub) or re_check_call_int.match(sub)
            if m_ck:
                label, var, method, args, expected = m_ck.groups()
                ops.append(("check", label, var, method, args, expected))
                continue
            m_inst = re_inst.search(sub)
            if m_inst:
                var, args = m_inst.groups()
                ctor_args_by_var[var] = args
                ops.append(("inst", var, args))
                continue
            m_call = re_call.match(sub)
            if m_call:
                var, method, args = m_call.groups()
                ops.append(("call", var, method, args))
                continue
            # Unrecognized — record as raw (commented out in output)
            ops.append(("raw", sub))

    return {"ctor_args_by_var": ctor_args_by_var, "ops": ops}


# ---------------------------------------------------------------------
# Per-language driver emitters
# ---------------------------------------------------------------------

def emit_driver_rust(name: str, parsed: dict) -> str:
    out = []
    out.append("\nfn check(label: &str, actual: &str, expected: &str) {")
    out.append("    if actual != expected {")
    out.append('        println!("FAIL: {} expected \'{}\', got \'{}\'", label, expected, actual);')
    out.append("        std::process::exit(1);")
    out.append("    }")
    out.append("}\n")
    out.append("fn main() {")
    for op in parsed["ops"]:
        if op[0] == "inst":
            _, var, args = op
            args_rs = ", ".join(
                f"String::from({a.strip()})" if a.strip().startswith('"') else a.strip()
                for a in args.split(",") if a.strip()
            )
            out.append(f"    let mut {var} = @@{name}({args_rs});")
        elif op[0] == "call":
            _, var, method, args = op
            out.append(f"    {var}.{method}({args});")
        elif op[0] == "check":
            _, label, var, method, args, expected = op
            out.append(f'    check("{label}", &{var}.{method}({args}), "{expected}");')
        elif op[0] == "raw":
            out.append(f"    // {op[1]}")
    out.append(f'    println!("PASS: {name}");')
    out.append("}")
    return "\n".join(out) + "\n"


def emit_driver_javalike(name: str, parsed: dict, prologue: str = "",
                          class_keyword: str = "class Main",
                          main_sig: str = "    public static void main(String[] args)",
                          println: str = "System.out.println",
                          exit_form: str = "System.exit(1)",
                          var_kw: str = "var",
                          decl_form: str | None = None) -> str:
    """Shared shape for Java/C#/Kotlin/Swift/Dart/TS/JS/Cpp."""
    out = [prologue] if prologue else []
    out.append(f"{class_keyword} {{")
    out.append(f"    static void check(String label, String actual, String expected) {{")
    out.append(f"        if (!actual.equals(expected)) {{")
    out.append(f'            {println}("FAIL: " + label + " expected \'" + expected + "\', got \'" + actual + "\'");')
    out.append(f"            {exit_form};")
    out.append("        }")
    out.append("    }\n")
    out.append(f"{main_sig} {{")
    for op in parsed["ops"]:
        if op[0] == "inst":
            _, var, args = op
            out.append(f"        {var_kw} {var} = @@{name}({args});")
        elif op[0] == "call":
            _, var, method, args = op
            out.append(f"        {var}.{method}({args});")
        elif op[0] == "check":
            _, label, var, method, args, expected = op
            out.append(f'        check("{label}", {var}.{method}({args}), "{expected}");')
        elif op[0] == "raw":
            out.append(f"        // {op[1]}")
    out.append(f'        {println}("PASS: {name}");')
    out.append("    }")
    out.append("}")
    return "\n".join(out) + "\n"


def emit_driver_dynamic(name: str, parsed: dict, *, call: str = ".",
                        printer: str = "console.log", exit_form: str = "process.exit(1)",
                        var_kw: str = "const", check_concat: str = "+",
                        statement_terminator: str = ";",
                        line_join: str = "") -> str:
    """JS/TS/Dart/PHP/Ruby/Lua/GDScript share a flat-file structure."""
    out: list[str] = []
    t = statement_terminator
    # Helper fn
    out.append(f"function check(label, actual, expected) {{")
    out.append(f"    if (actual !== expected) {{")
    out.append(f'        {printer}("FAIL: " + label + " expected \'" + expected + "\', got \'" + actual + "\'"){t}')
    out.append(f"        {exit_form}{t}")
    out.append(f"    }}")
    out.append(f"}}\n")
    for op in parsed["ops"]:
        if op[0] == "inst":
            _, var, args = op
            out.append(f"{var_kw} {var} = @@{name}({args}){t}")
        elif op[0] == "call":
            _, var, method, args = op
            out.append(f"{var}{call}{method}({args}){t}")
        elif op[0] == "check":
            _, label, var, method, args, expected = op
            out.append(f'check("{label}", {var}{call}{method}({args}), "{expected}"){t}')
        elif op[0] == "raw":
            out.append(f"// {op[1]}")
    out.append(f'{printer}("PASS: {name}"){t}')
    return "\n".join(out) + "\n"


def emit_driver(name: str, parsed: dict, backend: str) -> str:
    """Dispatch to the per-backend driver emitter."""
    if backend == "rust":
        return emit_driver_rust(name, parsed)
    # The Family A/B/C dynamic + typed-OO shapes can mostly share form.
    # Default fallback: produce a JS-ish flat driver and let the user
    # post-edit. The matrix runner will surface anything that doesn't
    # compile.
    if backend in ("javascript", "typescript"):
        return emit_driver_dynamic(name, parsed)
    # For backends where this codemod doesn't have a robust template,
    # emit a stub with a TODO so the user knows the driver still needs
    # hand-finishing.
    out = [
        f"// TODO: driver for {backend} — codemod stub. Methods:",
    ]
    for op in parsed["ops"]:
        out.append(f"//   {op}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def transform(fpy_path: Path) -> dict[str, str]:
    src = fpy_path.read_text()
    target_line, comments, system_block, driver = split_fpy(src)
    name, params = parse_system_header(system_block)
    parsed = parse_python_driver(driver, name)
    out: dict[str, str] = {}
    for backend in BACKENDS:
        ann = f'@@[target("{TARGET[backend]}")]\n'
        sys_b = rewrite_self_in_system(system_block, backend)
        sys_b = rewrite_types_in_system(sys_b, backend)
        driver_b = emit_driver(name, parsed, backend)
        body = ann + "\n" + "".join(comments) + sys_b + "\n" + driver_b
        ext = EXT[backend]
        out[ext] = body
    return out


def main():
    if len(sys.argv) != 2:
        print("usage: port_recipe.py <fixture.fpy>", file=sys.stderr)
        sys.exit(2)
    fpy_path = Path(sys.argv[1])
    if not fpy_path.exists() or fpy_path.suffix != ".fpy":
        print(f"not a .fpy file: {fpy_path}", file=sys.stderr)
        sys.exit(2)
    outputs = transform(fpy_path)
    for ext, body in outputs.items():
        out_path = fpy_path.with_suffix("." + ext)
        out_path.write_text(body)
        print(f"  wrote {out_path}")


if __name__ == "__main__":
    main()
