# Future enhancements — test environment

Optimization opportunities that have been investigated but not (yet)
implemented. Each entry has a rough effort estimate and a clear
expected payoff so future work can grab the highest-impact item that
fits the available time budget.

## Background: where wall-clock time goes today

After the 2026-05-03 perf wave (gdscript batching `fe7ac063`,
erlang batching `0ce91e61`, go single-build `8e110dc2`, dart
no-link-platform `0829e692`), the full matrix runs in **~96 s**
on the matrix host (8-core).

Per-language wall-clock under matrix load (sorted slowest-first,
solo runs with warm caches):

| Lang | Wall-clock | Bottleneck |
|---|---|---|
| kotlin | ~18 s | single batched `kotlinc` JVM |
| erlang | ~18 s | batched `erl -run` (was 22 s; per-test escripts now collapse into ~5 BEAM starts) |
| rust | ~14 s | one `cargo build` for all bins |
| dart | ~10 s | per-test `dart compile kernel --no-link-platform` (parallel; was 18 s) |
| swift | ~10 s | per-test `swiftc` (parallel) |
| c | ~7 s | per-test `gcc` (parallel; ccache warm) |
| go | ~7 s | one `go build ./cmd/...` (was 17 s with per-test builds) |
| csharp | ~5 s | one `dotnet build` |
| java | ~5 s | one `javac` |
| cpp | ~4 s | per-test `g++` (parallel; ccache warm) |
| gdscript | ~3 s | one Godot process running batch harness (was 44 s with per-test cold starts) |
| typescript | ~3 s | one `tsx` process |
| python | ~3 s | one `python3` import-each |
| ruby, php, lua, javascript | <2 s | interpreted, fast |

