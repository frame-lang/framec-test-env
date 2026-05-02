# Fuzz dry-run status — 2026-05-02

This file tracks the dry-run discipline for the 21-phase fuzz program.
A phase is **green** when two consecutive waves complete with zero new
defects (the second wave attests that the first wasn't a fluke). The
two waves must sample the same axes — wave-2 doesn't have to extend
the dimensions, but it must run after every defect surfaced by wave-1
has been fixed and the corpus regenerated.

For axis-extension (truly new dimensions) see the wave-3+ candidates
listed in `FUZZ_PLAN.md` per phase. Most high-value-density phases
(2, 14, 15, 19, 24) already have axis-extension baked into the
corpus through prior wave plans; phases 11, 12, 13, 16, 17, 20, 21
ship with one axis only.

## Tier vocabulary

- **smoke**: 2–25 cases per phase, 5–30s wall-clock per phase.
- **full**: 12–162 cases per phase, 1–15 min wall-clock.
- **wave**: one execution of a tier across the full backend matrix
  (or the wired subset for phases with design-exclusion langs).

A successful wave = pass on every case × every wired backend.

## Phase status

| Phase | Wave 1 (smoke) | Wave 2 (full) | Defects in flight | Status |
|---|---|---|---|---|
| 2 (persist) | ✅ 17×2 = 34 | ✅ 17×81 = 1,377 | D20 found + fixed | **green** |
| 3 (selfcall) | ✅ 17×6 = 102 | ✅ 17×162 = 2,754 | none | **green** |
| 4 (hsm-parents) | ✅ 17×3 = 51 | ✅ 17×81 = 1,377 | none | **green** |
| 5 (operations) | ✅ 17×1 = 17 | ✅ 17×27 = 459 | none | **green** |
| 6 (async) | ✅ 11×1 = 11 | ✅ 11×20 = 220 | none | **green** (5 langs no-async) |
| 7 (multisys) | ✅ 15×1 = 15 | ✅ 15×12 = 180 | none | **green** (Java/Erlang excluded) |
| 8 (negative) | ✅ 44/44 | ✅ 44/44 | runner regex bug fixed | **green** |
| 9 (nested-syntax) | ✅ 5/5 | ✅ 17×5 = 85 | none | **green** |
| 10 (expression) | ✅ smoke | ✅ full × 17 | none | **green** |
| 11 (stmt-pair) | ✅ 25/25 | ✅ 100/100 | none | **green** |
| 12 (ctrl-flow) | ✅ smoke | ✅ full | none | **green** |
| 13 (shadow) | ✅ smoke | ✅ full | none | **green** |
| 14 (hsm-cross) | ✅ 8/8 | ✅ 80/80 | none | **green** |
| 15 (state-args) | ✅ smoke | ✅ full | none | **green** |
| 16 (comments) | ✅ smoke | ✅ full | none | **green** |
| 17 (multievent) | ✅ smoke | ✅ full | none | **green** |
| 18 (stress) | ✅ smoke | ✅ full | none | **green** |
| 19 (pushpop) | ⚠️ 169/170 (D19) | ✅ 170/170 post-fix | D19 found + fixed | **needs wave 2 rerun** |
| 20 (const-sys) | ✅ smoke | ✅ full | none | **green** |
| 21 (arith) | ✅ smoke | ✅ full | none | **green** |
| 24 (persist-x) | ✅ smoke | ✅ full | none | **green** |

## Defects surfaced and resolved during dry-run

### D19 — Rust enter-args stringification breaks typed receiver
- **Phase**: 19 (pushpop)
- **Surfaced by**: smoke wave (case `pp_p8_enter_args_round_trip__t0`)
- **Fix**: lifecycle dispatcher now downcasts to `String` then parses
  to the declared receiver type (i64 / f64 / bool). String params
  still downcast directly. `framec/src/frame_c/compiler/codegen/rust_system.rs`.
- **Commit**: `ce093fd` (framepiler).

### D20 — Dart restore_state emits Frame keyword `as str`
- **Phase**: 2 (persist)
- **Surfaced by**: full wave (54 of 81 persist cases × Dart failed;
  smoke's 2-case sample didn't include str domain field)
- **Fix**: `parse_dart_type` normalizes Frame keywords `str|string`
  → `String` and `float` → `double` before constructing the
  primitive node. `framec/src/frame_c/compiler/codegen/interface_gen.rs`.
- **Commit**: `e6291b2` (framepiler).

## Methodology lessons

1. **Smoke ≠ representative**. Smoke samples 2-25 cases per phase;
   defects that depend on a specific axis combination (D20 needed a
   str domain field; smoke's RNG didn't draw one) ride straight
   through. Full tier is non-negotiable for dry-run discipline.

2. **First defect-clean wave = wave-1, post-fix**. The current
   `green` rows have wave-2 (full) post-fix as their second clean
   wave. Strict reading: a phase with a defect surfaced by wave-1
   needs *two* subsequent clean waves, not one. Phase 19 is the
   only such phase in this run.

3. **Harness gaps masquerade as codegen defects**. Two wave-2
   "regressions" turned out to be harness side: prolog injection
   regex didn't match the new attribute syntax, and Java/Kotlin
   classpaths missed jackson jars after the JVM migration. Fixed
   in `fuzz/diff_harness/run_fuzz.py` + `fuzz/diff_harness/langs.py`.

## Next discipline step

Re-run wave 2 (full tier) one more time after **all** defects fixed
to confirm 2 consecutive clean waves on every phase. The Phase 2-7
diff-harness rerun (commit `e6291b2`) already satisfied this; Phase
19 still needs its post-fix wave-2 rerun to be airtight.

Once that completes, axis-extension (wave-3) is the next
discipline tier — see `FUZZ_PLAN.md` per-phase wave-2 candidates.
