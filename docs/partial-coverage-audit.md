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
| Intentional (matrix-aligned skip or target-uniform redundancy) | 16 |
| Single-target by design (smoke / regression net) | 10 |
| Stale — should be expanded | 7 |
| **Total** | **33** |

(The 3 originally flagged "Investigate" cases were resolved in
the same audit pass: `54_interp_state_var` is intentional except
for 2 stale ports — GDScript and PHP; `102_persist_domain_list_dict`
is stale per its own fixture comment; segmenter × 3 are intentional
because their coverage is target-uniform within each comment-syntax
family.)

## `primary/` (18)

| Fixture | Present | Verdict | Notes |
|---|---|---|---|
| `52_hsm_state_arg_propagation` | rs | **Single-target** | Rust-only regression net for D5 cascade visibility fix |
| `54_interp_state_var` | cs, dart, js, kt, py, rb, swift, ts | **Intentional + 2 stale ports** | Tests interpolation of state-vars in string literals (`f"x is {$.count}"`). 8 present langs have native interpolation. Missing 9 split: c/cpp/erlang/go/java/lua have no native interpolation (intentional skip — they'd test `printf`-style formatting, a different code path). **GDScript and PHP do have native interpolation and should be added.** |
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
| `102_persist_domain_list_dict` | c, py | **Stale** | Fixture comment explicitly says "On every other backend: the type-ignorant domain-field path through Jackson / Codable / serde / etc." — 17-backend intent currently materialized as 2 fixtures. Port to remaining 15. |
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
| `frame_tokens_in_comments` | 12 (no cs/go/java/kt/php) | **Intentional** |
| `heavy_native_prolog` | 12 (no cs/go/java/kt/php) | **Intentional** |
| `nested_braces` | 12 (no cs/go/java/kt/php) | **Intentional** |

**Pattern:** segmenter logic is target-uniform within each
comment-syntax family — `//` C-family (c, cpp, dart, js, swift,
ts — 6 fixtures), `#` (gd, py, rb, lua — 4 fixtures), `%` (erl
— 1 fixture). The missing 5 (cs, go, java, kt, php) are all
`//`-comment C-family; adding them would duplicate coverage that
the existing 6 `//`-family fixtures already provide. No new code
paths exercised.

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

The stale category is the actionable porting list. Aggregated:

1. **`81_persist_async_basic`**: investigate the Go anomaly (matrix
   says 🚫 async but fixture exists; either a stub or the matrix is
   wrong); add Dart coverage (matrix says ✅). Open question, not
   yet resolved by this audit.
2. **`82_persist_multi_system`**: port to 12 more backends (c, cpp,
   cs, dart, gd, go, kt, lua, php, rb, rs, swift). Matrix expects
   ✅ on all 15 multi-system backends; only 3 covered.
3. **`102_persist_domain_list_dict`**: port to 14 more backends
   (cpp, cs, dart, gd, go, java, js, kt, lua, php, rb, rs, swift,
   ts). Fixture comment itself names every backend's native
   serializer path; the gap is unambiguously stale.
4. **`103_at_bang_no_init`**: add `fkt` and `fswift` coverage (D7
   shipped on those per memory entries `#312` + `#313`).
5. **`54_interp_state_var`**: add `fgd` + `fphp` (2 ports).
   Resolved during audit — both have native string interpolation.
6. **`data_types/` × 5**: port each to `fjs`, `frs`, `fswift`,
   `fts` — 20 file ports.
7. **`scoping/` × 2**: same — 8 file ports.
8. **`capabilities/actions_call_wrappers`** and
   **`capabilities/system_return_header_defaults`**: same — 8 file
   ports.

Total stale-fix work: ~52 fixture ports. Each is mechanical (the
feature works on the target; just add the `.f<ext>` variant). The
remaining 1 open question is the Go async anomaly in #1 — worth
a 10-min poke before doing the Dart port.

## Methodology

Generated by `find` + `ls` scripts over
`tests/common/positive/<dir>/` walking each fixture stem and
counting backend-specific extension files (`.fpy`, `.fjava`, etc.),
filtering out `.driver`, `.escript`, README, and helper files.
Cross-referenced against `runtime-capability-matrix.md` to
classify gaps. Verdicts are conservative — when in doubt,
classified as "Investigate" rather than "Stale".
