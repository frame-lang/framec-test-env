# Framec Fuzz Plan — Full 17-Backend Runtime Coverage

> **Companion docs:**
> - `TEST_INFRA_ROADMAP.md` — unified runner contract (tier + tag
>   filters, top-level meta-runner, smoke / full / cross-sectional
>   modes). Prerequisite for Phase 11+ work.
> - `DEFECTS.md` — open and closed framec defects surfaced by the
>   fuzz suite, including D1 (cross-backend self-call mid-expression
>   bug, fixed 2026-04-28).
> - `README.md` — quick-start usage and tier-model summary.

## Goal

Every Frame semantic feature exercised at runtime against **every backend
that supports it**. Failures are byte-level trace divergences, not just
compile errors.

**Phases 1-10 status (2026-04-28):**

- Phase 1 (trace harness): shipped.
- Phase 2 (`@@persist`): 1,377 cases × 17 backends, clean.
- Phase 3 (`@@:self`): 2,646 cases (16 langs full + Erlang 54 of 162).
- Phase 4 (HSM parents): 1,377 cases × 17, clean.
- Phase 5 (Operations): 459 cases × 17, clean.
- Phase 6 (Async): 220 cases × 11 wired backends.
- Phase 7 (Multi-system): 168 cases × 14 backends.
- Phase 8 (Negative): 18 codes × 17 backends.
- Phase 9 (Nested syntax): 5 patterns × 17 = 85 cases, clean
  (curated regression tier).
- Phase 10 (Expression cross-product): v2 = 460 cases × 17 = 7,820
  cases, clean. D1/D2/D3 closed.

Target end state:

- All runtime fuzzers apply to all applicable backends (~11–17 each).
- Each case is a single Frame source compared across N backends via a
  shared trace oracle — any divergence is a blocker.
- ~30,000 runtime-semantic cases passing, bug-free, partitioned across
  Frame 4.0 / 4.1 / 4.2 release traunches (see "Release traunching"
  section below).

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

- **Phase 3 `@@:self`** — **reinstated** (all three post_structure
  axes now run: `linear`, `if_guarded`, `if_both_arms` = 162 cases).
  The harness ships an indent-aware block-syntax transform
  (`_transform_py_if_blocks` in `langs.py`) with per-target
  specializations:
    - C-family (JS, TS, Kotlin, Dart, C#, Java, C, C++, Swift, Rust,
      Go, PHP): `if (X) { … } else { … }`
    - Ruby:    `if X … else … end`
    - Lua:     `if X then … else … end`
    - Python, GDScript: no transform — generator's canonical form
  Erlang explicitly skips `if_guarded` / `if_both_arms` via
  `Lang.case_supported` — its `if`/`case` syntax diverges
  structurally (expression-returning arms, `DataN` record-update
  chains, `,`-separated statements) and needs its own transform.
  Runs 54 of 162 applicable cases (108 skipped).

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
**~2,754 cases**. **Done**: 2,646 trace-diff checks clean (16 × 162 +
Erlang 54 applicable); 108 Erlang cases explicitly skipped by
`Lang.case_supported` pending an Erlang-specific if-to-case
transform (see Exceptions & workarounds [S]).

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

### Phase 9 — Nested Frame syntax fuzz

**Goal:** validate that Frame constructs nest recursively. Every
Frame segment accepts any sub-expression that is itself a Frame
segment (or a native expression that contains Frame segments).

**Patterns to cover:**
- `@@:self.foo(@@:return)` — `@@:return` as an arg
- `@@:self.foo(@@:params.x)` — `@@:params` as an arg
- `@@:(self.op(@@:return))` — self-call inside return expression
- `@@:return = @@:self.foo()` — self-call as return-value assignment RHS
- `$.var = @@:self.foo()` — self-call as state-var assignment RHS
- `@@:self.foo(self.op())` — operation call as an arg
- `@@:(self.op(@@:params.x))` — operation call with `@@:params` inside
- Two levels deep: `@@:self.foo(@@:self.bar(@@:return))` (if the
  spec allows)

