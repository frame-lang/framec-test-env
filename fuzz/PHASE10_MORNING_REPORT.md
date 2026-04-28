# Phase 10 — Morning Report (2026-04-28)

## Update: D1 closed, D2 resolved (2026-04-28 morning)

Mark resolved D2 in favor of option 2 (terminate execution at the
**statement execution context boundary**, not within an expression).
D1 fix shipped in `frame_expansion.rs`: ~5-line edit deferring the
`pending_guard` emission until a newline-bearing NativeCode segment
arrives. Result: transition guard fires once at end-of-statement
regardless of embedded self-call count.

**v2 full tier now: 7,820 / 7,820 passing across all 17 langs.**

D3 (Swift self-assign corpus issue) also fixed via a
generator filter in `gen_perm.py:_is_self_assign_d1`.

Below is the original morning report — historical context up to the
overnight session ending.

---

## TL;DR

Phase 10 generator + tiered runner shipped. v1 fully clean across all
17 languages. v2 surfaced one new bug class (D1 — `self.field =`
multi-call expressions break codegen on most backends), logged for
your review along with a related design question (D2). One Erlang
codegen fix shipped. No commits made.

## What ran tonight

| Tier | Cases / lang | Total runs | Pass | Fail | Notes |
|---|---|---|---|---|---|
| **v1 full** (single LHS = `@@:return`) | 154 | 17 × 154 = 2,618 | 2,618 | 0 | Clean across the matrix |
| **v1 smoke** (one per equiv class) | 30 | 17 × 30 = 510 | 510 | 0 | ~30s end-to-end |
| **v2 full** (LHS = ret / dom / sv) | 462 | 17 × 462 = 7,854 | mostly clean | ~18 per backend (D1) | Erlang now 462/462 after fix |

## Files added

- `framepiler_test_env/fuzz/gen_perm.py` — generator. Single-statement,
  depth ≤ 2 cross-product. 7 receivers × 3 operators × 3 LHS targets.
  Reuses `gen_nested.py`'s `LangSpec` for per-language emission.
- `framepiler_test_env/fuzz/run_perm.sh` — runner with
  `--tier=smoke|core|full` and `--lang=<name>`.
