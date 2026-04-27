#!/usr/bin/env python3
"""Cross-backend structural diff audit.

Compiles a Frame fixture through every backend and extracts the
framec-emitted internal method/field names from each output. The
report flags any name that appears in some backends but not
others — those are real cross-backend divergences.

The 17 backends should align on these names because they're
framec-internal: the kernel, router, transition helpers, per-state
dispatchers, per-handler methods, and shared field names on
FrameEvent / FrameContext / Compartment. Authors don't see these
names; they exist purely so the runtime semantics match across
languages.

Usage:

    python3 tools/structural_audit.py [--fixture FILE] [--out REPORT.md]

Defaults: fixture = tests/common/positive/primary/49_hsm_enter_exit_params.fpy
Compiles into /tmp/struct_audit/<lang>/ and writes the report to
docs/structural_audit_report.md (or REPORT.md if specified).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


# Language → file extension(s) the framec output uses. Some
# backends emit multiple files (e.g., C emits .c + .h); we look at
# all of them.
LANG_EXTS: Dict[str, List[str]] = {
    "python_3":   [".py"],
    "typescript": [".ts"],
    "javascript": [".js"],
    "rust":       [".rs"],
    "c":          [".c", ".h"],
    "cpp":        [".cpp", ".hpp", ".h"],
    "csharp":     [".cs"],
    "java":       [".java"],
    "go":         [".go"],
    "php":        [".php"],
    "kotlin":     [".kt"],
    "swift":      [".swift"],
    "ruby":       [".rb"],
    "erlang":     [".erl"],
    "lua":        [".lua"],
    "dart":       [".dart"],
    "gdscript":   [".gd"],
}

# Framec-internal naming conventions. We extract any identifier
# that matches one of these patterns from each language's output.
FRAMEC_NAME_PATTERNS = [
    re.compile(r"\b(__\w+)"),                  # __kernel, __router, __transition, __hsm_chain, __compartment, __next_compartment, __sys_…, __compartment, __fire_enter_cascade, __fire_exit_cascade, __route_to_state, __prepareEnter, __prepareExit, __process_transition_loop, __push_transition
    re.compile(r"\b(_state_\w+)"),             # _state_<S>
    re.compile(r"\b(_s_\w+_hdl_\w+_\w+)"),     # _s_<S>_hdl_<kind>_<event>
    re.compile(r"\b(_context_stack)"),
    re.compile(r"\b(_state_stack)"),
    re.compile(r"\b(_return)"),
    re.compile(r"\b(_data)"),
    re.compile(r"\b(_transitioned)"),
    re.compile(r"\b(_message)"),
    re.compile(r"\b(_parameters)"),
    re.compile(r"\b(state_vars)"),
    re.compile(r"\b(state_args)"),
    re.compile(r"\b(enter_args)"),
    re.compile(r"\b(exit_args)"),
    re.compile(r"\b(forward_event)"),
    re.compile(r"\b(parent_compartment)"),
    re.compile(r"\b(frame_\w+__)"),            # Erlang: frame_transition__, frame_dispatch__, frame_enter__<s>, frame_exit__<s>, frame_arg_at__, frame_forward_transition__, frame_unwrap_forward__, frame_exit_dispatch__, frame_fire_enter_cascade__, frame_fire_exit_cascade__
    re.compile(r"\b(frame_current_state)"),    # Erlang field
    re.compile(r"\b(frame_enter_args)"),
    re.compile(r"\b(frame_exit_args)"),
    re.compile(r"\b(frame_state_args)"),
    re.compile(r"\b(frame_context_stack)"),
    re.compile(r"\b(frame_return_val)"),
    re.compile(r"\b(frame_stack)"),
]


# Names that look framec-internal but are actually language-native
# idioms. We strip these before reporting so the divergence list
# only contains framec-named identifiers.
LANGUAGE_IDIOMS = {
    "__name__", "__main__",                    # Python
    "__init__",                                # Python (constructor)
    "__construct",                             # PHP (constructor)
    "__index",                                 # Lua (metatable method)
}


# Local-variable names that framec emits inside method bodies — they're
# framec-prefixed but they're not part of the public structural shape
# (they're scratch bindings, not method or field names). The audit
# focuses on shapes that authors and other backends might depend on,
# so locals get filtered.
LOCAL_VAR_NAMES = {
    "__e", "__ea", "__sa", "__ctx", "__chain", "__i", "__next",
    "__result", "__result_ctx", "__rv", "__return_val",
    "__frame_event", "__skipInitialEnter",
    "__Event", "__ReturnVal_1",                # Erlang locals
    # Rust scratch locals (transition expansion, state-var write-through).
    "__c", "__cursor", "__rhs", "__rs_tmp_arg", "__sv_comp",
    "__ctx_event",
    # Persist serialize/deserialize locals — these are private helper
    # variables inside the @@persist-emitted serialization code and
    # vary by backend (each backend uses its own naming idioms for
    # local cursors, intermediate values, JSON document handles, etc).
    # Not part of the cross-backend structural shape.
    "__cj", "__sc", "__ser", "__deser", "__sv", "__doc", "__opts",
    "__root", "__name", "__value", "__instance", "__j", "__stack",
    "__SerComp", "__DeserComp", "__ser_comp", "__deser_comp",
    "__serComp", "__deserComp",
}


# C uses a `<SystemName>_<role>` prefix instead of `__<role>`. The
# `c` and `cpp` extensions of `__kernel`, `__router`, etc. show up
# under names like `HSMEnterExitParams_kernel`. We accept this as
# an intentional naming-convention divergence (documented in the
# runtime spec) — verifying *role completeness* in C is out of
# scope for this script.
KNOWN_INTENTIONAL_DIVERGENCES = {
    # Backend → reason
    "c": "uses `<SystemName>_<role>` prefix instead of `__<role>` "
         "(role-completeness check is out-of-scope; see the C "
         "backend documentation).",
    "erlang": "built on gen_statem instead of a custom kernel "
              "(uses `frame_*__/N` helpers + `frame_<field>` "
              "data record fields; see runtime-capability-matrix "
              "footnotes [a], [b], [c]).",
}

# Names that some specific backends rename to match their language's
# style conventions. The audit treats these as intentional renames
# rather than divergences. Map: canonical-name → set of backends that
# use a non-canonical form, with a one-line explanation per pair.
KNOWN_RENAMES = {
    "_message": {
        "rust": "Rust uses `message` (no underscore) on its FrameEvent struct; idiomatic Rust style.",
    },
    "_parameters": {
        "rust": "Rust uses `parameters` (no underscore) on its FrameEvent struct; idiomatic Rust style.",
    },
    "parent_compartment": {
        "go": "Go uses `parentCompartment` (camelCase); standard Go field-naming convention.",
    },
    "state_args": {
        "rust": "Rust uses a typed `state_context: <System>StateContext` enum instead of a generic list — "
                "different by design (see runtime-capability-matrix entry for HSM parameter propagation).",
    },
    "state_vars": {
        "rust": "Rust uses typed struct fields per state (one struct per state's vars) inside the typed StateContext enum.",
        "go": "Go uses `stateVars` (camelCase); standard Go field-naming convention.",
    },
    "__hsm_chain": {
        # Rust emits `__hsm_chain` as a method on the system. Other
        # backends use either:
        #   - `hsm_chain()` method without underscore prefix (Go,
        #     C++, Java, Kotlin, Swift, C#, Dart) — a language-style
        #     rename of the same role.
        #   - `_HSM_CHAIN` class-level static dict (Python, TS, JS,
        #     Lua, Ruby, PHP, GDScript) — same lookup table baked
        #     in as constant data instead of a method.
        # Both shapes are equivalent: a per-leaf-state ancestry
        # lookup. Rust's `__hsm_chain` follows the framec-internal
        # double-underscore convention; the other forms are
        # language-idiomatic alternatives.
        "cpp": "uses `hsm_chain()` (no underscore prefix); language-style.",
        "csharp": "uses `hsm_chain()`; language-style.",
        "dart": "uses `hsm_chain()`; language-style.",
        "go": "uses `hsm_chain()`; language-style.",
        "java": "uses `hsm_chain()`; language-style.",
        "kotlin": "uses `hsm_chain()`; language-style.",
        "swift": "uses `hsm_chain()`; language-style.",
        "gdscript": "uses `_HSM_CHAIN` class-level static dict.",
        "javascript": "uses `_HSM_CHAIN` static dict.",
        "lua": "uses `_HSM_CHAIN` table at module scope.",
        "php": "uses `_HSM_CHAIN` static array.",
        "python_3": "uses `_HSM_CHAIN` class-level static dict.",
        "ruby": "uses `_HSM_CHAIN` constant.",
        "typescript": "uses `_HSM_CHAIN` static dict.",
    },
}


def extract_names(source: str) -> Set[str]:
    """Return framec-named identifiers found in `source`, with
    language idioms and local-variable names filtered out."""
    names: Set[str] = set()
    for pat in FRAMEC_NAME_PATTERNS:
        for m in pat.finditer(source):
            names.add(m.group(1))
    return names - LANGUAGE_IDIOMS - LOCAL_VAR_NAMES


# Patterns that should appear in any non-trivial framec emission.
# If NONE of these appear in the output, the @@system block was almost
# certainly NOT compiled — the source passed through as native code.
# This happens when the fixture contains target-language-incompatible
# syntax in its prolog/epilog (e.g., apostrophes in Python `#` comments
# confusing the TS/Rust/etc. unified scanner's string-mode tracking,
# which then silently consumes the @@system block as "string content").
COMPILE_SUCCESS_MARKERS = re.compile(
    r"(_state_\w+|__kernel|__router|__transition|frame_dispatch__|"
    r"\w+_kernel\b|\w+_router\b)"
)


def compile_fixture(framec: Path, fixture: Path, out_dir: Path) -> Dict[str, Path]:
    """Run framec for each lang. Returns lang → list of output files
    (or empty list if the compile failed)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    lang_outputs: Dict[str, List[Path]] = {}
    fixture_size = fixture.stat().st_size
    for lang in LANG_EXTS:
        lang_dir = out_dir / lang
        if lang_dir.exists():
            shutil.rmtree(lang_dir)
        lang_dir.mkdir(parents=True)
        proc = subprocess.run(
            [str(framec), "compile", "-l", lang, "-o", str(lang_dir), str(fixture)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(f"  {lang}: TRANSPILE FAIL: {proc.stderr.splitlines()[0] if proc.stderr else proc.stdout.splitlines()[0]}", file=sys.stderr)
            lang_outputs[lang] = []
            continue
        files = []
        for ext in LANG_EXTS[lang]:
            files.extend(lang_dir.rglob(f"*{ext}"))
        if not files:
            print(f"  {lang}: NO OUTPUT", file=sys.stderr)
            lang_outputs[lang] = []
            continue
        # Sanity: detect silent-passthrough where the @@system block
        # was treated as native code. If the output contains no framec
        # internal marker (kernel/router/per-state dispatcher), the
        # backend's unified scanner mis-segmented the source — flag
        # as compile-failed rather than letting it skew the audit.
        # Common cause: apostrophes in source-language `#` comments
        # outside the @@system block confuse the target's unified
        # scanner string-mode (TS/Rust/C/etc. treat `'` as a string
        # opener), which then consumes the @@system block as
        # "string content".
        combined = "\n".join(f.read_text(errors="replace") for f in files)
        out_size = sum(f.stat().st_size for f in files)
        if not COMPILE_SUCCESS_MARKERS.search(combined):
            print(
                f"  {lang}: SILENT PASSTHROUGH (no framec markers in "
                f"{out_size}B output; fixture's native code likely "
                f"confused the {lang} unified scanner — pick a fixture "
                f"with no apostrophes in source-language comments)",
                file=sys.stderr,
            )
            lang_outputs[lang] = []
            continue
        lang_outputs[lang] = files
        print(f"  {lang}: {len(files)} file(s), {out_size} bytes")
    return lang_outputs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--fixture", default=None, help="Frame source file (default: 49_hsm_enter_exit_params.fpy)")
    p.add_argument("--out", default=None, help="Report output path (default: docs/structural_audit_report.md)")
    p.add_argument("--framec", default=None, help="Path to framec binary")
    p.add_argument("--workdir", default="/tmp/struct_audit", help="Work directory for compiled outputs")
    args = p.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    fixture = Path(args.fixture) if args.fixture else (
        repo_root / "tests" / "common" / "positive" / "primary"
        / "49_hsm_enter_exit_params.fpy"
    )
    out_path = Path(args.out) if args.out else (
        repo_root / "docs" / "structural_audit_report.md"
    )
    workdir = Path(args.workdir)
    framec = Path(args.framec) if args.framec else (
        Path("/Users/marktruluck/projects/framepiler/target/release/framec")
    )

    if not fixture.exists():
        print(f"fixture not found: {fixture}", file=sys.stderr)
        return 2
    if not framec.exists():
        print(f"framec not found: {framec}", file=sys.stderr)
        return 2

    print(f"# Structural audit\n")
    print(f"Fixture: {fixture.relative_to(repo_root) if fixture.is_relative_to(repo_root) else fixture}")
    print(f"Workdir: {workdir}")
    print(f"")
    print(f"## Compiling fixture to all 17 backends\n")
    lang_outputs = compile_fixture(framec, fixture, workdir)

    # Extract names per language.
    print(f"\n## Extracting framec-emitted names per backend\n")
    names_per_lang: Dict[str, Set[str]] = {}
    for lang, files in lang_outputs.items():
        if not files:
            names_per_lang[lang] = set()
            continue
        text = "\n".join(f.read_text() for f in files)
        names_per_lang[lang] = extract_names(text)
        print(f"  {lang}: {len(names_per_lang[lang])} unique framec-named identifiers")

    # Build cross-language matrix: name → set of langs that have it.
    name_to_langs: Dict[str, Set[str]] = defaultdict(set)
    for lang, names in names_per_lang.items():
        for n in names:
            name_to_langs[n].add(lang)

    all_langs = set(LANG_EXTS.keys())

    # Backends that failed to compile this fixture (transpile error,
    # no output, or silent passthrough). Exclude them from the
    # "missing" calculation — a divergence flagged because Java
    # couldn't transpile the fixture isn't a codegen alignment bug,
    # it's a fixture-feature/backend mismatch that's reported
    # separately as the per-backend identifier count of 0.
    failed_compile_langs = {
        lang for lang, files in lang_outputs.items() if not files
    }

    # Subtract the intentionally-divergent backends from the "universal"
    # check so we measure alignment across the 15 backends that share
    # the standard kernel-and-dispatcher shape.
    intentional_divergent = set(KNOWN_INTENTIONAL_DIVERGENCES.keys())
    standard_langs = all_langs - intentional_divergent - failed_compile_langs

    universal_names = sorted(
        n for n, langs in name_to_langs.items() if langs == all_langs
    )
    universal_in_standard = sorted(
        n for n, langs in name_to_langs.items()
        if (langs & standard_langs) == standard_langs
        and n not in universal_names
    )
    erlang_specific = sorted(
        n for n, langs in name_to_langs.items()
        if langs == {"erlang"}
    )
    # Rust elides synthetic empty enter/exit handlers — when a state
    # has no `$>(…)` or `<$(…)` declared, Rust skips emitting the
    # `_s_<S>_hdl_frame_enter` / `_s_<S>_hdl_frame_exit` method
    # entirely (the cascade dispatcher checks for the variant before
    # calling). Other backends emit a no-op method placeholder. Both
    # produce equivalent runtime behavior; it's a per-backend code-
    # size optimization. Treat any `_s_<S>_hdl_frame_enter|exit` that
    # is "missing only from Rust" as a documented rename, not a bug.
    rust_elides_synthetic_handler = re.compile(
        r"^_s_\w+_hdl_frame_(enter|exit)$"
    )

    real_divergences: List = []
    documented_renames: List = []
    for n, langs in name_to_langs.items():
        if langs == all_langs:
            continue
        if (langs & standard_langs) == standard_langs:
            continue
        if langs == {"erlang"} or langs == {"c"}:
            continue
        missing = standard_langs - langs
        # Rust elides synthetic empty enter/exit handlers (see comment
        # above). Treat as documented rename when the only backend
        # missing the name is Rust AND the name matches the synthetic
        # handler pattern.
        if missing == {"rust"} and rust_elides_synthetic_handler.match(n):
            documented_renames.append((n, langs, {
                "rust": "Rust elides synthetic empty enter/exit handlers; "
                        "the cascade dispatcher checks for the variant before "
                        "calling. Other backends emit a no-op method placeholder.",
            }))
            continue
        # Filter: is the missing-from set fully explained by KNOWN_RENAMES?
        rename_info = KNOWN_RENAMES.get(n, {})
        if rename_info and missing.issubset(set(rename_info.keys())):
            documented_renames.append((n, langs, rename_info))
        else:
            real_divergences.append((n, langs))
    real_divergences.sort(key=lambda x: x[0])
    documented_renames.sort(key=lambda x: x[0])
    c_specific = sorted(
        n for n, langs in name_to_langs.items()
        if langs == {"c"}
    )

    # Emit report.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# Cross-backend structural audit\n")
    lines.append(f"Fixture: `{fixture.name}`")
    lines.append("")
    lines.append("Compiles a representative Frame source through all 17 backends, "
                 "extracts every framec-internal identifier (kernel methods, "
                 "per-state dispatchers, per-handler methods, shared field names), "
                 "and surfaces any name that appears in some backends but not others.")
    lines.append("")
    lines.append("Generated by `tools/structural_audit.py`. Re-run any time to "
                 "verify the alignment after codegen changes.")
    lines.append("")
    lines.append(f"## Summary\n")
    n_compiled = sum(1 for v in lang_outputs.values() if v)
    lines.append(f"- Backends compiled: **{n_compiled} / {len(LANG_EXTS)}**")
    if failed_compile_langs:
        lines.append(
            f"- Backends that did NOT compile this fixture: "
            f"**{len(failed_compile_langs)}** ({', '.join(sorted(failed_compile_langs))}) "
            f"— excluded from divergence calculation."
        )
    lines.append(f"- Standard backends (kernel-and-dispatcher shape, compiled OK): **{len(standard_langs)}** ({', '.join(sorted(standard_langs))})")
    lines.append(f"- Intentionally-divergent backends: **{len(intentional_divergent)}** ({', '.join(sorted(intentional_divergent))})")
    lines.append("")
    lines.append(f"- Universal across all 17 backends: **{len(universal_names)}**")
    lines.append(f"- Universal across the {len(standard_langs)} compiled standard backends: **{len(universal_in_standard)}**")
    lines.append(f"- Erlang-only (gen_statem-native): **{len(erlang_specific)}**")
    lines.append(f"- C-only (system-prefix-named): **{len(c_specific)}** _(role-completeness verified separately)_")
    lines.append(f"- Documented language-style renames (Rust/Go/etc): **{len(documented_renames)}**")
    lines.append(f"- **Real cross-backend divergences (potential bugs): {len(real_divergences)}**")
    lines.append("")

    lines.append("## Per-backend identifier counts\n")
    lines.append("| Lang | # framec names | Notes |")
    lines.append("|---|---|---|")
    for lang in LANG_EXTS:
        notes = KNOWN_INTENTIONAL_DIVERGENCES.get(lang, "")
        if not lang_outputs.get(lang):
            lines.append(f"| {lang} | (compile failed) | {notes} |")
        else:
            lines.append(f"| {lang} | {len(names_per_lang[lang])} | {notes} |")
    lines.append("")

    lines.append("## Universal names (in every backend, all 17)\n")
    if universal_names:
        for n in universal_names:
            lines.append(f"- `{n}`")
    else:
        lines.append("_(none — every name diverges across at least one backend; this is normal "
                     "since C and Erlang use different naming conventions)_")
    lines.append("")

    lines.append(f"## Universal names across the {len(standard_langs)} compiled standard backends\n")
    lines.append("These exist in every backend that uses the kernel-and-dispatcher shape "
                 "and successfully compiled this fixture (C and Erlang excluded — C uses "
                 "`<SystemName>_<role>` prefix; Erlang is gen_statem-native; backends that "
                 "failed to compile or silently passed-through the fixture are also excluded).")
    lines.append("")
    if universal_in_standard:
        for n in universal_in_standard:
            lines.append(f"- `{n}`")
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("## Erlang-specific names (gen_statem-native)\n")
    lines.append("Expected per the runtime-capability-matrix footnotes. Listed for completeness.")
    lines.append("")
    for n in erlang_specific:
        lines.append(f"- `{n}`")
    lines.append("")

    lines.append("## C-specific names\n")
    lines.append("C is system-prefix-named so most kernel/router/dispatcher functions appear "
                 "under names like `<SystemName>_kernel` rather than `__kernel`. The names "
                 "below are scratch local variables that leak into the audit; they're benign.")
    lines.append("")
    for n in c_specific:
        lines.append(f"- `{n}`")
    lines.append("")

    lines.append("## Documented renames (intentional naming-style divergences)\n")
    lines.append("Names that SOME standard backends rename to fit their language's "
                 "style (Rust's no-underscore convention, Go's camelCase, etc). "
                 "These are intentional and tracked in `KNOWN_RENAMES` in the audit "
                 "script.")
    lines.append("")
    if documented_renames:
        for name, langs, rename_info in documented_renames:
            missing = sorted(standard_langs - langs)
            lines.append(f"### `{name}`")
            lines.append("")
            for renaming_lang in missing:
                reason = rename_info.get(renaming_lang, "(no documented reason — please update KNOWN_RENAMES)")
                lines.append(f"- **{renaming_lang}**: {reason}")
            lines.append("")
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("## Real cross-backend divergences (potential bugs)\n")
    lines.append("Names emitted by some-but-not-all-of-the-15-standard backends, NOT "
                 "explained by Erlang's gen_statem-native shape, C's system-prefix "
                 "naming, or a documented rename. Each row deserves a look: it could "
                 "be a backend-specific helper that's intentionally narrow, OR a real "
                 "codegen inconsistency.")
    lines.append("")
    if real_divergences:
        lines.append("| Name | Present in | Missing from |")
        lines.append("|---|---|---|")
        for name, langs in real_divergences:
            missing = sorted(standard_langs - langs)
            present = sorted(langs & standard_langs)
            pres = ", ".join(present) if len(present) <= 6 else f"{', '.join(present[:6])}, +{len(present)-6} more"
            miss = ", ".join(missing) if len(missing) <= 6 else f"{', '.join(missing[:6])}, +{len(missing)-6} more"
            lines.append(f"| `{name}` | {pres} | {miss} |")
    else:
        lines.append("**None.** Full structural alignment across the 15 standard backends "
                     "(modulo documented language-style renames above).")
    lines.append("")

    out_path.write_text("\n".join(lines) + "\n")
    print(f"\nReport written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
