# Framec Fuzz Plan — Full 17-Backend Runtime Coverage

## Goal

Every Frame semantic feature exercised at runtime against **every backend
that supports it**. Failures are byte-level trace divergences, not just
compile errors. Today we have:

- **2,800** structural cases × 14 backends (compile-only)
- **324** `@@persist` runtime cases × 2 backends (Python, JS)
- **486** `@@:self` runtime cases × 3 backends (Python, JS, Erlang)

Target end state:

- All runtime fuzzers apply to all applicable backends (~12–17 each).
- Each case is a single Frame source compared across N backends via a
  shared trace oracle — any divergence is a blocker.
- ~50,000 runtime-semantic cases passing, bug-free.

## Core architecture: the differential trace harness

The current runtime fuzzers each bundle a language-specific harness into
the generated Frame source. That doesn't scale: 17 harness variants per
fuzzer, each independently drift-prone. Replace with a **generator
+ wrapper template** split:

**Generator emits** a pure-Frame `@@system` block with:
- Interface methods named predictably (`op_00()`, `op_01()`, …)
- Every handler body prints a single `TRACE:` line at well-defined points
  (entry, exit, transition, return value). Trace lines are
  language-agnostic: `TRACE: op_00 -> $S1` / `TRACE: ret 42` /
  `TRACE: state $S2 x=7 y="hi"`.

**Per-language wrapper templates** (one per backend, ~30 LoC each)
render the generated system into a runnable program that:
1. Instantiates the system.
2. Calls a fixed event sequence (encoded in the source as a comment
   like `# SEQ: op_00, op_01, save, restore, op_02`).
3. Dumps the final trace to stdout.

**Runner** (new `run_diff.sh`):
1. Transpile the one Frame source to each applicable target.
2. Compile + run each; capture stdout.
3. `diff` every trace against the Python reference trace; fail on any
   byte-level divergence.

**Why trace diff, not PASS/FAIL:** bugs like the Erlang arm-unification
one produce subtly-wrong state, not crashes. A byte-diff surfaces them
immediately. The Python oracle is cheap to generate (Python is the
fastest-to-iterate backend and its semantics are the spec).

### Trace format (contract)

Every backend must emit the same byte sequence. Stable rules:
- One event per line, prefixed `TRACE: `.
- Integers: decimal, no leading zeros, no `+`.
- Strings: double-quoted, no escaping of non-printable bytes (generator
  avoids them).
- Bools: lowercase `true` / `false`.
- Floats: **excluded** from fuzz axes (language variance is inherent).
- Enum-like state names: `$StateName` with the `$` literal.
- Order: generator emits explicit event calls in a fixed sequence; the
  trace is that sequence's result.

Discrepancies in trace format between backends are themselves bugs to
fix. The fuzzer is also a spec-enforcement tool.

### Wrapper-template contract

Each `wrappers/<target>.template` exposes three substitution points:

- `{{SYSTEM_SRC}}`  — the `@@system` block from the generator.
- `{{INSTANTIATE}}` — how to construct and run the event sequence.
- `{{DUMP}}`       — how to serialize the final trace array to stdout.