The matrix wall-clock (96s) is bound by the slowest container.
The current top three (kotlin / erlang / rust) all use one
process internally already; further wins would come from
in-process framec API (#171) eliminating subprocess fork-exec
per test, or per-container parallelism tuning (#162).

## Open opportunities

<!-- Item 1 (GDScript batching) shipped 2026-05-03 in `fe7ac063`.
Empirically discovered that `quit()` in a `script.new()`-instantiated
SceneTree subclass exits only the inner SceneTree, not the parent
harness — so no fixture rewrite was needed. See "Closed" below. -->

### 2. Per-container parallelism: granular tuning
**Effort:** small · **Expected payoff:** marginal (5–10 s).

Today every parallel-stage container uses the same `MATRIX_JOBS=4`
cap. In practice the heavy compilers (kotlin, cpp, swift) have
different sweet spots. cpp's per-test g++ benefits from higher
parallelism than rust's per-test exec stage because cpp's jobs are
short-lived and CPU-bound while rust's are linker-bound.

A more granular tuning would profile each container's optimal
JOBS-per-host-core ratio under matrix load and set them
individually. Probably:

```make
CPP_COMPILE_JOBS=6
SWIFT_COMPILE_JOBS=4
DART_COMPILE_JOBS=4
GO_COMPILE_JOBS=6
ERLANG_TEST_JOBS=8
RUST_EXEC_JOBS=8
```

The right numbers come from a 5-run average per setting, not from
intuition.

<!-- Item 3 (ccache for cpp / c) shipped 2026-04-26 in `2e83816`. See
the "Closed" section for the actual numbers. -->

<!-- Item 4 (single-go-build) shipped 2026-05-03 in `8e110dc2`. Tests
are laid out as sub-packages under one Go module
(`/go_runner/cmd/<sanitized>/main.go`); a single
`go build ./cmd/...` produces all binaries. Go: 17 s → 6.7 s. -->

<!-- Item 5 (Dart aot-snapshot) investigated 2026-05-03 — N/A. AOT
compile is ~3.4× slower than kernel and the faster exec doesn't
recover. Kernel mode wins. Instead, `--no-link-platform`
(`0829e692`) skips embedding the 7.9 MB platform kernel per .dill;
Dart 18 s → 10.1 s. -->

<!-- Item 6 (Erlang single-erlc) shipped 2026-05-03 in `0ce91e61` via a
different mechanism than originally proposed. Generated escripts are
converted to callable modules (`-module(test_<id>). run() -> ...`)
and batch-executed via a single `erl -run` shell using
load_dir_modules / purge_dir_modules to handle short-name collisions
across tests. Erlang 22 s → 18 s. -->

<!-- Item 7 (PCH for C) investigated 2026-05-03 — N/A. C is already
~6 s for 265 tests (~24 ms/test). Per-step gcc breakdown: cold
compile 41 ms, preprocess 8 ms, link 9 ms. PCH would save ~2 s
total — not worth the integration cost on top of ccache. -->

### 8. Stagger heavy containers in the orchestrator
**Effort:** medium · **Expected payoff:** uncertain; potentially
~10–15 s.

Today `docker compose up -d $LANGS` starts all 17 containers at the
same instant. The first 30 s have all of them in heavy compile
phase together — peak contention. Staggered starts (kotlin first,
swift 5 s later, …, lightweight langs last) would smooth the
contention curve. Risk: complicates orchestration; could regress
into OOM territory if too many heavies overlap. Worth pairing with
fine-grained profiling first.

### 9. Reduce framec re-invocations via in-process API
**Effort:** large · **Expected payoff:** ~10–15 s (framec startup
cost adds up across the matrix).

Each test calls framec as a subprocess. framec startup itself
costs ~30 ms × ~3,500 tests across 17 languages = ~100 s
amortised. An in-process Rust binding (or JSON-RPC daemon) would
avoid the per-call startup. This is a meaningful refactor of the
test infrastructure and only worthwhile if matrix wall-clock
becomes a bottleneck for the project (currently it isn't).

## Closed (already implemented)

- ✅ Docker memory bump (host) → 15.6 GB
- ✅ kotlin `-J-Xmx2g` → `-J-Xmx4g` (`c3e2740`)
- ✅ Parallelize erlang `erlc` step (`13267d8`)
- ✅ kotlin OOM-retry on SIGKILL (`56132ca`)
- ✅ Per-container `MATRIX_JOBS=4` cap in matrix mode (`6d7dc22`)
- ✅ `framec_cached` source-hash cache (pre-existing)
- ✅ Per-language `_batch.sh` runners with parallel stages (pre-existing)
- ✅ ccache for cpp / c (`2e83816`, 2026-04-26) — split compile/link
  + framec_cached on c. Matrix wall-clock 128 s → 103 s on warm runs.
- ✅ Deterministic C codegen (framepiler `72f3ea5`, 2026-04-26) —
  iterate `machine.states` (Vec) instead of `arcanum.get_enhanced_states()`
  (HashMap) and sort handlers by event name. ccache hit rate 69% → 76%
  on c/cpp warm runs.
- ✅ GDScript single-Godot batch harness (`fe7ac063`, 2026-05-03) —
  one Godot process loads each test via `script.new()` from a parent
  SceneTree subclass. Inner `quit()` exits the inner SceneTree
  without killing the parent (empirically verified). Markers
  (`==FRAME-TEST-BEGIN/END==`) slice batch output per-test. GDScript:
  44 s → 3.6 s (12×). No fixture rewrite required.
- ✅ Erlang escript→module batching (`0ce91e61`, 2026-05-03) —
  generated escripts converted to callable modules
  (`-module(test_<id>). run() -> ...`), batch-executed via a single
  `erl -run` shell. `load_dir_modules` / `purge_dir_modules` per-test
  handles short-name collisions (e.g. `s` shared across tests).
  Sidecar drivers fall back to legacy escript path. Erlang: 22 s → 18 s.
- ✅ Single Go build across tests (`8e110dc2`, 2026-05-03) — tests
  laid out as sub-packages under one Go module
  (`/go_runner/cmd/<sanitized>/main.go`); a single
  `go build ./cmd/...` builds all binaries. Toolchain parallelises
  internally. Go: 17 s → 6.7 s (2.5×).
- ✅ Dart `--no-link-platform` (`0829e692`, 2026-05-03) — skip
  embedding the 7.9 MB platform kernel in each .dill; Dart locates
  it at runtime. Compile 229 ms → 185 ms, run 32 ms → 20 ms, .dill
  size 7.9 MB → 16 K (494× smaller — less I/O, more cache locality).
  Dart: 18 s → 10.1 s (1.8×).
