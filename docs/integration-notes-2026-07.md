# Integration notes — `integration/test-env-2026-07`

Coordination state for the July 2026 integration branch. This branch bundles
several independent test-env waves that are **not yet on `main`**. Everything
runs against the authoritative local `framec` build (see below); point the
suites at that binary and the numbers and verdicts hold.

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

### `@@fsm` suite requires the authoritative build

The `@@fsm` diagnostic suite asserts **specific** error codes; one fixture,
`transition_in_action_body.fpy` (`# expect-error: E712`), depends on framec#162.
That fix is carried by the authoritative local build (4.6.0.6), which the
harness defaults to, so the suite is green. Just point the runner at the
authoritative binary rather than an arbitrary PATH `framec`.

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
| framec#162 | `@@fsm` transition-in-action should emit E712 | fixed; carried by the authoritative local build (`4.6.0.x`) |
| framec#163 | E723 case | by-design (no change) |

## Merge-to-`main` checklist

1. `python scripts/check_coverage.py` → green (16/stem, no collisions).
2. `python scripts/check_docs.py` → green (table + counts in sync).
3. Full matrix + fuzz on the release commit against the authoritative build.
