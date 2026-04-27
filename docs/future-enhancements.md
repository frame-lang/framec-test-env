# Future enhancements — test environment

Optimization opportunities that have been investigated but not (yet)
implemented. Each entry has a rough effort estimate and a clear
expected payoff so future work can grab the highest-impact item that
fits the available time budget.

## Background: where wall-clock time goes today

After the round of optimizations in commits `c3e2740` (kotlin -Xmx
bump), `13267d8` (parallel erlc), `56132ca` (kotlin OOM-retry), and
`6d7dc22` (per-container parallelism cap), the full matrix runs in
~128 s on a 12-core host with 15.6 GB Docker memory.

Per-language wall-clock under matrix load (sorted slowest-first):

| Lang | Wall-clock | Bottleneck |
|---|---|---|
| kotlin | ~125 s | single batched `kotlinc` JVM |
| cpp | ~125 s | per-test `g++` (parallel) |
| gdscript | ~110 s | per-test `godot --headless` cold start |
| erlang | ~95 s | per-test `escript` cold start |
| rust | ~90 s | one `cargo build` for all bins |
| go | ~90 s | per-test `go build` (parallel) |
| dart | ~90 s | per-test `dart compile kernel` (parallel) |
| c | ~70 s | per-test `gcc` (parallel) |
| swift | ~60 s | per-test `swiftc` (parallel) |
| csharp | ~45 s | one `dotnet build` |
| java | ~40 s | one `javac` |
| typescript | ~25 s | one `tsx` process |
| python | ~25 s | one `python3` import-each |
| ruby, php, lua, javascript | <10 s | interpreted, fast |

The matrix wall-clock is bound by the slowest container. Anything that
shaves the top three (kotlin / cpp / gdscript) drops total wall-clock;
anything that shaves the lower tiers does not.

## Open opportunities

### 1. GDScript — batch tests in fewer Godot processes
**Effort:** medium · **Expected payoff:** ~50 s solo, possibly ~20 s
matrix (gdscript is currently ~110 s in matrix; cutting it doesn't
necessarily reduce wall-clock unless cpp / kotlin shrink too).

Each test is a fresh `godot --headless --script <file>` invocation
that pays a 1–2 s cold start. With 217 tests at 6-way parallelism
that's ~50 s of pure startup overhead.

A single Godot process *can* execute multiple SceneTree scripts in
sequence via `load()` and instantiation, so a wrapper `.gd` driver
could run a manifest of tests in one process. The complication: each
test currently calls `quit()` at the end, which terminates the whole
SceneTree. The driver needs each test to signal completion without
quitting, then advance to the next.

Sketch:

```gdscript
# /opt/test_runner.gd
extends SceneTree
var tests: Array
var idx := 0
func _init():
    tests = read_manifest("/tmp/gd_manifest.tsv")
    next_test()
func next_test():
    if idx >= tests.size(): quit(); return
    var t = tests[idx]; idx += 1
    var s = load(t).new()
    # capture s.run() output, classify, emit TAP
    next_test()
```

Risk: every existing `*.fgd` test extends SceneTree and calls
`quit()`; rewriting them is a big touch. Alternative: have the
driver `instantiate` each test, set a flag the test checks instead
of `quit()`, and re-emit the test source through framec with
`@@target gdscript_runner` mode. Either path is a substantial
refactor.

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


### 4. Single-go-build across tests
**Effort:** medium · **Expected payoff:** ~30 s (go: ~90 s → ~60 s).

`go build` cold-starts the toolchain per test. A single
`go build ./...` over a tests/ directory containing one `main`
package per test would amortise the toolchain init across all
tests. Current per-test `main` packages collide; the workaround
is per-test directory. Going to `go build` of all dirs at once is
viable but needs the test runner to walk the resulting bin/
directory rather than expecting per-test bin paths.

### 5. Dart — `dart compile aot-snapshot` instead of kernel
**Effort:** small · **Expected payoff:** uncertain; may slow exec
phase by enough to net-negative.

`dart compile kernel` produces a `.dill` file the VM JITs at run
time; the VM cold start adds ~1 s per test. `dart compile
aot-snapshot` produces a native binary that runs immediately but
takes longer to produce. For a test suite with many short runs and
one compile per test, AOT may be a wash. Worth measuring before
committing to the change.

### 6. Erlang — single erlc, multi-source
**Effort:** small · **Expected payoff:** ~10–20 s (erlang: 15 s solo →
~5 s solo; matrix benefit smaller).

`erlc *.erl` compiles N files in one BEAM startup. Currently we
parallelise N invocations of `erlc -o <dir> <one_file>`. A single
invocation amortises the cold start across all files. The challenge:
each test's .erl lives in its own work_dir for namespace isolation.
Either flatten everything into one dir (with sanitized filenames so
no collisions) or use multiple `-o` flags — neither is supported
out of the box. Easiest: invoke `erlc` once per work_dir but
batched, so we still pay N BEAM startups but with fewer xargs
spawns.

### 7. Pre-compiled C runtime header
**Effort:** small · **Expected payoff:** ~10–20 s (c: ~70 s → ~50 s).

The C runtime (FrameVec, FrameDict, etc.) is currently inlined into
every generated .c file. A shared `frame_runtime.h` precompiled
with `gcc -x c-header` would let each test compile only the
test-specific code. Generated source would `#include
"frame_runtime.h"` instead of inlining the runtime. Same idea
applies to C++ if its runtime headers grow.

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