`wrappers/` sits at `fuzz/wrappers/` and each template is the smallest
valid harness for that language (think "shortest program that can
instantiate a Frame system, fire N events, print a captured
trace"). Keeping them tiny keeps drift local.

## Backend applicability matrix

Resolved in Phase 1.1 by compiling a minimal `@@persist` system across
all 17 backends and inspecting the generated save/restore API. **All 17
backends emit persist code.** Naming varies — see the persist API
table below; capture the quirks once in `diff_harness/langs.py`.

| Backend     | `@@persist` | `@@:self` | Async | Operations | Multi-sys |
|-------------|-------------|-----------|-------|------------|-----------|
| Python      | ✓           | ✓         | ✓     | ✓          | ✓         |
| TypeScript  | ✓           | ✓         | ✓     | ✓          | ✓         |
| JavaScript  | ✓           | ✓         | ✓     | ✓          | ✓         |
| Rust        | ✓           | ✓         | ✓     | ✓          | ✓         |
| C           | ✓           | ✓         | ✗     | ✓          | ✓         |
| C++         | ✓           | ✓         | ✓     | ✓          | ✓         |
| C#          | ✓           | ✓         | ✓     | ✓          | ✓         |
| Java        | ✓           | ✓         | ✓     | ✓          | ✓         |
| Kotlin      | ✓           | ✓         | ✓     | ✓          | ✓         |
| Swift       | ✓           | ✓         | ✓     | ✓          | ✓         |
| Dart        | ✓           | ✓         | ✓     | ✓          | ✓         |
| GDScript    | ✓           | ✓         | ✓     | ✓          | ✓         |
| Go          | ✓           | ✓         | ✗     | ✓          | ✓         |
| PHP         | ✓           | ✓         | ✗     | ✓          | ✓         |
| Ruby        | ✓           | ✓         | ✗     | ✓          | ✓         |
| Lua         | ✓           | ✓         | ✗     | ✓          | ✓         |
| Erlang      | ✓           | ✓         | ✗     | ✓          | ✗         |

`✗` are permanent exclusions — language-incompat, not framec gaps.

### Persist API naming across backends (from Phase 1.1 probe)

Codegen emits each backend's persist methods with slightly different
names. The wrapper per backend has to know these:

| Backend    | Save method              | Restore call                             | Blob type       |
|------------|--------------------------|------------------------------------------|-----------------|
| python_3   | `save_state()`           | `P.restore_state(data)` static            | bytes (pickle)  |
| javascript | `saveState()`            | `P.restoreState(json)` static             | string (JSON)   |
| typescript | `saveState()`            | `P.restoreState(json)` static             | string (JSON)   |
| rust       | `save_state(&mut self)`  | `P::restore_state(json)`                  | String (JSON)   |
| c          | `P_save_state(self)`     | `P_restore_state(json)` → `P*`            | `char*` (JSON)  |
| cpp        | `save_state()`           | `P::restore_state(json)` static           | std::string     |
| csharp     | `SaveState()`            | `P.RestoreState(json)` static             | string (JSON)   |
| java       | `save_state()`           | `P.restore_state(json)` static            | String (JSON)   |
| kotlin     | `save_state()`           | `P.restore_state(json)`                   | String (JSON)   |
| swift      | `saveState()`            | `P.restoreState(_ json)` static           | String (JSON)   |
| **go**     | `SaveState()`            | **`RestoreP(json)` package-level fn**     | string (JSON)   |
| php        | `save_state()`           | `P::restore_state($json)` static          | JSON string     |
| ruby       | `save_state`             | `P.restore_state(json)` classmethod       | JSON string     |
| lua        | `P:save_state()`         | `P.restore_state(json_str)`               | JSON string     |
| dart       | `saveState()`            | `P.restoreState(json)` static             | String (JSON)   |
| gdscript   | `save_state()`           | `P.restore_state(data)` static            | PackedByteArray |
| **erlang** | `p:save_state(Pid)`      | **`p:load_state(Map)` — note "load"**     | map             |

**Naming-consistency note (framec codegen follow-up):** case style is
inconsistent (snake_case vs camelCase vs PascalCase) and two backends
are outliers — Go's `RestoreP` is a package-level function, and Erlang
uses `load_state` instead of `restore_state`. Worth a separate issue to
unify once the harness is in place; for now the harness just carries
the quirks.

## Phase plan

### Phase 1 — Differential trace harness (1–2 days)

**1.1 Backend applicability smoke run.** Compile + run
`tests/common/positive/demos/18_session_persistence.f*` for every
backend; record pass/fail. Resolves the two `?` cells in the matrix.
Output: `applicability.tsv` consumed by the runner.

**1.2 Trace format spec.** Write `TRACE_FORMAT.md` nailing down the
contract above. Include a tiny reference trace generator in Python used
to build the oracle.

**1.3 Wrapper templates.** Port the 17 per-language wrappers from
existing gen scripts, stripped to the bare minimum (no per-case
specialization). Each ≤50 lines. Validated by running a fixed known-
good Frame source against all applicable targets and asserting all
traces diff-clean against Python's.

**1.4 Runner (`run_diff.sh`).** Takes a Frame source, produces per-
backend traces, diffs them. One backend's failure doesn't abort the
others — we want to see every divergence per run.

**Exit criterion Phase 1:** a canary test (simple 3-state machine + 3
events) passes diff-clean on all ~16 applicable backends.

### Phase 2 — `@@persist` on all backends (1–2 days)

Rework the existing `gen_persist.py` to:
- Emit pure Frame (no per-language harness inside).
- Encode the event sequence as a source comment (`# FUZZ_SEQ: …`).
- Keep all existing axes: STATE_COUNTS [2,3,5], HSM_DEPTHS [0,1,2],
  STATE_VARS on/off, DOMAIN_SETS {int, int+str, int+str+bool},
  TARGET_OFFSETS [0,1,2].

**162 cases × (backends with @@persist support from matrix).** Expected:
**2,430+ cases** (162 × ~15 backends).

Landing criteria:
- All cases pass diff-clean — any divergence is treated as a codegen
  bug to fix. Memory says we've already found Rust/Erlang/PHP bugs in
  this class; expect 2–5 more.
- `fuzz/run_persist.sh` replaced by `fuzz/run_diff.sh persist`.

### Phase 3 — `@@:self` on all backends (1 day)

Same treatment applied to `gen_selfcall.py`. Axes unchanged:
VARIANTS × POST_CALL_STMTS × POST_STRUCTURE. Expected: 162 × ~16 =
**~2,600 cases**.

### Phase 4 — HSM parent-semantics fuzz (1 day)

New fuzzer. Axes:
- Parent handler returns (no transition), transitions to sibling,
  transitions to uncle (cross-subtree).
- Child emits side effect before event, parent's handler runs after
  `=> $^` — assert child's post-forward code did NOT run (the same
  guard-semantics class that bit us in Erlang @@:self).