**Contract:** the single generated Frame source compiles to every
backend with byte-identical semantic output. Nested Frame syntax
is expanded recursively at framec's segmentation / expansion stage
— NOT left verbatim in the target source.

**Expected:** ~60 cases × 17 backends = **~1,020 cases**.

**Current status:** Phase 9 harness landed. Defect #10 was closed
(framec recursively expands nested Frame syntax via
`expand_expression` in `frame_expansion.rs`). Harness covers
**11 patterns × 17 backends = 184 cases passing / 3 known
codegen defects surfaced** for follow-up:

- `dart/p11_statevar_lhs` — Dart's typed-lowering of
  `self.n + $.scache` emits `state_vars["scache"]` (dynamic)
  without an `as int` cast; `int + dynamic = num` fails the
  assignment back to `int n`.
- `erlang/p9_return_plus_transition` — `@@:return = N;
  @@:self.absorb(@@:return); -> $Done` produces an Erlang
  syntax error at the trailing semicolon. The transition-guard
  wrapping interacts badly with the explicit `-> $Done`.
- `erlang/p13_selfcall_arithmetic` — `@@:return =
  @@:self.compute() + 1` evaluates to 9 instead of 10. The
  Erlang codegen loses the `+ 1` arithmetic when the LHS of
  the operator is a `@@:self.method()` call.

Each is a concrete codegen finding. None are present in the
matrix (which uses explicit intermediates) — Phase 9 is
literally what surfaces them.

Lessons learned through the bring-up:
- drive() must return `int` for patterns that emit `@@:return`
  as a typed-int arg — gives framec the type hint for the
  Rust/Go/Swift downcast emit.
- drive() must be void for patterns that don't set @@:return
  (p2/p5/p6) — declaring `: int` makes Java's wrapper extract a
  never-set _return slot and NPE on the cast.
- Go capitalises interface methods by export convention; the
  fixture's method names + body references both need the
  capitalised form so framec's E601 case-match doesn't reject.
- Lua uses `:` for method dispatch (auto-self), `.` for field
  access; PHP uses `->` for both and `$` prefix on params.
- C lacks struct-method dispatch — bare `self.method()` in
  passthrough doesn't translate. The `op_call(lang, ...)`
  helper switches between language-native dot-call syntax and
  C's `<Sys>_<method>(self, args)` free-function form per
  backend.

The 7 patterns:

  - P1  `@@:self.foo(@@:return)`          — `@@:return` as arg
  - P2  `@@:self.foo(@@:params.x)`        — `@@:params` as arg
  - P3  `@@:(self.add_one(@@:return))`    — op-call with `@@:return`
  - P4  `@@:return = @@:self.compute()`   — self-call as `@@:=` RHS
  - P5  `self.cache = @@:self.compute()`  — self-call as field assign
  - P6  `@@:self.absorb(self.peek())`     — op-call as arg
  - P7  `@@:self.foo(@@:self.bar(@@:r))`  — two-level nest
  - P8  `@@:self.a(@@:self.b(@@:self.c(@@:r)))`  — three-level
  - P9  `@@:return = N; @@:self.absorb(@@:r); -> $Done` —
        return + transition same handler
  - P11 `$.scache = @@:self.compute()` — state-var as LHS
  - P13 `@@:return = @@:self.compute() + 1` — selfcall in
        native arithmetic

Each case is self-checking (Python/JS/TS/Ruby/Lua/PHP/Dart via
inline drivers; Erlang via an external escript that reads
`%% FUZZ_EXPECTED_N:`). Generator + runner: `gen_nested.py` /
`run_nested.sh`. Expanding to the remaining backends (csharp,
java, kotlin, c, cpp, gdscript) + the rust/go/swift defect fix +
~50 more pattern variations (HSM parents, transitions inside
nested args, push/pop interactions) follows the same shape —
bring up one backend at a time, assert against the same
expected-N contract.

