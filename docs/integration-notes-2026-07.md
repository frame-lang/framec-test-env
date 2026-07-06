# Integration notes — `integration/test-env-2026-07`

Coordination state for the July 2026 integration branch. This branch bundles
several independent test-env waves that are **not yet on `main`**, and it has
a cross-repo dependency on a specific `framec` build. Read this before merging
to `main` or running the suites against a stock release binary — the numbers
and pass/fail verdicts below depend on *which* `framec` you point at.

## What this branch bundles

Merged onto `integration/test-env-2026-07` (see `git log main..HEAD` for the
authoritative list):

| Wave | Summary |
|---|---|
| #404 | Coverage-gate closure — all 641 remaining stems resolved to a real port or a documented `.skip.md`; gate is green at 16 enforced backends. |
| #20  | `@@fsm` negative-diagnostic suite (`tests/common/transpile-error/fsm/`) — asserts framec *rejects* invalid `@@fsm`; covers 13 of 14 §9 codes. |
| #22  | async×persist fuzz extension — `fuzz/run_all.sh` Phase 26, 11 async backends × 4 patterns. |
| #6   | `scripts/verify_local.sh` — host-side 17-backend fixture verifier. |
| #7   | closure of the inherited coverage gaps (skip.md). |
| #8   | authoritative-framec build reform (see below). |
| #9   | batch-build resilience — per-file failure isolation in the five batch-compile runners (rust/csharp/go/java/kotlin). |
| #10  | `scripts/check_docs.py` doc-freshness gate. |
| docker | framec-cache auto-trim + `make prune` (disk-leak fix). |

## framec build coordination (the important part)

**The authoritative binary is `~/.frame/local/bin/framec`** — the most recent
local build. Version scheme: the last release supplies the `x.y.z` ordinals
and `.n` is the local rev, e.g. `4.6.0.6`. Resolution order used everywhere in
the harness (runners, fuzz, fsm runner):

```
$FRAMEC  →  ~/.frame/local/bin/framec  →  first `framec` on PATH
```

### E712 / `@@fsm` suite is version-coupled — verify before merging

The `@@fsm` diagnostic suite asserts **specific** error codes. One fixture is
coupled to framec#162:

| fixture | framec 4.6.0.6 (local, authoritative) | framec 4.6.1 (a PATH release) |
|---|---|---|
| `transition_in_action_body.fpy` (`# expect-error: E712`) | rejects with **E712** ✓ suite passes | rejects with **E700** ✗ suite reports `expected E712, got E700` |

Key nuance: on **both** builds framec *rejects* the invalid input (rc=65) —
**there is no silent-miscompile exposure on 4.6.1.** Only the *precise-code*
assertion is version-coupled: the E712 diagnostic from framec#162 lives in the
`4.6.0.x` local line; the `4.6.1` release cut emits the coarser E700 for the
same input. Because every harness component defaults to the authoritative local
build (#8), the suite is green by default; it only fails if you force
`FRAMEC=$(command -v framec)` onto a 4.6.1 release.

**Implication for merging to `main`:** if `main`'s CI/RC runs the fsm suite
against a stock **4.6.1** binary, expect **1 failure** (E712→E700) until either
the E712 diagnostic lands in the released line, or the fixture is relaxed to
accept E700 as an alternative. This is the one known precondition gating the
merge; nothing else on the branch is framec-version-sensitive in a
pass/fail-changing way.

## Standing constraints

- **Erlang (`ferl`) is deprecated / being retired this release.** The coverage
  gate enforces **16** backends (Erlang excluded — see `check_coverage.py`
  `BACKENDS`). Existing `.ferl` fixtures and `.ferl.skip.md` placeholders are
  retained but not enforced; do not add new Erlang machinery. The
  "Supported Languages" table still lists Erlang as *Deprecated* so the
  17-vs-16 distinction stays legible — `scripts/check_docs.py` enforces that
  split (16 = gate, 17 = languages the dispatch can still target).

## Filed framec issues

| issue | subject | status |
|---|---|---|
| framec#162 | `@@fsm` transition-in-action should emit E712 | fixed in the `4.6.0.x` local line; **not yet in the 4.6.1 release** (emits E700) |
| framec#163 | E723 case | by-design (no change) |

## Merge-to-`main` checklist

1. `python scripts/check_coverage.py` → green (16/stem, no collisions).
2. `python scripts/check_docs.py` → green (table + counts in sync).
3. Decide the fsm E712 precondition: confirm the 4.6.x-released framec that
   `main` will run against emits E712, **or** relax
   `transition_in_action_body.fpy` to accept E700. Do not merge with the
   assertion mismatched against the release binary.
4. Full matrix + fuzz on the release commit against the authoritative build.