- 2-level and 3-level HSM.

Expected: ~400 cases × ~16 backends = **~6,400 cases**.

### Phase 5 — Operations fuzz (1 day)

Axes:
- Called from interface, called from another operation, called from
  action.
- With `static`, without.
- Return type int/str/void; operation uses `@@:(expr)` vs
  `@@:return(expr)`.
- Operation reads domain, operation writes domain.

Expected: ~200 cases × ~16 backends = **~3,200 cases**.

### Phase 6 — Async fuzz (1–2 days, narrower)

Async is 11-backend. Axes:
- Single await in handler body, two sequential awaits, await-then-
  transition, await-then-mutate-domain.
- Two-phase init with async enter handler.

Expected: ~100 cases × 11 backends = **~1,100 cases**.

### Phase 7 — Multi-system fuzz (1 day)

Axes:
- System-in-domain (`logger: @@Logger()`).
- System-as-handler-param.
- Cross-system call, nested cross-system call.

Expected: ~150 cases × ~16 backends = **~2,400 cases**.

## Grand-total projected coverage

| Phase | New cases  | Cumulative |
|-------|------------|------------|
| Now   |     3,610  |     3,610  |
| 2     |    ~2,430  |    ~6,040  |
| 3     |    ~2,600  |    ~8,640  |
| 4     |    ~6,400  |   ~15,040  |
| 5     |    ~3,200  |   ~18,240  |
| 6     |    ~1,100  |   ~19,340  |
| 7     |    ~2,400  |   ~21,740  |

Well under 50k — tight enough that a full fuzz run fits in a coffee-
break, loose enough that it's catching real bugs per phase.

## Operational details

**Timing per case:** current persist/selfcall fuzzers run ~200 cases/min
on a single backend. Differential harness runs slower (N transpiles +
compiles + runs per case). Target: full fuzz run < 20 min for all
phases × all backends on one machine. Budget 1 second per case wall
time across all backends.

**CI integration:** nightly full run + per-PR smoke (100 cases from each
phase). Pre-commit runs no fuzz (kept cheap).

**Failure triage:**
1. Diff the failing trace pair. Byte-level → codegen bug.
2. If multiple backends diverge the same way from Python, the bug is
   probably in Python's trace or the trace-format spec itself.
3. If only one diverges, it's a codegen bug in that backend. File +
   fix in framec, not the fuzzer.

**When to treat a gap as legitimate:** language-incompat (async in C,
one-class-per-file in Java, etc.) → mark `✗` in matrix and skip. Never
`✗` a gap that framec could close; raise it as a codegen bug.

## Risks

1. **Trace format ambiguity.** Float formatting, integer overflow,
   Unicode — any of these leaks cross-backend variance that isn't
   actually a framec bug. Mitigation: aggressive type restriction in
   generators (int in `[-1000, 1000]`, ASCII-only strings, no floats).

2. **Per-language wrapper drift.** A wrapper template that silently
   initializes state differently from another would mask real bugs.
   Mitigation: canary test in Phase 1.4 — all wrappers must match on a
   known-good source before *any* fuzz runs.

3. **Event sequence complexity.** If the generator emits unreachable
   events (e.g. `pop$` with empty stack), every backend might produce
   different error behavior. Mitigation: generator guarantees each
   emitted event is reachable from the current state (track a shadow
   state during generation).

4. **@@persist serialization format divergence.** Each backend's
   `save_state()` returns a different envelope (Python pickles, JS
   stringifies, etc.). We can't diff the blob — diff the POST-restore
   behavior trace instead. Already the design in the existing
   gen_persist.py; carry forward.

## Immediate next step

Start Phase 1.1: the applicability smoke run. That's 10 minutes of
bash to fill in the `?` cells before we design wrappers for backends
that might not support the feature at all.