### Phase 8 — Negative (passthrough-error) fuzz

**Goal:** validate that Frame's native-code passthrough model correctly
surfaces bad native syntax at the *target* compiler, not silently at
Frame. Every case is a Frame source that is valid Frame structurally
but contains a native expression that should fail in exactly one
backend's native compiler.

**Pattern:** the fuzz source emits, say, `return true` in an operation
body. Python compilation of that source must fail at the Python
interpreter (`NameError: name 'true' is not defined`), not at
framec. The oracle is the error class / message fragment expected
from the target compiler, pinned per-backend.

**Axes (draft):**
- bad_literal: `true`/`false` to a Python target, `True`/`False` to
  JS/Go/Rust, integer overflow literals, non-UTF8 string escapes.
- bad_identifier: camelCase in a snake_case-only spot, reserved
  keywords as variable names per-language.
- bad_type: using `string` in a Go spec (should be `string` works —
  but `str` wouldn't), using `Number` in a Rust spec, etc.
- bad_expression: Python-style `not x` in a brace-family target;
  C-style `x && y` in a Python target.

**Contract per case:**
```json
{
  "harness_kind": "negative",
  "expected": {
    "stage": "target_compile" | "target_runtime",
    "error_fragment": "NameError: name 'true' is not defined"
  }
}
```

**Framec MUST:**
1. Transpile without error (the Frame structure is valid).
2. Pass the bad native text through verbatim.
3. The target compiler/interpreter emits its native error.

**Framec MUST NOT:**
- Translate bad literals into "something that works" (that would
  hide the author's mistake).
- Silently drop or rewrite the offending token.
- Fail at the Frame stage for syntax it doesn't own.

**Runner behavior:** success = target compile/run failed with the
expected `error_fragment` substring. Failure = target compile/run
*succeeded* (framec translated something it shouldn't have) OR
framec itself failed (framec is validating native syntax it
shouldn't be).

Expected: ~50 cases × 17 backends = **~850 cases**. Each case is
authored, not generated, because the expected error text is highly
specific; a generator would hit the combinatorial explosion of
target error formats.

**Why this matters:** without negative fuzz, a framec regression that
silently rewrites `return true` → `return True` for Python (a hack
even if well-intentioned) would go undetected — the positive fuzz
would still pass, because the "fix" makes the bad spec work. Negative
fuzz locks in the contract that bad Frame specs fail where they
should: at the native compiler.

### Phase 10 — Full-permutation expression fuzz (shipped 2026-04-28)

**Goal:** exhaustive cross-product of Frame's expression-evaluation
codegen surface — receivers × operators × LHS targets × statement
context. Catches the operator-siblings of every spot-check pattern.

**Generator + runner:** `gen_perm.py` + `run_perm.sh`. First fuzz
phase with the unified tier+tag contract (smoke / core / full).

**Tier model:**
- Smoke: one case per coarse equivalence class. ~30-90 cases/lang,
  ~30s matrix wall clock.
- Core: delegates to `run_nested.sh` (Phase 9's curated patterns).
- Full: full cross-product. 460 cases/lang, ~20-30 min matrix wall
  clock at full parallelism.

**v2 axes (shipped):**
- Receivers (7): two int literals, domain field, state-var, parameter,
  two self-call shapes (`@@:self.compute()`, `@@:self.add_one(2)`).
- Operators (3): `+`, `-`, `*`.
- LHS targets (3): `@@:return =`, `self.<dom> =`, `$.<sv> =`.
- Depth ≤ 2.

**v3-v5 (deferred to 4.1):** more receivers (`@@:return` read,
`@@:params["x"]`), comparison operators (`==`, `!=`, `<`, `>`),
native-local LHS, transition placement, depth-3 nesting. Estimated
8-12 hours; saturates the expression-evaluation surface.

**Status (2026-04-28):** v2 = 7,820 / 7,820 passing across 17 langs.
Surfaced D1 (cross-backend mid-expression guard bug, fixed) and
D3 (Swift self-assign corpus issue, filtered). D2 design decision
codified in `docs/frame_runtime.md` Step 19: "transition check fires
at statement boundaries, not within statements."

**Frame feature gate:** none — all 17 langs.

---

### Phase 11 — Statement-pair sequencing (wave 1 shipped 2026-04-28)

**Goal:** Two-statement bodies × cross-product, testing how
`_transitioned`, `@@:return`, `@@:event`, `@@:params` flow between
adjacent statements within one handler.

**Axes:**
- Statement pair shapes: assignment + selfcall, selfcall + transition,
  selfcall + selfcall, return-write + transition, etc.
- Receivers and LHS from Phase 10 carried in.
- Whether statement #1 transitions or not.

**Wave 1 shipped:** 5 S1 × 5 S2 × 4 LIT = 100 cases × 17 langs =
1,700 case-runs. All passing on first run; no new defects surfaced.
Generator: `gen_stmt_pair.py`. Runner: `run_stmt_pair.sh`. Smoke:
~40s parallel (25 cases/lang). Full: ~8 min serial.

S1 kinds: `dom_w`, `sv_w`, `ret_w`, `sc_bare`, `sc_assign_dom`.
S2 kinds: `dom_to_ret`, `sv_to_ret`, `dom_plus_lit`, `sv_plus_lit`,
`dom_w_lit`. LITs: 1, 5, -3, 0.

**Wave 2 candidates (not yet shipped):**
- Add transition-bearing S1 (`-> $S1`) and/or S2.
- Add HSM × stmt-pair (parent vs sibling vs uncle transitions
  inside the second statement).
- Add `@@:event` and `@@:params` reads in S2 to exercise event-
  metadata flow across statements.

**Value density (post wave 1):** lower than predicted. Wave 1
expected to find 1-2 bugs based on Phase 9 p9/p11 history; found 0.
Either the framec defect tracker is closed for this shape, or the
remaining defects live in axes Wave 1 doesn't reach (transitions,
HSM, event metadata). Wave 2 should aim at those before declaring
the phase saturated.

**Frame feature gate:** none.

---

### Phase 12 — Control-flow embedding (proposed)

**Goal:** Frame expressions inside `if` / `while` conditions and
bodies. Tests guard injection in branched code paths.

**Axes:**
- Expression placement: condition vs. then-body vs. else-body vs.
  while-body.
- Embedded self-call vs. domain read vs. literal.
- Single-statement vs. multi-statement body.

**Estimated cases:** ~1,500 patterns × 17 = ~25,500 if 1-level
nesting. Smoke ~100 patterns (single-statement, `if` only).

**Value density:** high. Phase 9 p12 was deliberately omitted because
of `if` / `while` parser interaction — bugs likely there.

**Frame feature gate:** `if` / `while` syntax (already supported).

---

### Phase 13 — Identifier shadowing (proposed)

**Goal:** `self.x` vs `$.x` vs param `x` vs local `x` — does framec
correctly resolve scope when names collide?

**Axes:**
- Same name across (domain field, state-var, param, native local).
- Reading vs. writing each.

**Estimated cases:** ~30 patterns × 17 = ~500. Smoke ~10 patterns.

**Value density:** medium. Likely surfaces 2-3 framec scope bugs.

**Frame feature gate:** none.

---

### Phase 14 — HSM × everything (proposed)

**Goal:** Cross-product of Phase 4 (HSM) with Phases 2/5/6/7/10.
Tests that each feature behaves correctly under deep HSM hierarchies.

**Axes:**
- HSM depth: 1, 2, 3.
- Each feature (persist / operations / async / multi-system /
  expression) exercised per HSM level.

**Estimated cases:** depth × per-phase 80%-subset. Realistically
~3,000 × 17 = ~50,000 if fully cross-producted, or ~1,500 × 17 =
25,500 if capped at depth 2. Smoke ~depth-2 × Phase 5+10 ~500 cases.

**Value density:** medium-high. Each phase's HSM coverage is
currently shallow.

**Frame feature gate:** HSM (already supported).

---

### Phase 15 — State-arg propagation × everything (proposed)

**Goal:** Phase 4 covers HSM args narrowly. Cross-product with
Phases 2/5/6/7/10.

**Axes:** state-args declared at each HSM level × feature × passthrough.

**Estimated cases:** ~500 × 17 = ~8,500. Smoke ~50 patterns at 2-level
HSM.

**Value density:** high (state-arg propagation is a known framec
hot-spot).

---

### Phase 16 — Comment + whitespace robustness (proposed)

**Goal:** Frame source with embedded comments at every position
(handler-body, between segments, inside expressions) and unusual
whitespace. Tests scanner robustness.

**Axes:** comment placement × whitespace variations × per-language
comment leader.

**Estimated cases:** ~50 patterns × 17 = ~850. Smoke ~10 patterns.

**Value density:** low-medium. Scanner code is well-trodden.

---

### Phase 17 — Multi-event traces (proposed)

**Goal:** Send event A → B → C in sequence; assert compound trace
ordering. Tests stateful behavior across events.

**Axes:**
- Event sequence length (2, 3, 5).
- Mix of transitioning / non-transitioning events.
- Mix of self-calls, persist saves, async.

**Estimated cases:** ~200 × 17 = ~3,400. Smoke ~30 patterns.

**Value density:** medium.

---

### Phase 18 — Stress / boundary (optional)

**Goal:** Very deep state stacks, many transitions, large state-vars.
Tests runtime under load.

**Axes:** stack depth (100, 1000), transition count (1k, 10k),
state-var size (1KB, 1MB), domain size (100, 1000 fields).

**Estimated cases:** ~30 patterns × 17 = ~510. Smoke ~10 patterns.

**Value density:** low (likely surfaces perf issues, not correctness).

---

### Phase 19 — Push/pop modal stack (proposed)

**Goal:** `push$` / `pop$` interactions × everything. Phase 9 p11
(state-var round-trip) doesn't deeply test the modal stack.

**Axes:** push depth, modal context with state-vars / domain mods,
pop with explicit transition vs implicit return, push/pop in HSM.

**Estimated cases:** ~150 × 17 = ~2,550. Smoke ~20 patterns.

**Value density:** medium-high (push/pop is less-trodden code path).

---

### Phase 20 — Const fields + `@@:system` access (proposed)

**Goal:** const domain fields, `@@:system.state` reads, system params.

**Axes:** const-field-read at every position, `@@:system.state` in
handlers / conditions / expressions, system params × state init.

**Estimated cases:** ~100 × 17 = ~1,700. Smoke ~20 patterns.

**Value density:** low. Const fields are simple.

---

### Phase 21 — Type coercion edge cases (optional)

**Goal:** int → float, signed → unsigned, narrowing conversions.
Per-backend behavior may differ.

**Axes:** type pairs (~15 combinations), coercion direction.

**Estimated cases:** ~50 × 17 = ~850. Smoke ~10 patterns (int ↔ str).

**Value density:** low (but worth a smoke pass; likely surfaces 1-2
backend-specific bugs).

---

### Phase 22 — Panic / error recovery (optional)

**Goal:** What happens when a handler panics? Each backend has
different semantics (Rust panic, Java exception, Python raise, etc.).

**Axes:** panic in handler / self-call / transition.

**Estimated cases:** ~30 × 17 = ~510.

**Value density:** low (documents per-backend semantics, not framec
bugs). Optional.

---

### Phase 23 — Concurrency (optional)

**Goal:** Multiple threads / actors invoking the same system.

**Axes:** 2/4/8-thread dispatch × reads/writes.

**Estimated cases:** ~30 × applicable-langs (≤10).

**Value density:** low for framec correctness (Frame is single-
threaded by design). High for production-readiness claims.

---

## Wave-based expansion methodology

No upfront release-version traunching. Nothing is feature-deprecated,
so phases aren't gated by release boundaries. Instead, expansion
proceeds in waves once the test infra layer
(`TEST_INFRA_ROADMAP.md`) is in place.

### Wave shape

Each wave adds **+100 new tests per phase touched** (waves can
target one phase or multiple in parallel). After each wave:

1. Run the smoke tier across all phases — confirm wall clock stays
   within budget (~2 min target).
2. Run the full tier on the touched phases — measure bug-finding
   rate.
3. Decide next wave's targets based on bug-finding observed.

### Stopping criterion

Empirical, not numeric. We stop investing in a phase when bug-
finding tails off — the precise threshold is decided wave-by-wave.
A reasonable working guideline: "0 bugs in 2-3 consecutive waves"
suggests the phase is saturated for now; reallocate effort to
phases still finding bugs.

### What this replaces

The earlier Frame 4.0/4.1/4.2 release traunching is dropped.
Phase planning is now driven by:
- Test infra prerequisite (Phase 0) ships first.
- Then waves of +100 tests per phase, in whichever phase is
  currently producing the most bugs.
- Phases 11-23 come on-line opportunistically as bandwidth allows;
  no fixed ship-by-version commitments.

### Prerequisite ordering

1. **Test infra (Phase 0)** must land first — see
   `TEST_INFRA_ROADMAP.md`. ~55h.
2. **Existing phases (1-10)** retroactively standardized to the
   tier+tag contract during infra build (~40h is part of the 55h).
3. **New phases (11-23)** then come on-line one at a time, each
   shipping with the standard runner contract.

## Grand-total projected coverage

### Phases 1-10 (shipped)

| Phase | Cases passing | Status |
|---|---|---|
| 2 | 1,377 (17 × 81) | **done** |
| 3 | 2,646 (16 × 162 + Erlang 54; 108 Erlang skips) | **done** |
| 4 | ~6,800 (17 × 81 clean after Erlang post-fwd fix) | **done** |
| 5 | ~3,400 (17 × 27, 3×3×3 axes MVP) | **done** |
| 6 | ~220 (11-backend subset) | partial |
| 7 | ~168 (14 backends) | partial |
| 8 | ~306 (18 codes × 17) | shipped |
| 9 | 85 (5 patterns × 17, curated regression tier) | **done** |
| 10 v2 | 7,820 (460 × 17) | **done** |
| **Subtotal shipped** | **~22,800** | |

### Phases 11-23 (proposed, full-corpus ceilings)

| Phase | Smoke tier | Full corpus ceiling |
|---|---|---|
| 11 stmt-pair | ~850 | ~8,500 |
| 12 control-flow | ~1,700 | ~25,500 |
| 13 shadowing | ~170 | ~500 |
| 14 HSM × all | ~500 | ~25,500+ (depth-3 explodes) |
| 15 state-args × all | ~850 | ~8,500 |
| 16 comments | ~170 | ~850 |
| 17 multi-event | ~510 | ~3,400 |
| 18 stress | ~170 | ~510 |
| 19 push/pop | ~340 | ~2,550 |
| 20 const + @@:system | ~340 | ~1,700 |
| 21 type coercion | ~170 | ~850 |
| 22 panic | ~85 | ~510 |
| 23 concurrency | ~85 | ~300 |

Phases land via wave-based expansion (see "Wave-based expansion
methodology" above). Smoke tier target wall clock: ~2 min total.
Full tier target: ~30-45 min total.

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

## Immediate next step (updated 2026-04-28)

Phases 1-10 are shipped (see status at top of doc). The next blocking
work for Frame 4.0 is the **test infra layer** described in
`TEST_INFRA_ROADMAP.md` — unified runner contract (tier + tag filters,
top-level meta-runner, smoke / full / cross-sectional modes).
Without it, the new Phases 11-15 in 4.0 ship with ad-hoc per-phase
runners and we lock in another release cycle of the cross-cutting-
runner debt.

Sequence:
1. Test infra (Phase 0): ~55h.
2. Phase 11 (statement-pair) smoke: ~13h.
3. Phase 12 (control-flow) smoke: ~15h.
4. Phase 14 (HSM × all) smoke: ~15h.
5. Phase 15 (state-args × all) smoke: ~13h.

Total 4.0 effort: ~110-120h (3 weeks of focused work).

Earlier "next step" note (kept for historical context):
Phase 1.1 applicability smoke run was the original kickoff — that's
done; Phases 1-9 used its results.

## TODO: per-language guides — idiomatic Frame for each backend

Frame's "Oceans Model" (native code passes through to the target)
gives each backend its own idiomatic surface. Some patterns work
universally (Frame state machines, transitions, `@@:return`) but
others are target-specific in non-obvious ways:

- **Loop idioms** — Frame has two: (1) imperative `while cond { ... }`
  via native passthrough (only works on backends with a `while`
  keyword: every C-family + Python, but not Erlang); (2) state-flow
  loop where iteration is a state-machine self-transition (works
  everywhere). Erlang practitioners reach for idiom 2 by reflex
  because `gen_statem` already implements its state semantics via
  tail-position recursion. C-family practitioners default to idiom
  1 because it matches their loops. Same applies to recursion in
  general — Erlang programmers expect helper-level recursion in
  the prolog passthrough; C-family expect for/while inside handler
  bodies.
- **Async** — Frame async lowers to `await EXPR.method()` in
  Rust, `co_await EXPR.method()` in C++, `EXPR.method()` (suspend
  function) in Kotlin. The Frame source uses `await EXPR` and
  framec / harness rewrite per-target. Documenting which Frame
  source shapes are portable vs. need per-target rewriting is
  high-value.
- **Domain field types** — `: list` works on dynamic targets but
  needs a `typedef` workaround on C and a `Vec<T>` on Rust. The
  Frame source for C uses `typedef char* JobSlots[8];` in the
  prolog and `pending: JobSlots` in domain. This is non-obvious
  — would benefit from a guide.
- **Multi-system per file** — Java requires one public class per
  file; Erlang requires one module per file. Frame source with
  multiple `@@system` blocks must be split for those targets.
  Currently surfaced via `@@skip` on multi-system fixtures; a
  guide would pre-empt the issue.
- **String concat** — Python/JS/Java accept `String + String`
  natively; Rust requires `String + &String` (`.clone() + &`).
  The diff harness already rewrites `self.X + self.Y` for Rust
  (see `_rust_trace`); the equivalent rewrite for Frame source
  written by humans would be documented per-target.
- **String interpolation** — Python `f"…"`, JS template literals
  ``` `…${expr}…` ```, Erlang `io_lib:format/2`, C `snprintf`.
  Each is target-specific; the universal Frame syntax is
  `@@:(expr)` for return values + native string concat.
- **Return-type inference** — strongly-typed targets (TS / Java /
  Kotlin / Swift / C# / Dart / C / C++ / Go / Rust) emit
  `return …;` only when the source declares `(): type`; dynamic
  targets always emit a return. Already documented in
  `frame_runtime.md`'s "Return values across target languages"
  but a per-target cheat-sheet would surface the contract.

**Action:** create `docs/per_language_guides/<lang>.md` for each
of the 17 backends. Each file documents the target's idiomatic
Frame patterns, common gotchas, and the framec / harness
behaviours the user needs to know. Start with Erlang and Rust —
their idioms diverge most sharply from the C-family default and
they're the most common source of "framec doesn't do what I
expect" friction.

Cross-references:
- `docs/runtime-capability-matrix.md` for the per-backend
  capability table.
- `docs/erlang_alignment_requirements.md` for the existing
  Erlang-divergence catalogue (self-call guard mechanism).
- Frame source examples at
  `tests/common/positive/control_flow/while_*.ferl` for the
  state-flow loop idiom in Erlang.
