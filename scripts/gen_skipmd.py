#!/usr/bin/env python3
"""
Batch-generate `<stem>.f<ext>.skip.md` files for fixtures that are
intentionally not ported to certain backends.

Each batch entry is a dict:
  - stem_path  : path under tests/common/positive (e.g.
                 "primary/52_hsm_state_arg_propagation")
  - real_exts  : list of backends with real ports (e.g. ["frs"])
  - title      : short markdown H1 for the skip.md
  - body       : markdown body explaining why this fixture is
                 intentionally skipped on the other backends

The 16 missing backends each get an identical `<stem>.<ext>.skip.md`
file. The skip text is uniform — the reason is "this fixture is
target-specific by design", not per-backend.

Run: scripts/gen_skipmd.py
Reads the BATCHES list at the bottom of this file. Idempotent: skips
any `.skip.md` that already exists.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POSITIVE_DIR = REPO_ROOT / "tests" / "common" / "positive"

# Erlang (`ferl`) is deprecated and no longer part of the enforced backend
# set (see scripts/check_coverage.py) — do not emit new `.ferl.skip.md`.
ALL_BACKENDS: tuple[str, ...] = (
    "fc", "fcpp", "fcs", "fdart", "fgd", "fgo", "fjava",
    "fjs", "fkt", "flua", "fphp", "fpy", "frb", "frs", "fswift", "fts",
)


@dataclass
class SkipBatch:
    stem_path: str       # e.g. "primary/52_hsm_state_arg_propagation"
    real_exts: list[str]  # backends that have real ports, e.g. ["frs"]
    title: str
    body: str


def render_skip_md(batch: SkipBatch) -> str:
    return f"# {batch.title}\n\n{batch.body.rstrip()}\n"


def run(batches: list[SkipBatch]) -> int:
    total_created = 0
    total_existed = 0
    for batch in batches:
        content = render_skip_md(batch)
        for ext in ALL_BACKENDS:
            if ext in batch.real_exts:
                continue
            target = POSITIVE_DIR / f"{batch.stem_path}.{ext}.skip.md"
            if target.exists():
                total_existed += 1
                continue
            target.write_text(content)
            total_created += 1
        print(f"  {batch.stem_path}: {len(ALL_BACKENDS) - len(batch.real_exts)} backends")
    print()
    print(f"Created: {total_created}   Already existed (idempotent skip): {total_existed}")
    return 0


# ---------------------------------------------------------------------------
# Shared skip-reason text — same wording reused across many stems with
# the same skip rationale.
# ---------------------------------------------------------------------------

_C_ONLY_BODY = (
    "C-codegen-specific regression net. The bug or behavior it "
    "guards against was specific to the C backend's pointer-based "
    "dispatch, native-function passthrough, or lifecycle-stack "
    "handling. Other backends didn't share the same code path.\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_RUST_ONLY_BODY = (
    "Rust-codegen-specific regression net. The bug or behavior it "
    "guards against was specific to Rust's borrow-checker, typed-"
    "domain handling, or factory-call path. Other backends didn't "
    "share the same code path.\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_SEGMENTER_UNIFORM_BODY = (
    "The segmenter's tokenization / brace-handling / comment-"
    "tracking logic is target-uniform within each comment-syntax "
    "family. The matrix corpus has fixtures in the `//` C-family "
    "(c, cpp, dart, js, swift, ts — 6 fixtures), the `#` family "
    "(gd, py, rb, lua — 4), and the `%` family (erl — 1). Adding "
    "this backend's fixture would duplicate coverage that already "
    "exists in its comment-syntax family.\n\n"
    "See `docs/partial-coverage-audit.md`."
)


def c_only(stem_path: str) -> SkipBatch:
    return SkipBatch(
        stem_path=stem_path,
        real_exts=["fc"],
        title="Intentional skip — C-only regression net",
        body=_C_ONLY_BODY,
    )


def rust_only(stem_path: str) -> SkipBatch:
    return SkipBatch(
        stem_path=stem_path,
        real_exts=["frs"],
        title="Intentional skip — Rust-only regression net",
        body=_RUST_ONLY_BODY,
    )


def segmenter_skip(stem_path: str, real: list[str]) -> SkipBatch:
    return SkipBatch(
        stem_path=stem_path,
        real_exts=real,
        title="Intentional skip — segmenter coverage target-uniform",
        body=_SEGMENTER_UNIFORM_BODY,
    )


def skip_only(stem_path: str, skip_exts: list[str], title: str,
              body: str) -> SkipBatch:
    """Build a SkipBatch by naming the backends to SKIP (the inverse of
    real_exts). Convenient when most backends have real ports and only a
    few are intentionally absent."""
    real = [e for e in ALL_BACKENDS if e not in skip_exts]
    return SkipBatch(stem_path=stem_path, real_exts=real, title=title,
                     body=body)


# Shared reasons reused across several stems.
_ERLANG_MULTI_BODY = (
    "Erlang requires one `-module` per file (framec E431), so a "
    "multi-system / nested-`@@SystemName` fixture cannot be expressed "
    "in a single `.ferl`. The same behavior is exercised end-to-end "
    "via the multi-source layout under `tests/erlang/multi/` (one "
    "`.ferl` per module + a shared `driver.escript`); persist recurses "
    "through child gen_statem process trees. See capability-matrix "
    "footnotes [k]/[p].\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_JAVA_ERLANG_MULTI_BODY = (
    "Multi-system-per-file fixture. Java requires one public class per "
    "file (framec E430) and Erlang one `-module` per file (E431), so "
    "neither can host multiple `@@system` declarations in a single "
    "source file. Cross-system composition is exercised for both via "
    "the multi-source layouts under `tests/java/multi/` and "
    "`tests/erlang/multi/`. See capability-matrix footnotes [j]/[k].\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_C_NO_COLLECTION_BODY = (
    "C has no built-in list/dict type (capability-matrix footnote [l]), "
    "so a list-/dict-typed *state argument* has no idiomatic C "
    "representation to thread through the typed state-context path this "
    "fixture probes. The 16 backends with native collections cover the "
    "compound-state-arg path uniformly; C's compound-type persistence is "
    "exercised separately by `102_persist_domain_list_dict` via the "
    "symbol-mangled pack/unpack helpers.\n\n"
    "See `docs/partial-coverage-audit.md`."
)


# ---------------------------------------------------------------------------
# Batches — one entry per single-target fixture in framework dirs (not
# cookbook dirs scientific/security/robotics/parser_specialists, which
# belong to the cookbook port agent).
# ---------------------------------------------------------------------------

BATCHES: list[SkipBatch] = [
    # === primary/ audit-verified single-target fixtures ===
    SkipBatch(
        stem_path="primary/52_hsm_state_arg_propagation",
        real_exts=["frs"],
        title="Intentional skip — Rust-only regression net",
        body=(
            "This fixture is a Rust-only regression net for the D5 "
            "cascade-visibility fix. The bug it guards against was "
            "specific to Rust's compartment-mutation path; other "
            "backends had different cascade behavior and aren't "
            "covered by the same regression.\n\n"
            "See `docs/partial-coverage-audit.md` for the audit "
            "entry."
        ),
    ),
    SkipBatch(
        stem_path="primary/55_nested_frame_args",
        real_exts=["fpy"],
        title="Intentional skip — Python-only smoke fixture",
        body=(
            "Python-only smoke fixture for nested `@@SystemName($(arg))` "
            "call resolution. No regression coverage value on other "
            "backends since the codegen path is target-agnostic.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),
    SkipBatch(
        stem_path="primary/99_persist_param_child",
        real_exts=["fgd"],
        title="Intentional skip — GDScript-specific regression",
        body=(
            "GDScript-only regression for the parameterized-child × "
            "domain-init fix (`#328` in framec memory). The bug was "
            "GDScript-codegen-specific; other backends already "
            "handled the case correctly.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),
    SkipBatch(
        stem_path="primary/106_hsm_3deep_cascade",
        real_exts=["fpy"],
        title="Intentional skip — Python-only RFC-0019 smoke",
        body=(
            "Python smoke fixture covering 3-deep HSM cascade per "
            "RFC-0019 (`#408` in framec memory). Same cascade "
            "behavior is exercised across all 17 backends by the "
            "matrix's broader HSM tests (tests 46, 47, 48, 49, 53, "
            "61, 62 etc.).\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === interfaces/ audit-verified single-target ===
    SkipBatch(
        stem_path="interfaces/return_typed",
        real_exts=["fts"],
        title="Intentional skip — TypeScript-specific edge case",
        body=(
            "TypeScript-only fixture for a TS-parser quirk in typed "
            "return-value handling. Not a feature test — a "
            "regression net for one specific TS codegen path.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === capabilities/ audit-verified single-target ===
    SkipBatch(
        stem_path="capabilities/nested_functions",
        real_exts=["fc"],
        title="Intentional skip — C-only test",
        body=(
            "C-only test for nested-function handling in native "
            "prolog. C is the only target where the issue surfaces; "
            "other backends handle nested helper functions via their "
            "native scoping rules without Frame-side intervention.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === core/ — C-only regression nets ===
    c_only("core/forward_multi_native"),
    c_only("core/forward_then_native_exec"),
    c_only("core/terminal_last_stack_ops"),
    c_only("core/transition_basic"),
    c_only("core/transition_state_args_exec"),
    c_only("core/transition_state_id_exec"),

    # === systems/ — C-only regression nets ===
    c_only("systems/if_forward_exec"),
    c_only("systems/interface_with_param"),
    c_only("systems/simple_interface"),
    c_only("systems/system_return_header_defaults"),
    c_only("systems/transition_basic_exec"),

    # === systems/ — Rust-only regression net ===
    rust_only("systems/handler_outside_state"),

    # === validator/ — C-only regression nets ===
    c_only("validator/terminal_last_forward"),
    c_only("validator/terminal_last_transition"),

    # === segmenter/ — target-uniform within comment-syntax family ===
    segmenter_skip(
        "segmenter/frame_tokens_in_comments",
        ["fc", "fcpp", "fdart", "ferl", "fgd", "fjs", "flua",
         "fpy", "frb", "frs", "fswift", "fts"],
    ),
    segmenter_skip(
        "segmenter/heavy_native_prolog",
        ["fc", "fcpp", "fdart", "ferl", "fgd", "fjs", "flua",
         "fpy", "frb", "frs", "fswift", "fts"],
    ),
    segmenter_skip(
        "segmenter/nested_braces",
        ["fc", "fcpp", "fdart", "ferl", "fgd", "fjs", "flua",
         "fpy", "frb", "frs", "fswift", "fts"],
    ),

    # === interfaces/ — dynamic-only return-type inference ===
    SkipBatch(
        stem_path="interfaces/return_no_type_annotation",
        real_exts=["fgd", "fjs", "flua", "fphp", "fpy", "frb"],
        title="Intentional skip — dynamic-typed targets only",
        body=(
            "Tests Frame's allowance of return without a type "
            "annotation on the interface method. Only meaningful on "
            "dynamically typed targets (Python, JS, Ruby, Lua, PHP, "
            "GDScript) where return types are inferred at runtime. "
            "Typed targets (Java, Kotlin, Swift, C#, C, C++, Go, "
            "Rust, Dart, TS) require explicit return-type "
            "annotations as part of their host-language grammar — a "
            "Frame fixture missing the annotation cannot transpile.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === primary/81 — async-native targets only ===
    SkipBatch(
        stem_path="primary/81_persist_async_basic",
        real_exts=["fcpp", "fcs", "fgd", "fgo", "fjava", "fjs",
                   "fkt", "fpy", "frs", "fswift", "fts"],
        title="Intentional skip — async-native targets only",
        body=(
            "Persist × async cross-product fixture. Limited to "
            "backends with native async/await primitives that "
            "Frame's async codegen targets: C++ (coroutines), C# "
            "(async/await), GDScript (await), Go (goroutines + "
            "channels), Java (CompletableFuture), JS/TS "
            "(async/await), Kotlin (coroutines), Python "
            "(asyncio), Rust (async fn), Swift (async/await).\n\n"
            "C, Dart, Erlang, Lua, PHP, Ruby do not have a "
            "consistent native-async target shape that Frame "
            "currently emits to (per the per-language capability "
            "matrix); no port for them.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === primary/101 — dynamically-typed int/float fidelity (single-target) ===
    SkipBatch(
        stem_path="primary/101_persist_int_fidelity",
        real_exts=["fgd", "flua"],
        title="Intentional skip — dynamic int/float fidelity only",
        body=(
            "Probes the int-vs-float representation ambiguity that only "
            "arises on dynamically-typed backends: after a persist "
            "round-trip, does an integer domain field deserialize back "
            "as an int (not a float)? GDScript and Lua are the two "
            "dynamic backends where the JSON number path can silently "
            "promote `42` to `42.0`. On statically-typed backends the "
            "field's declared type pins the representation, so there is "
            "nothing to probe.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === primary/ list & dict state-args — C has no native collection ===
    skip_only("primary/73_list_state_arg", ["fc"],
              "Intentional skip — C has no native list type",
              _C_NO_COLLECTION_BODY),
    skip_only("primary/75_nested_list_state_arg", ["fc"],
              "Intentional skip — C has no native list type",
              _C_NO_COLLECTION_BODY),
    skip_only("primary/78_nested_dict_state_arg", ["fc"],
              "Intentional skip — C has no native dict type",
              _C_NO_COLLECTION_BODY),
    skip_only("primary/79_dict_of_list_state_arg", ["fc"],
              "Intentional skip — C has no native list/dict type",
              _C_NO_COLLECTION_BODY),
    skip_only("primary/80_list_of_dict_state_arg", ["fc"],
              "Intentional skip — C has no native list/dict type",
              _C_NO_COLLECTION_BODY),

    # === primary/ nested & multi-instance persist — Erlang one-module-per-file ===
    skip_only("primary/84_persist_nested_hsm", ["ferl"],
              "Intentional skip — Erlang one module per file",
              _ERLANG_MULTI_BODY),
    skip_only("primary/85_persist_three_level_nested", ["ferl"],
              "Intentional skip — Erlang one module per file",
              _ERLANG_MULTI_BODY),
    skip_only("primary/86_persist_numeric_typing", ["ferl"],
              "Intentional skip — Erlang one module per file",
              _ERLANG_MULTI_BODY),
    skip_only("primary/87_persist_multi_instance", ["ferl"],
              "Intentional skip — Erlang one module per file",
              _ERLANG_MULTI_BODY),

    # === primary/88 — Erlang quiescent enforcement is implicit ===
    skip_only(
        "primary/88_persist_quiescent_error", ["ferl"],
        "Intentional skip — Erlang quiescent contract is implicit",
        (
            "Erlang enforces the quiescent contract implicitly via "
            "`gen_statem` run-to-completion semantics rather than an "
            "explicit `E700` throw: a handler that synchronously calls "
            "`save_state` on its own Pid deadlocks (the actor is busy "
            "processing the current event), times out after 5s, and the "
            "calling process crashes. Functionally equivalent to E700 "
            "(the operation fails on a contract violation) but the "
            "mechanism differs, so the explicit-error assertion this "
            "fixture makes does not apply. See capability-matrix "
            "footnote [q].\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === primary/91 — multi-system cross-ref (Java + Erlang one-per-file) ===
    skip_only("primary/91_main_attr_cross_ref", ["fjava", "ferl"],
              "Intentional skip — multi-system per file (Java/Erlang)",
              _JAVA_ERLANG_MULTI_BODY),

    # === primary/82 — multi-system persist; Java + Erlang skip, rest are real ports ===
    skip_only("primary/82_persist_multi_system", ["fjava", "ferl"],
              "Intentional skip — multi-system per file (Java/Erlang)",
              _JAVA_ERLANG_MULTI_BODY),

    # === primary/54 — inline string interpolation; backends without the syntax ===
    skip_only(
        "primary/54_interp_state_var",
        ["fc", "fcpp", "ferl", "fgd", "fgo", "fjava", "flua", "frs"],
        "Intentional skip — no native inline string interpolation",
        (
            "This fixture exercises framec lowering a state-var (`$.x`) "
            "*inside* the target's native inline string-interpolation "
            "construct — Python f-strings, JS/Kotlin/Dart template "
            "literals, C# `$\"…\"`, Swift `\\(…)`, Ruby `#{…}`, PHP "
            "`\"{$…}\"`. The backends skipped here have no inline "
            "interpolation syntax for that lowering to inhabit:\n\n"
            "- **Rust** — `format!` is a macro, not inline string "
            "interpolation; framec rejects the f-string form (transpile "
            "error).\n"
            "- **C, C++, Go, Java, Lua** — use printf-style / `String."
            "format` / `%`-formatting, a different code path explicitly "
            "out of scope for this fixture.\n"
            "- **GDScript** — uses `%`/`.format()`; it has no inline "
            "`${}`/`{}` interpolation, so framec emits literal braces "
            "that GDScript does not expand (verified empirically; this "
            "corrects the earlier audit note that listed GDScript as a "
            "port candidate).\n\n"
            "The interpolation feature is covered on the eight backends "
            "with native inline syntax (C#, Dart, JS, Kotlin, Python, "
            "Ruby, Swift, TS) plus PHP.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === primary/103 — @@! no-init sigil smoke on the RFC-0017 D7 reference set ===
    # Real ports: erl, gd, java, py, rs (present) + kt, swift (this batch adds).
    SkipBatch(
        stem_path="primary/103_at_bang_no_init",
        real_exts=["ferl", "fgd", "fjava", "fkt", "fpy", "frs", "fswift"],
        title="Intentional skip — @@! sigil smoke on D7 reference backends",
        body=(
            "This fixture exists to exercise the `@@!Foo()` no-init "
            "*sigil* itself (RFC-0017 D7) — the syntactic form that "
            "allocates a naked shell without running the start state's "
            "`$Start(...)` body or `$>` enter handler. It is scoped to "
            "the D7 reference backends the sigil shipped on (Python, "
            "Rust, Java, Kotlin, Swift, Erlang) plus GDScript.\n\n"
            "On the remaining backends, the restore-without-init "
            "*behavior* that `@@!` enables is already covered "
            "end-to-end by the persist suite (tests 23-25, 51, 56-60, "
            "83-88, 93, 96, 98, 99): `@@[load]` allocates the shell and "
            "populates it from the serialized blob without re-firing the "
            "enter cascade. Re-testing the sigil on every backend would "
            "duplicate that coverage without exercising a new code "
            "path.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === systems/ — forward-then-transition exec-ordering regression net (C + Rust) ===
    # fc + frs are the REAL ports; skip.md goes on the other 15 backends.
    SkipBatch(
        stem_path="systems/child_forwards_then_transition_exec",
        real_exts=["fc", "frs"],
        title="Intentional skip — C/Rust exec-ordering regression net",
        body=(
            "Execution-ordering regression net with `@@run-expect` output "
            "assertions (`FORWARD:PARENT` ×2 then `TRANSITION:`). It pins "
            "the exact forward-then-transition dispatch sequence on the "
            "two exec backends whose lowering is most divergent: C "
            "(pointer-based dispatch) and Rust (typed `StateContext` "
            "enum). The forward (`=> $^`) and transition (`-> $S`) "
            "semantics themselves are exercised across all 17 backends by "
            "the broader `control_flow/` and `systems/` suites; this "
            "fixture's distinct value is the exact-output contract on the "
            "C/Rust exec paths, which is not target-uniform.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Coverage-gate closure (2026-07): the remaining common/positive gaps are all
# single-target or capability-scoped by design — verified per-stem. Grouped
# here and appended to BATCHES.
# ---------------------------------------------------------------------------

_MAX_COVERAGE_BODY = (
    "Per-language **maximal-surface** fixture: exercises the fullest Frame "
    "feature set a single backend supports (HSM, stack, all statement forms, "
    "transitions, references, const, actions, operations, multi-system, "
    "persist, async) written in that backend's own idioms. Single-target by "
    "design — there is no cross-language equivalent; broad behavioral parity "
    "is covered by the per-feature suites.\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_ASYNC_LANG_IDIOM_BODY = (
    "Language-specific async/concurrency idiom test. It exercises a construct "
    "particular to this backend's async model — e.g. C# exception filters / "
    "`Task` combinators, Kotlin dispatchers / `Mutex` / supervisor scope / "
    "cancellation, Swift `async let` / detached tasks / task groups, Dart "
    "futures / zones / completers, C++ coroutine throw-propagation / "
    "string-return lifetime, GDScript typed-await returns. These have no "
    "cross-language analogue, so the fixture is single-target by design.\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_ASYNC_SPLIT_BODY = (
    "Cross-backend async behavioral fixture whose coverage is **split across "
    "the common and language-specific trees**: the Python, TypeScript, "
    "JavaScript, Rust and Java variants live under `tests/<lang>/positive/` "
    "(all five present there), while the six typed backends here carry the "
    "`common/positive/primary/` copy. The remaining backends — C, Go, PHP, "
    "Ruby, Lua — are one-color (no async/await), so the fixture does not "
    "apply.\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_FLOAT_ERASURE_BODY = (
    "Statically-typed numeric-erasure round-trip: probes whether an integer "
    "survives a boundary that would erase it to a float, on the statically-"
    "typed backends where that ambiguity exists (C#, Go, Java, Kotlin, "
    "Swift). Dynamic backends preserve the runtime numeric type (nothing to "
    "erase), so the fixture is scoped to those five by design.\n\n"
    "See `docs/partial-coverage-audit.md`."
)

_TABLE_LITERAL_BODY = (
    "Lua-specific: exercises a Lua table literal (`{...}`) inside a loop body "
    "— native Lua syntax with no cross-language analogue. Single-target by "
    "design.\n\n"
    "See `docs/partial-coverage-audit.md`."
)

# max_coverage: one stem per language, present only on its own backend.
_MAX = {
    "max_c": "fc", "max_cpp": "fcpp", "max_csharp": "fcs", "max_dart": "fdart",
    "max_gdscript": "fgd", "max_go": "fgo", "max_java": "fjava",
    "max_javascript": "fjs", "max_kotlin": "fkt", "max_lua": "flua",
    "max_php": "fphp", "max_python_3": "fpy", "max_ruby": "frb",
    "max_rust": "frs", "max_swift": "fswift", "max_typescript": "fts",
}
for _stem, _ext in _MAX.items():
    BATCHES.append(SkipBatch(
        stem_path=f"max_coverage/{_stem}", real_exts=[_ext],
        title="Intentional skip — per-language maximal-surface fixture",
        body=_MAX_COVERAGE_BODY))

# primary/async_<lang>_*: language-specific async idiom, single-target.
_ASYNC_IDIOM = {
    "async_cpp_nested_throw_propagation": "fcpp",
    "async_cpp_string_return_lifetime": "fcpp",
    "async_cpp_throw_after_partial_await": "fcpp",
    "async_cs_exception_filter": "fcs",
    "async_cs_task_whenall_aggregation": "fcs",
    "async_cs_task_whenany_winner": "fcs",
    "async_dt_completer_bridge": "fdart",
    "async_dt_future_then_chain": "fdart",
    "async_dt_future_wait_aggregation": "fdart",
    "async_dt_zone_value_propagation": "fdart",
    "async_gd_no_node_subclass": "fgd",
    "async_gd_optional_typing": "fgd",
    "async_gd_typed_zero_return": "fgd",
    "async_kt_cancellation_clears_gate": "fkt",
    "async_kt_companion_factory_resolves": "fkt",
    "async_kt_dispatcher_switch_in_handler": "fkt",
    "async_kt_e703_message_format": "fkt",
    "async_kt_mutex_serializes_drivers": "fkt",
    "async_kt_noncancellable_finally": "fkt",
    "async_kt_supervisor_scope_isolates": "fkt",
    "async_sw_async_let_parallel": "fswift",
    "async_sw_detached_task": "fswift",
    "async_sw_task_cancel_clears_gate": "fswift",
    "async_sw_task_group_concurrent_entry": "fswift",
}
for _stem, _ext in _ASYNC_IDIOM.items():
    BATCHES.append(SkipBatch(
        stem_path=f"primary/{_stem}", real_exts=[_ext],
        title="Intentional skip — language-specific async idiom",
        body=_ASYNC_LANG_IDIOM_BODY))

# primary/async_* split across common + language-specific trees.
for _stem in ("async_composition_parent_child", "async_concurrent_entry_e703",
              "async_distinct_instances_parallel", "async_exception_clears_gate",
              "async_persist_roundtrip_gate_clears", "async_sync_op_bypass_gate"):
    BATCHES.append(SkipBatch(
        stem_path=f"primary/{_stem}",
        real_exts=["fcpp", "fcs", "fdart", "fgd", "fkt", "fswift"],
        title="Intentional skip — async fixture split across test trees",
        body=_ASYNC_SPLIT_BODY))

BATCHES.append(SkipBatch(
    stem_path="primary/float_erasure_roundtrip",
    real_exts=["fcs", "fgo", "fjava", "fkt", "fswift"],
    title="Intentional skip — statically-typed numeric erasure only",
    body=_FLOAT_ERASURE_BODY))

BATCHES.append(SkipBatch(
    stem_path="control_flow/table_literal_in_loop", real_exts=["flua"],
    title="Intentional skip — Lua-specific table literal",
    body=_TABLE_LITERAL_BODY))


if __name__ == "__main__":
    sys.exit(run(BATCHES))
