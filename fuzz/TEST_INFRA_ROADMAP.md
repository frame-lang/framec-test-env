# Test infra roadmap

## Goals

Across ~20 fuzz phases × 17 languages × thousands of cases each, the
fuzz suite needs three operating modes:

1. **Smoke** — fast iteration, runnable on every framec change.
   Target: under 2 min total wall clock across all phases.
2. **Full** — exhaustive, runnable nightly or before commit.
   Target: under 30-45 min total wall clock.
3. **Cross-sectional** — arbitrary slices ("all Erlang tests", "all
   HSM tests across all phases", "smoke + tag=async"). Runnable on
   demand for triage or targeted debugging.

Today only Phase 10 has these affordances. The other phases each
have their own ad-hoc runner with no shared filter contract. This
doc describes the architecture to unify them.

## Current state (2026-04-28)

| Phase | Has tier filter? | Tag support | Per-lang summary? |
|---|---|---|---|
| 2 (`@@persist`) | random sample | None | run_persist.sh aggregate only |
| 3 (`@@:self`) | full only | None | run_selfcall.sh aggregate only |
| 4 (HSM parents) | full only | None | aggregate only |
| 5 (Operations) | full only | None | aggregate only |
| 6 (Async) | full only | None | aggregate only |
| 7 (Multi-system) | full only | None | aggregate only |
| 8 (Negative) | full only | None | aggregate only |
| 9 (Nested) | smoke=core (4 patterns curated) | None | per-lang via `run_nested.sh` |
| 10 (Expression) | smoke / core / full | `equiv_class` per case | per-lang `_index.tsv` + per-lang summary files |

Phase 10 is the model. The other 8 phases need to migrate to its
structure.

## Target architecture

Three deliverables that, together, make every phase's runner uniform
and queryable:

### 1. Standard runner contract

Every phase runner accepts the same flags:

```
run_<phase>.sh [--tier=smoke|core|full] [--tag=<comma-list>] [--lang=<name>]
```

Defaults: `--tier=full`, no tag filter, all langs.

Behavior:
- Smoke = curated subset that catches 80%+ of historical bugs in the
  phase. Phase-specific selection (see "Per-phase migration" below).
- Core = phase-specific essentials, runtime-asserted where possible.
- Full = current full corpus, transpile + run + assert.
- Tag filter applies on top: only run cases whose tag set
  intersects with the requested tags.

### 2. Per-phase sidecar index

Extending Phase 10's `cases_perm/_index.tsv` model:

```
phase    lang       case_id              tags                                    tier   expected
phase2   python_3   persist_hsm0_int     hsm,depth-0,persist,smoke,save-restore  smoke  ok
phase2   rust       persist_hsm2_strint  hsm,depth-2,persist,full,save-restore   full   ok
phase4   erlang     hsm_uncle_2lvl       hsm,depth-2,parent,uncle,core           core   ok
phase10  swift      ret_d2_lit5_plus_..  expr,return-lhs,arith,smoke             smoke  10
```

Tag categories (curated, finite vocabulary):
- **Lang**: `python_3`, `javascript`, ..., `erlang` — 17 values
- **Feature**: `persist`, `selfcall`, `hsm`, `async`, `multisys`,
  `expr`, `control-flow`, `negative`, `nested-syntax`, `pushpop`,
  `operations`, `lifecycle`, `state-args`, `enter-args`, `exit-args`
- **Depth**: `depth-0`, `depth-1`, `depth-2`, `depth-3`,
  `hsm-1`, `hsm-2`, `hsm-3`
- **LHS / context**: `return-lhs`, `dom-lhs`, `sv-lhs`, `void-lhs`,
  `in-if`, `in-while`, `after-call`, `before-transition`
- **Tier**: `smoke`, `core`, `full`
- **Behavior**: `save-restore`, `transition`, `parent`, `uncle`,
  `panic`, `coercion`, etc. (per-phase specifics)

Tags are **additive**: a case might be `hsm,depth-2,persist,smoke`.
Filters use comma-separated AND-of-tags by default; `|` for OR is
out of scope for v1.

### 3. Top-level meta-runner

`framepiler_test_env/fuzz/run_all.sh` — iterates configured phases
with shared flags:

```bash
run_all.sh --tier=smoke                      # ~1-2 min total
run_all.sh --tier=full                       # ~30-60 min total
run_all.sh --tag=erlang                      # all Erlang, all phases
run_all.sh --tag=hsm,depth-2 --lang=rust     # cross-section
run_all.sh --tier=core --tag=async           # all async core
run_all.sh --phases=2,3,10 --tier=smoke      # explicit phase list
```

Output: aggregated table (per-phase × per-lang counts) with FAIL
details inlined. Returns nonzero exit if any phase failed.

Implementation: shell-glue that loops over the existing per-phase
runners, passing through `--tier` / `--tag` / `--lang`. ~150 LOC.

## Per-phase migration tasks

Each existing phase needs a migration to the standard contract.
Order picked by ease + value (cheap-and-impactful first).

### Phase 9 — already done

`run_nested.sh` already supports per-lang explicit args and Phase
10's `run_perm.sh --tier=core` delegates to it. Add `--tag` filter
support: ~1h.

### Phase 10 — already done

Reference implementation. Other phases mimic this structure.

### Phase 2 (`@@persist`) — ~6h

- Tag every existing case in `gen_persist.py` with
  `persist,depth-N,domain-set,target-offset-N`.
- Define smoke as `depth=[0,1] ∧ domain=int`. Estimate: ~50 cases per lang.
- Define core as the regression cases that surfaced bugs during
  bring-up (~20).
- Update `run_persist.sh` to accept `--tier` / `--tag` / `--lang`.
- Emit per-lang summary in `logs_persist/per_lang/`.

### Phase 3 (`@@:self`) — ~5h

Same shape as Phase 2. Tag with `selfcall,linear|if-guarded|if-both,
post-N`. Smoke = linear only.

### Phase 4 (HSM parents) — ~5h

Tag with `hsm,depth-N,parent|sibling|uncle`. Smoke = depth-1 +
parent-returns + sibling.

### Phase 5 (Operations) — ~3h

Smaller corpus. Tag with `operations,caller-X,return-type-Y`.

### Phase 6 (Async) — ~4h

Tag with `async,await-N,phase-init`. Smoke = single-await only.

### Phase 7 (Multi-system) — ~4h

Tag with `multisys,domain|param,nested-N`. Smoke = system-in-domain
+ single cross-call.

### Phase 8 (Negative) — ~3h

Tag with `negative,error-code-EXXX`. Smoke = E601-E604 (the most
common framec validators).

### Top-level meta-runner — ~6h

`run_all.sh` orchestrating all phases.

### Tag taxonomy + audit — ~5h

Document the tag vocabulary in `TAG_VOCABULARY.md`. Audit existing
phases for taxonomy consistency.

### Verification — ~3h

Smoke loop (`run_all.sh --tier=smoke`) under 2 min, no flakes.
Full loop under 45 min. Cross-sectional queries return correct
case counts.

**Total**: ~45h infra + ~10h cleanup = **~55h**. Calling it 1.5 weeks
of focused work, parallelizable across phases (someone other than the
phase author can do the tagging mechanically).

## Wall clock budget targets

Based on Phase 10 measurements + extrapolation:

| Tier | Per-phase wall (typical) | Total parallel-by-lang | Total sequential |
|---|---|---|---|
| smoke | 5-30s | 1-2 min | 5-10 min |
| core | 20-60s | 3-5 min | 10-20 min |
| full | 1-15 min | 20-40 min | 1-2 hr |

Parallel-by-lang means each backend runs concurrently within a
phase. Phases run sequentially across each other (Phase 2 finishes
before Phase 3 starts) since most fuzz wall clock is interpreter /
compiler startup, which is per-process anyway.

For aggressive smoke: parallelize PHASES too. Each phase × backend
in its own process. Memory cost: ~100-200MB per concurrent process,
17 langs × 9 phases = 153 processes ≈ 30GB peak. Achievable on
a workstation; not desired for laptops. Default to per-lang
parallelism only; expose `--parallel-phases` flag for power users.

## Verification at end-of-infra-build

1. `run_all.sh --tier=smoke` completes in <2 min on a typical macOS
   workstation.
2. `run_all.sh --tier=full` completes in <45 min.
3. `run_all.sh --tag=erlang --tier=full` runs only Erlang cases
   across all phases; result count matches sum of per-phase Erlang
   counts.
4. `run_all.sh --tag=hsm,depth-2` runs only depth-2 HSM cases across
   all phases; result count matches sum of per-phase tag-matched
   counts.
5. No phase regresses (each phase's full count matches pre-migration
   baseline).

## Open questions

1. **Tag taxonomy ownership** — should `TAG_VOCABULARY.md` be
   authoritative (only documented tags are valid) or descriptive
   (any tag accepted, vocab doc is informational)? Authoritative is
   safer; descriptive is more flexible. Lean authoritative for v1.

2. **Smoke selection per phase** — automatic via tag heuristic, or
   manual per-phase curation? Phase 10 picks first-per-equiv-class;
   that worked. But other phases may not have a clean equivalence
   structure (Phase 8 negative cases are each independent). Probably
   per-phase manual curation, with a `tier=smoke` tag emitted by the
   generator.

3. **Phase 0 sequencing** — should the test infra layer be done
   serially (40-55h sprint) before any new phase work, or can it
   land per-phase as Phases 11-15 are built (each new phase ships
   its own tier+tag wiring matching the contract)? Serial is cleaner
   contract-wise; per-phase risks contract drift. Lean serial; can
   relax if 4.0 timeline forces parallelization.

4. **CI integration** — does Frame 4.0 ship with `run_all.sh
   --tier=smoke` wired into pre-commit / CI, or is the infra purely
   developer-side? Adds ~2 min to every commit if pre-commit; might
   want it as nightly-CI-only for 4.0.
