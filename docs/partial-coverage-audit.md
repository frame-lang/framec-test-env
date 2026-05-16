# Partial-coverage fixture audit

A snapshot audit of the 33 fixtures in `tests/common/positive/` that
have fewer than 17 backend implementations, classified by why the
gap exists. Most gaps are *intentional* (the feature is documented
🚫 in the capability matrix) and a few are *stale* (the gap predates
a feature shipping; the fixture should be ported).

Conducted 2026-05-16. See
[runtime-capability-matrix.md](runtime-capability-matrix.md) for the
canonical capability table the verdicts refer to.

## Summary

| Category | Count |
|---|---|
| Intentional (matrix-aligned skip) | 12 |
| Single-target by design (smoke / regression net) | 10 |
| Stale — should be expanded | 8 |
| Investigate further | 3 |
| **Total** | **33** |

## `primary/` (18)

| Fixture | Present | Verdict | Notes |
|---|---|---|---|
| `52_hsm_state_arg_propagation` | rs | **Single-target** | Rust-only regression net for D5 cascade visibility fix |
| `54_interp_state_var` | cs, dart, js, kt, py, rb, swift, ts | **Investigate** | 8 langs (no c/cpp/erl/gd/go/java/lua/php). String-interpolation stress test; the missing 9 include both dynamic (lua, php) and typed (c, cpp, go, java) — partition unclear. |
| `55_nested_frame_args` | py | **Single-target** | Python-only smoke for nested `@@SystemName($(arg))` calls |
| `75_nested_list_state_arg` | 16 (no erl) | **Intentional** | Wave 8 nested-system test; Erlang multi-system 🚫[k] |
| `78_nested_dict_state_arg` | 16 (no erl) | **Intentional** | Same — Erlang multi-system 🚫[k] |
| `81_persist_async_basic` | cpp, cs, gd, go, java, js, kt, py, rs, swift, ts | **Stale** | Async-✅ langs per matrix: 11 (py, ts, js, rs, cpp, cs, java, kt, swift, dart, gd). Fixture has go (which is 🚫[g] async) but missing dart (which is ✅ async). Two anomalies — see below. |
| `82_persist_multi_system` | js, py, ts | **Stale** | Multi-system × persist test from Wave 7. Matrix says multi-system works on 15 langs (Java/Erlang 🚫). Fixture only on dynamic 3 — should be ported to ~12 more. |
| `84_persist_nested_hsm` | 16 (no erl) | **Intentional** | Erlang multi-system 🚫[k] |
| `85_persist_three_level_nested` | 16 (no erl) | **Intentional** | Erlang multi-system 🚫[k] |
| `86_persist_numeric_typing` | 16 (no erl) | **Intentional** | Erlang multi-system 🚫[k] |
| `87_persist_multi_instance` | 16 (no erl) | **Intentional** | Erlang multi-system 🚫[k] |
| `88_persist_quiescent_error` | 15 (no erl, no go) | **Intentional** | Erlang quiescent ⚠️[q] (implicit); Go was deliberately deferred for E700 (verify with `wave8` notes). |
| `91_main_attr_cross_ref` | 15 (no erl, no java) | **Intentional** | Multi-system fixture; Java 🚫[j] + Erlang 🚫[k] |
| `99_persist_param_child` | gd | **Single-target** | GDScript-only regression for parameterized-child × domain-init fix (#328) |
| `101_persist_int_fidelity` | gd, lua | **Single-target** | Dynamic-typing int/float ambiguity; specific to these two. |
| `102_persist_domain_list_dict` | c, py | **Investigate** | List + dict as persisted domain fields. C and Python only — but persist-list-dict should work on all 16 non-Erlang backends. Possibly stale. |
| `103_at_bang_no_init` | erl, gd, java, py, rs | **Stale** | RFC-0015 D7 shipped on 6 backends (Python, Rust, Java, Kotlin, Swift, Erlang per memory `#312`+`#313`). Missing kotlin + swift coverage here. |
| `106_hsm_3deep_cascade` | py | **Single-target** | RFC-0019 smoke fixture (#408 in roadmap), Python-only by design |

## `data_types/` (5)

All five fixtures share the same coverage shape: 13 langs, missing
`fjs`, `frs`, `fswift`, `fts`.

| Fixture | Present | Verdict |
|---|---|---|
| `dict_ops` | 13 (no js/rs/swift/ts) | **Stale** |
| `inside_string_tokens_ignored` | 13 (no js/rs/swift/ts) | **Stale** |
| `ints_strings` | 13 (no js/rs/swift/ts) | **Stale** |
| `module_visitor_map_basic` | 13 (no js/rs/swift/ts) | **Stale** |
| `test_mixed_body_strings_comments` | 13 (no js/rs/swift/ts) | **Stale** |

**Pattern:** these are pre-RFC-0013 data-type tests that haven't
been ported to JS/Rust/Swift/TS. Likely a deliberate deferral when
those backends were added — should now be filled.

## `segmenter/` (3)

All three share: 12 langs, missing `fcs`, `fgo`, `fjava`, `fkt`,
`fphp`.

| Fixture | Present | Verdict |
|---|---|---|
| `frame_tokens_in_comments` | 12 (no cs/go/java/kt/php) | **Investigate** |
| `heavy_native_prolog` | 12 (no cs/go/java/kt/php) | **Investigate** |
| `nested_braces` | 12 (no cs/go/java/kt/php) | **Investigate** |

**Pattern:** segmenter tests cover token-level parsing
robustness — the segmenter is target-language-agnostic (it sees
Frame source before any codegen), so the missing backends might
genuinely add no coverage value, OR they might have been left out
because of a fixture-authoring deferral. Need confirmation.

## `scoping/` (2)

Both share: 13 langs, missing the same 4 (js, rs, swift, ts).

| Fixture | Present | Verdict |
|---|---|---|
| `function_scope` | 13 (no js/rs/swift/ts) | **Stale** |
| `nested_functions` | 13 (no js/rs/swift/ts) | **Stale** |

Same pattern as `data_types/` — pre-port deferral.

## `capabilities/` (3)

| Fixture | Present | Verdict | Notes |
|---|---|---|---|
| `actions_call_wrappers` | 13 (no js/rs/swift/ts) | **Stale** | Same pattern |
| `nested_functions` | c | **Single-target** | C-only test for native nested-function handling |
| `system_return_header_defaults` | 13 (no js/rs/swift/ts) | **Stale** | Same pattern |

## `interfaces/` (2)

| Fixture | Present | Verdict | Notes |
|---|---|---|---|
| `return_no_type_annotation` | gd, js, lua, php, py, rb | **Intentional** | Dynamic-langs-only test (untyped return) — typed backends require explicit return type so this fixture is conceptually N/A there. |
| `return_typed` | ts | **Single-target** | TypeScript-only edge case; probably exists for a specific TS-parser quirk. |

## Action items derived from audit

The stale category is the actionable list — gaps that should be
filled. Aggregated:

1. **`81_persist_async_basic`**: investigate the Go anomaly (matrix
   says 🚫 async but fixture exists; either a stub or the matrix is
   wrong); add Dart coverage (matrix says ✅).
2. **`82_persist_multi_system`**: port to 12 more backends (c, cpp,
   cs, dart, gd, go, kt, lua, php, rb, rs, swift). Matrix expects
   ✅ on all 15 multi-system backends; only 3 covered.
3. **`102_persist_domain_list_dict`**: port to 14 more backends
   (cpp, cs, dart, gd, go, java, js, kt, lua, php, rb, rs, swift,
   ts). Persist with list+dict domain fields should be universal.
4. **`103_at_bang_no_init`**: add `fkt` and `fswift` coverage (D7
   shipped on those per memory entries `#312` + `#313`).
5. **`data_types/` × 5**: port each to `fjs`, `frs`, `fswift`,
   `fts` — 20 file ports.
6. **`scoping/` × 2**: same — 8 file ports.
7. **`capabilities/actions_call_wrappers`** and
   **`capabilities/system_return_header_defaults`**: same — 8 file
   ports.

Total stale-fix work: ~50 fixture ports. Each is mechanical (the
feature works; just add the `.f<ext>` variant). Could be batched
into a single sweep, or piggyback on the cookbook-port agent's
parallel work.

## Action items requiring investigation

1. **`54_interp_state_var`**: why does this 8-lang fixture skip
   both dynamic (lua, php) and typed (c, cpp, go, java) backends?
   Read the fixture body to identify what specific behavior is
   being tested.
2. **`102_persist_domain_list_dict`**: confirm whether the gap is
   stale or intentional. The Python+C limitation looks accidental
   but C's `list`/`dict` story has `[l]` footnote — verify.
3. **`segmenter/` × 3**: confirm whether C#, Go, Java, Kotlin, PHP
   are intentionally skipped for segmenter tests or just
   undeferred. Segmenter is target-agnostic, but the matrix runner
   may genuinely need backend coverage to detect regressions
   surfaced by the codegen pipeline downstream of the segmenter.

## Methodology

Generated by `find` + `ls` scripts over
`tests/common/positive/<dir>/` walking each fixture stem and
counting backend-specific extension files (`.fpy`, `.fjava`, etc.),
filtering out `.driver`, `.escript`, README, and helper files.
Cross-referenced against `runtime-capability-matrix.md` to
classify gaps. Verdicts are conservative — when in doubt,
classified as "Investigate" rather than "Stale".
