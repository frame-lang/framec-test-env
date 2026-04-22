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

| Backend     | `@@persist` | `@@:self` | HSM | Operations | Async | Multi-sys |
|-------------|-------------|-----------|-----|------------|-------|-----------|
| Python      | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| TypeScript  | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| JavaScript  | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| Rust        | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| C           | ✓           | ✓         | ✓   | ✓          | ✗     | ✓         |
| C++         | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| C#          | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| Java        | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| Kotlin      | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| Swift       | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| Dart        | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| GDScript    | ✓           | ✓         | ✓   | ✓          | ✓     | ✓         |
| Go          | ✓           | ✓         | ✓   | ✓          | ✗     | ✓         |
| PHP         | ✓           | ✓         | ✓   | ✓          | ✗     | ✓         |
| Ruby        | ✓           | ✓         | ✓   | ✓          | ✗     | ✓         |
| Lua         | ✓           | ✓         | ✓   | ✓          | ✗     | ✓         |
| Erlang      | ✓           | ✓         | ✓   | ✓          | ✗     | ✗         |

**Concrete applicable-backend counts per phase:**

| Phase | Feature            | Applicable |
|-------|--------------------|------------|
| 2     | `@@persist`        | **17** (done: 1,377 checks) |
| 3     | `@@:self`          | **17** (done: 918 checks)   |
| 4     | HSM parent-semantics | **17**     |
| 5     | Operations         | **17**     |
| 6     | Async              | **11** — C, Go, PHP, Ruby, Lua, Erlang lack async semantics |
| 7     | Multi-system       | **16** — Erlang's gen_statem processes don't compose as in-process instances |

`✗` are permanent exclusions — language-incompat, not framec gaps.

## Exceptions & workarounds log

As of Phase 3 completion. Every non-trivial deviation from "pure
Frame source → clean trace-diff" is listed here. Categorized as:

  **[F]** Framec codegen bug — should be fixed in framec (filed).
  **[H]** Harness-layer translation — architecture, not exception.
         Lives in `langs.py` because it's per-target syntax mapping
         (e.g. `self.` → `this.` for JS) that framec deliberately
         leaves to the Frame author.
  **[S]** Scope reduction — axes narrowed vs. the original plan.

### [F] Framec codegen bugs still open

- **Kotlin `restore_state` emitted as instance method, not companion
  static.** Fuzz harness uses the `tmp = Sys(); tmp.restore_state(...)`
  workaround (same pattern the matrix tests use). Would benefit from
  framec Kotlin fix to move the method into `companion object { }`.
  FINDINGS #13 (not yet filed as a separate entry).

- **C#/Java domain type `str` / `bool` not auto-mapped to native
  `string` / `String` / `boolean`.** Framec emits raw Frame type
  tokens; harness does `str → string` / `bool → boolean` rewrite.
  Framec should mirror what it already does for Rust (`str` →
  `String`) and Go (`str` → `string` — fixed this session).
  FINDINGS #12 + Java analogue.

### [F] Framec codegen bugs fixed this session

- Rust `str = ""` domain default ↦ `String::from("")` (`4b225f3`).
- Rust handler param `v: int` unpacked as String (same commit).
- Rust `rust_json_extract*` mapped Frame `int` → `i32` instead of `i64`
  (same commit).
- Rust `Box::new(self.<non_copy_field>)` didn't auto-clone (`f9bc737`).
- Go domain `str` not emitted as `string` (`1455d68`).
- Go `self.` not rewritten to `s.` inside `@@:()` return expression
  (same commit, hardened in `e6b921f`).
- Erlang `self.x = v;` record-update trailing-`;` parse error
  (`0132552`).

### [H] Harness-layer per-target syntax mappings

These are **not** exceptions — they're the expected architecture
where one Frame source is translated to each target's native syntax
before framec consumes it. Documented for audit:

- `self.` → `this.` (JS, TS, Kotlin, Dart, C#, Java)
- `self.` → `this->` (C++, PHP via `$this->`)
- `self.` → `self->` (C pointer semantics)
- `self.` → `s.` (Go receiver convention; ONLY for cases where
  framec doesn't auto-rewrite — fixed the gap this session)
- `True` / `False` → `true` / `false` (every lang except Python)
- `str` → target native (`String` Rust/C#/Java; `string` Go/C++;
  `char*` C)
- `bool` → `boolean` (Java/Kotlin)
- `= v;` → `= $v;` (PHP param sigil)
- `@@:self.<method>()` preserved (Frame syntax, not native `self.`)

### [H] Per-backend runtime quirks handled transparently

- **Lua** `cjson` decodes ints as floats on round-trip; harness uses
  `string.format("%d", rest:get_x())` to coerce.
- **GDScript** Godot prints "Godot Engine v4.6.2 ..." banner on
  stdout; `gdscript_run_custom` strips it before the trace diff.
- **Erlang** module name = `snake_case(Frame system name)` and
  persist API is `load_state/1` not `restore_state/1`.
- **Kotlin** jar main class is `<source.stem.capitalize() + "Kt">`.
- **C++** prolog injects `#include <nlohmann/json.hpp>` because
  framec references `nlohmann::json` in save_state but doesn't emit
  the include itself (user-supplied per framec convention).

### [S] Scope reductions

- **Phase 3 `@@:self`**: dropped `if_guarded` and `if_both_arms` post-
  structures from the axes. Reason: they'd require per-target block-
  syntax rewriting (Python `if X:` vs C-family `if (X) { }`), which
  deserves a proper indent-aware transform, not a regex. Reinstating
  is a follow-up — would add ~108 cases.
  Current: 3 × 3 × 2 × 3 × **1** = 54 cases (was 162 in plan).

### [S] Scope not reduced anywhere else

Phase 2 persist runs every axis in the plan. Remaining phases will
match the plan as written unless a real framec gap forces a drop.

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
VARIANTS × POST_CALL_STMTS × POST_STRUCTURE. Expected: 162 × 17 =
**~2,754 cases**. **Done**: 54 × 17 = 918 checks clean; the missing
108 cases per backend are the `if_guarded` / `if_both_arms`
post-structure variants held back pending block-syntax transform
(see Exceptions & workarounds).

### Phase 4 — HSM parent-semantics fuzz (1 day)

New fuzzer. Axes:
- Parent handler returns (no transition), transitions to sibling,
  transitions to uncle (cross-subtree).
- Child emits side effect before event, parent's handler runs after
  `=> $^` — assert child's post-forward code did NOT run (the same
  guard-semantics class that bit us in Erlang @@:self).
- 2-level and 3-level HSM.

Expected: ~400 cases × 17 backends = **~6,800 cases**.

### Phase 5 — Operations fuzz (1 day)

Axes:
- Called from interface, called from another operation, called from
  action.
- With `static`, without.
- Return type int/str/void; operation uses `@@:(expr)` vs
  `@@:return(expr)`.
- Operation reads domain, operation writes domain.

Expected: ~200 cases × 17 backends = **~3,400 cases**.

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

Expected: ~150 cases × 16 backends = **~2,400 cases**. (Erlang
excluded — gen_statem processes can't be composed as in-process
instances.)

## Grand-total projected coverage

| Phase | New cases  | Cumulative | Status                 |
|-------|------------|------------|------------------------|
| Now   |     3,610  |     3,610  | legacy baseline        |
| 2     |     1,377  |     4,987  | **done** (17 × 81)     |
| 3     |       918  |     5,905  | **done** (17 × 54; full axis reinstatement later adds ~1,836) |
| 4     |    ~6,800  |   ~12,705  | next                   |
| 5     |    ~3,400  |   ~16,105  |                        |
| 6     |    ~1,100  |   ~17,205  | 11-backend subset      |
| 7     |    ~2,400  |   ~19,605  | 16-backend subset      |

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