- `framepiler_test_env/fuzz/cases_perm/_index.tsv` — sidecar with
  `(lang, case_id, equiv_class, smoke, expected)`. Runner reads this
  for smoke filtering instead of in-source comments (those would land
  in JS/Java output where `#` isn't a comment).
- `framepiler_test_env/fuzz/DEFECTS.md` — defect log (D1 + D2).
- `framepiler_test_env/fuzz/PHASE10_MORNING_REPORT.md` — this file.

## Files modified

- `framepiler_test_env/fuzz/gen_nested.py` — Phase 9 trimmed from 11
  patterns to 4 (`p7`, `p8`, `p9`, `p11`). The retired patterns are
  subsumed by Phase 10's expression cross-product. The 4 retained
  patterns encode axes the generator doesn't reach:
  depth-3 nesting, multi-statement transition, multi-handler
  state-var round-trip.
- `framec/src/frame_c/compiler/codegen/erlang_system.rs` — body-line
  pre-pass updated to handle `self.<field> = self.<iface>() <op> X`
  (was previously skipped, falling through to `InterfaceCallWithBind`
  which used `rfind(')')` and grabbed the wrong close paren). Pre-pass
  now uses paren-balance for bare-call detection so mixed-expression
  RHS gets hoisted into a temp-bind.

## Tier model in use

| Tier | Source | Cases / lang | Wall clock | When to run |
|---|---|---|---|---|
| Smoke | gen_perm.py, one per coarse equiv class | 30 | ~30s | Every iteration |
| Core | gen_nested.py, p7+p8+p9+p11 | 4 | ~20s matrix | Before commit |
| Full | gen_perm.py, all combos | 462 | ~25 min matrix | Nightly / pre-release |
| Stress | All of the above + Phase 6/7/8 | All | 1hr+ | Pre-release |

Run examples:
```
./run_perm.sh --tier=smoke                  # 30 × 17 = 510 cases, ~30s
./run_perm.sh --tier=core                   # delegates to run_nested.sh (4 × 17)
./run_perm.sh --tier=full --lang=python_3   # 462 cases, ~30s
./run_perm.sh --tier=full                   # 462 × 17, ~25 min wall
```

## Defects surfaced

### D1 (cross-backend, needs-review)

`self.field = @@:self.method() <op> recv2` — codegen injects a
transition guard mid-expression, breaking syntax. Manifests on every
backend that uses `pending_guard` in `frame_expansion.rs` (essentially
all 15 typed backends; Erlang now safe via the body-line pre-pass).

- 18 cases per backend out of 462 (~3.9%).
- Same trigger across backends: domain LHS + first receiver = self-call
  + suffix expression continues on same line.
- v1 didn't surface this because v1 only used `@@:return =` LHS, which
  takes a different codegen path (`expand_expression` lowers the whole
  thing atomically).

### D2 (design question, needs-discussion)

The deeper question your earlier note flagged: **what should Frame's
contract be for multiple `@@:self.method()` calls inside one expression?**

Today's de facto behavior:
- `@@:return = self.a() + self.b()` — both calls run, no per-call
  abort. This works correctly across all 17 backends today.
- `self.field = self.a() + self.b()` — broken codegen (D1). Intent
  was per-call abort via injected guards; implementation falls apart
  because the guard is a statement, not an expression.

D2 in DEFECTS.md frames three options for resolving the contract:
"all calls run, guard at statement boundary" (matches existing
`@@:return =` behavior, simplest fix), "per-call abort via temp-bind
hoist" (most semantically correct, expensive across 15 backends), or
"forbid embedded self-calls; require explicit intermediates" (most
explicit, breakage risk).

**Status**: parked for your call.

## Codegen fixes shipped this session (uncommitted)

Earlier in the evening (before Phase 10):
1. Erlang `analyze_case_arms` recognizes bare-pattern arm headers
   (`s0 ->`, `_ ->`) emitted by `erlang_wrap_self_call_guards`. Closes
   Phase 9 p9 transition+return Erlang bug.
2. Erlang body-line pre-pass that splits `LHS = ... self.method()
   <suffix>` into a temp-bind + assignment. Closes Phase 9 p13
   selfcall-arithmetic Erlang bug.
3. Dart `compartment.state_vars["x"]` reads now emit `(... as <type>)`
   cast based on declared type. Closes Phase 9 p11 Dart cast bug.

Tonight (Phase 10):
4. Erlang body-line pre-pass extended to handle `self.<field> = ...`
   LHS forms with mixed RHS expressions (the same temp-bind hoist).
   Closes the Erlang manifestation of D1.

Verification:
- `cargo test --lib --release` — 363 passing.
- `cargo clippy --release -- -D warnings` — clean.
- `cargo fmt --check` — clean.
- 17-lang docker matrix — running at writing time of this report;
  status will be appended below.
- Phase 9 Erlang post-fix — 4/4 passing.
- Phase 10 v2 Erlang — 462/462 passing.

## Working tree state

- `framec/src/frame_c/compiler/codegen/erlang_system.rs` — modified
- `framec/src/frame_c/compiler/codegen/frame_expansion.rs` — modified
  (this evening's Dart cast fix)
- `framepiler_test_env/fuzz/gen_perm.py` — new
- `framepiler_test_env/fuzz/run_perm.sh` — new
- `framepiler_test_env/fuzz/DEFECTS.md` — new
- `framepiler_test_env/fuzz/PHASE10_MORNING_REPORT.md` — new (this file)
- `framepiler_test_env/fuzz/gen_nested.py` — modified (trim to 4 patterns)
- `framepiler_test_env/fuzz/cases_nested/` — regenerated (4 patterns × 17 = 68 files)
- `framepiler_test_env/fuzz/cases_perm/` — regenerated (462 cases × 17 = 7854 files)

No commits made. Per your global rule, awaiting explicit
permission before committing anything.

## What I'd suggest as morning order

1. Review **D2** (the design question) and pick the contract.
2. Decide on D1 fix shape based on D2 resolution.
3. Decide commit policy for the 4 codegen fixes (the 3 from earlier
   this evening + the 1 from tonight).
4. Phase 10 capability matrix entry — add a row for the new tier
   model in `framepiler_test_env/docs/runtime-capability-matrix.md`?
   (No edit made; flagging so it's discoverable when you want to.)
5. Once D2/D1 is decided, the same fix shape probably needs to
   propagate to other `pending_guard`-using backends (15 of them).

## Numbers in one place

- v1: 17 × 154 = **2,618 / 2,618 passing**

- v2: 17 × 462 = 7,854 cases, **7,533 passing** (95.9%). Per-lang
  results from `logs_perm/per_lang/summary_<lang>.tsv`:

  | Lang | Pass | Notes |
  |---|---|---|
  | Erlang | **462 / 462** | D1 fixed via the body-line pre-pass extension shipped this session |
  | Python, JS, TS, Ruby, Lua, PHP, GDScript, Dart, Go, C, C++, Java, Kotlin, C#, Rust | 444 / 462 | D1 — 18 dom-LHS + self-call + suffix cases |
  | Swift | 443 / 462 | D1 (18) + D3 (1: Swift compiler rejects literal `self.n = self.n` self-assign) |

- Phase 9: 17 × 4 = **68 / 68 passing** (Core tier)
- Cargo: 363 unit tests passing, clippy + fmt clean
- Docker matrix: **3,800 passed, 0 failed, 19 framec-gap skips, 17/17 clean**

## Defects logged

- **D1** (cross-backend, needs-review): Self-call mid-expression in
  `self.field = ...` LHS breaks codegen. 18 cases × 14 backends.
  Erlang fixed via body-line pre-pass.
- **D2** (design question, needs-discussion): Semantics of multiple
  `@@:self.method()` calls inside one expression. Currently `@@:return =`
  runs all calls, no per-call abort; `self.field =` was *intended*
  to inject per-call guards but is broken (D1). Three options
  in DEFECTS.md.
- **D3** (corpus issue, low priority): Swift rejects literal
  `self.n = self.n` (`dom_d1_dom_n`). Cosmetic — drop the
  receiver=LHS-target combinations from `enumerate_cases`.

## Infrastructure improvements this session

- `run_perm.sh` now writes per-lang summary files
  (`logs_perm/per_lang/summary_<lang>.tsv`) so concurrent
  `--lang=X` / `--lang=Y` invocations don't clobber each other.
  Aggregate `summary.tsv` is rebuilt at end-of-run.
- `batch_kotlin` is now resilient to compile failures: iteratively
  drops failing files (parsed from kotlinc stderr) and retries the
  batch until success. Caps at 5 iterations.
- `gen_perm.py` v2: adds LHS dimension (`@@:return =`,
  `self.<dom> =`, `$.<sv> =`) to the cross-product. 154 → 462 cases
  per lang.
- `fuzz/README.md` updated with Phase 9 + Phase 10 sections,
  documenting tier model and run examples.
