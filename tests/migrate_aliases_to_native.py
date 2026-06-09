#!/usr/bin/env python3
"""Migrate portable-alias types (int/str/float/bool) to per-language native
types across the shared matrix corpus.

Background: framec's per-backend type-alias table was removed (framec
FRAMEC_BUGS #37) — Frame has no type system, type names pass through
verbatim. The shared corpus under tests/common/ was authored with portable
aliases (`int`/`str`) on the assumption that the table would render them
per-backend; under passthrough those leak as invalid types on the typed
backends (e.g. `str` → unsized in Rust). Each per-language source file
(.frs, .fc, …) should use that language's NATIVE type names. This rewrites
alias types in TYPE POSITIONS (after a `:`) to the native spelling for the
file's extension.

Usage:
    python3 migrate_aliases_to_native.py --dry-run   # report only
    python3 migrate_aliases_to_native.py             # apply
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "common")

# Per-extension native spelling for each portable alias. An identity entry
# (alias == native) is a no-op; empty dict = dynamic/untyped backend, leave
# the source untouched (the alias is already valid or annotations are dropped).
# These maps reproduce, as a one-time corpus rewrite, exactly what the
# (now-removed) per-backend framec type tables used to do — so the corpus
# ends up written in each language's native type names. `void`/`None` are
# intentionally NOT mapped: they're structural (a method's no-return form),
# still handled by the kept mapper arms (Kotlin `Unit`, Go empty, Swift
# `Void`) and valid as-is in C/C++/C#/Java.
# Each map mirrors EXACTLY the (now-removed) per-backend framec table's match
# arms — only the spellings that table translated, so we don't touch types
# already native to that language (e.g. Rust `i32`/`f64` are left alone; only
# Rust's actual aliases `int`/`str`/`float`/`number`/`Any` are rewritten).
# The statically-typed backends are migrated to native spellings. Dart and
# GDScript are included: they are typed enough that `str`/`list`/`dict`/`float`
# are not real type names (Dart uses `String`/`double`; GDScript uses
# `String`/`Array`/`Dictionary`), and framec no longer aliases them. The truly
# dynamic backends (Python/JS/TS/Ruby/Lua/PHP/Erlang) ignore type annotations,
# so any alias usage there is harmless and left untouched. `void`/`None` are
# structural (kept in the mappers) and intentionally not rewritten.
SUBS = {
    # rust: int→i64, float→f64, str|string|String→String, Any→String (i32/i64/f32/f64/bool native)
    "frs":    {"int": "i64", "float": "f64", "str": "String", "string": "String", "Any": "String"},
    # c: number|Any→int, float→double, str|string|String→char*, boolean→bool (int/bool/double native)
    "fc":     {"number": "int", "Any": "int", "float": "double", "str": "char*",
               "string": "char*", "String": "char*", "boolean": "bool"},
    # cpp: i32|i64|number→int, float|f64|f32→double, str|string|String→std::string, boolean→bool, Any→std::any
    "fcpp":   {"i32": "int", "i64": "int", "number": "int", "float": "double", "f64": "double",
               "f32": "double", "str": "std::string", "string": "std::string", "String": "std::string",
               "boolean": "bool", "Any": "std::any"},
    # csharp: i32|i64|number→int, float|f64|f32→double, str|string|String→string, boolean→bool, Any→object
    "fcs":    {"i32": "int", "i64": "int", "number": "int", "float": "double", "f64": "double",
               "f32": "double", "str": "string", "string": "string", "String": "string",
               "boolean": "bool", "Any": "object"},
    # java: i32|i64|number→int, float|f64|f32→double, str|string→String, bool→boolean, Any→Object
    "fjava":  {"i32": "int", "i64": "int", "number": "int", "float": "double", "f64": "double",
               "f32": "double", "str": "String", "string": "String", "bool": "boolean", "Any": "Object"},
    # go: i32|i64|number→int, float|f64|f32→float64, str|string|String→string, boolean→bool, Any|Object|object→any
    "fgo":    {"i32": "int", "i64": "int", "number": "int", "float": "float64", "f64": "float64",
               "f32": "float64", "str": "string", "string": "string", "String": "string",
               "boolean": "bool", "Any": "any", "Object": "any", "object": "any"},
    # kotlin: int|i32|i64|number→Int, float|f64|f32|double→Double, str|string|String→String,
    #         bool|boolean→Boolean, Any|Object|object→Any?
    "fkt":    {"int": "Int", "i32": "Int", "i64": "Int", "number": "Int", "float": "Double",
               "f64": "Double", "f32": "Double", "double": "Double", "str": "String", "string": "String",
               "bool": "Boolean", "boolean": "Boolean", "Any": "Any?", "Object": "Any?", "object": "Any?"},
    # swift: int|i32|i64|number→Int, float|f64|f32|double→Double, str|string|String→String,
    #        bool|boolean|Boolean→Bool, Object|object→Any  (Any native)
    "fswift": {"int": "Int", "i32": "Int", "i64": "Int", "number": "Int", "float": "Double",
               "f64": "Double", "f32": "Double", "double": "Double", "str": "String", "string": "String",
               "bool": "Bool", "boolean": "Bool", "Boolean": "Bool", "Object": "Any", "object": "Any"},
    # dart: str|string→String, float|number→double, list→List, map→Map (int/bool native)
    "fdart":  {"str": "String", "string": "String", "float": "double",
               "number": "double", "list": "List", "map": "Map"},
    # gdscript: str|string→String, list→Array, dict|map→Dictionary (int/float/bool native)
    "fgd":    {"str": "String", "string": "String", "list": "Array",
               "dict": "Dictionary", "map": "Dictionary"},
    # Truly dynamic backends — annotations are ignored, leave untouched:
    "fpy": {}, "fjs": {}, "fts": {}, "frb": {}, "flua": {}, "fphp": {}, "ferl": {},
}

# Only rewrite an alias when it appears in a TYPE POSITION — directly after a
# `:` (interface params, state args, state vars, domain fields, return types).
# This avoids touching identifiers, string literals, and expressions.
def rewrite(text, mapping):
    changed = 0
    for alias, native in mapping.items():
        if alias == native:
            continue
        # `(?<!:)` so we don't match the `:string` inside a native `std::string`
        # (the second colon of `::`) — that would double it to `std::std::string`.
        pat = re.compile(r"(?<!:)(:\s*)" + re.escape(alias) + r"\b")
        text, n = pat.subn(lambda m: m.group(1) + native, text)
        changed += n
    return text, changed


def main():
    dry = "--dry-run" in sys.argv
    total_files = 0
    total_subs = 0
    per_ext = {}
    for dirpath, _dirs, files in os.walk(ROOT):
        for fn in files:
            ext = fn.rsplit(".", 1)[-1]
            if ext not in SUBS or not SUBS[ext]:
                continue
            path = os.path.join(dirpath, fn)
            with open(path) as fh:
                src = fh.read()
            out, n = rewrite(src, SUBS[ext])
            if n:
                total_files += 1
                total_subs += n
                per_ext[ext] = per_ext.get(ext, 0) + n
                if not dry:
                    with open(path, "w") as fh:
                        fh.write(out)
    verb = "would change" if dry else "changed"
    print(f"{verb} {total_subs} type annotations across {total_files} files")
    for ext in sorted(per_ext):
        print(f"  .{ext}: {per_ext[ext]} substitutions")


if __name__ == "__main__":
    main()
