# The Maximal-Coverage Fixture Contract (`max_*` family)

**Living document.** Every `max_<lang>.f<ext>` fixture in this directory claims to
exercise "every Frame construct the backend supports." This document defines what
that claim must actually mean, records the per-language hazards that make each
backend's fixture different, and is amended every time a shipped bug reveals a
class of coverage the fixtures were missing.

Each fixture's header comment must link back here. When you change the contract,
sweep the fixtures; when a fixture teaches a new lesson, write it back into this
document.

---

## Part 1 — The origin lesson (#159): why tags are not coverage

framec#159 shipped through this suite in three waves — an indexed cross-system
call emitted as invalid C, then the same call skipped when the method name
collided with the caller's, then again when two *children* shared the name. All
three waves passed `max_c.fc`. The post-mortem found two distinct failures of
coverage, and they are now the first two rules of the contract:

**The fixture hand-lowered the construct it was tagged as covering.** max_c's
only cross-system call was written as `Sensor_bump(self->sensor);` — the
*already-lowered C output* — under a `[composition]` tag, instead of the portable
`@@:self.sensor.bump()` whose lowering is framec's job. The tag audit said
"composition ✓" while the compiler path under test never ran. A tag satisfied by
pre-lowered code covers the *feature's runtime shape* and none of the *compiler*.

**The fixture permuted single axes; the bugs were cross-products.** Each #159
wave was an interaction term: (indexed field) × (cross-system call) ×
(name collision with the caller / with a sibling child). max_c had the collision
ingredient (two systems with `tick`) and never combined it with a field call. The
fuzz program's standing lesson — *feature-cross-product axes have the highest bug
density* — applies to hand-written maximal fixtures exactly as much as to
generated corpora.

---

## Part 2 — The generic coverage pattern (every `max_<lang>` MUST)

### Rules

- **R1 — Exercise the lowering, never its output.** Every construct framec
  translates must appear in its **portable Frame spelling** (`@@:self.child.m()`,
  `@@:self.list[i].m()`, `@@:params.x`, …), never pre-lowered into the target's
  native form. Hand-lowered calls are permitted only as *control* assertions
  proving the runtime side independently — and must be tagged `[control:]`, not
  with the construct's coverage tag.
- **R2 — Include the cross-product block** (Part 3), not just per-construct
  marginals.
- **R3 — Include the name-collision axis.** Parent and children sharing event
  names (`tick`, `update`) is the *norm* for orchestrators, not an edge case.
  Somewhere in the fixture, the calling system and at least two child system
  types must declare the same interface method, and the fixture must dispatch it
  through both a scalar field and an indexed field.
- **R4 — Tags name compiler paths, not features.** A `[tag]` line asserts "this
  line makes framec run path X," and must be falsifiable by reading the emitted
  code. `[composition: native child call]` was the anti-pattern.
- **R5 — Self-asserting at runtime.** TAP output, run under the real toolchain
  (not compile-only), asserting observable behavior — independent instances,
  state round-trips, values — not just "it didn't crash."
- **R6 — Exclusions are explicit.** A construct the backend doesn't support gets
  an `EXCLUDED:` line in the header with the reason and, where one exists, the
  issue/RFC reference (e.g. async on C). Silence is indistinguishable from a gap.
- **R7 — Every closed codegen bug adds its shape here first.** Before the fix
  ships, the reproducing construct goes into the relevant `max_*` fixture(s) (or
  this contract, if it's a new class), so the suite would have caught it.

### The construct checklist

Every fixture covers each item below in portable form (or lists it under
`EXCLUDED:`):

| Area | Constructs |
|---|---|
| **Attributes** | `@@[main]`, `@@[persist(T)]` + `@@[save]`/`@@[load]`, `@@[create(name)]`, `@@[no_persist]`, `@@[target]` pruning, `@@[async]` where supported |
| **Interface** | typed + void methods, params, returns, defaults; async members where supported |
| **Machine** | flat + HSM (`=> $Parent`), enter/exit handlers with args, typed state-args, transitions with exit/enter/state args, forwards (`-> => $S`, with args), `push$`/`pop$` (incl. push-with-transition), `=> $^` parent forward |
| **Actions / Operations** | typed params + returns, conditionals in bodies, action invocation from handlers |
| **Domain** | typed fields, `const`, initializers (constant + runtime), composition — scalar child (`pen: Pen* = @@Pen()`-style per target idiom) **and array/list of children** in the target's visible element-type spelling |
| **References** | `@@:self` (read, write, self-call, field-call, **indexed field-call**, field-call with Frame-expression index), `@@:params.x`, `@@:data.x` (set/read/call-scope isolation), `@@:event`, `@@:return` (bare/assign/`(e)` short-circuit), `@@:(expr)`, `@@:system.state.name` |
| **Persist** | save → mutate → restore round-trip: domain fields, machine state, post-restore liveness; `@@[no_persist]` exclusion |
| **Cross-products** | the Part 3 block |
| **Native co-existence** | native control flow wrapping Frame statements, native comments, string literals containing Frame-lookalike sigils, statement-terminator conventions |

### The oracle

Where a language has a shipped baseline (the games ports use JS), the fixture's
assertions should mirror values the baseline produces, so a behavioral divergence
— not just a compile failure — is caught.

---

## Part 3 — The cross-product block (mandatory, all languages)

The distilled #159 family. Every fixture includes a system cluster shaped like:

```
@@system Child1 { interface: tick(dt) probe(): int ... }
@@system Child2 { interface: tick(dt) probe(): int ... }   // SAME method names

@@system Orchestrator {
    interface:
        tick(dt)                       // collides with both children
    machine: $S {
        tick(dt) { @@:self._tick_all(dt); }
    }
    actions:
        _tick_all(dt) {
            <native loop> {
                @@:self.kids[i].tick(dt)          // indexed × cross-system × caller-collision
            }
            @@:self.kids[@@:self.kn].probe()      // Frame-expression index
            @@:self.solo.tick(dt)                 // scalar sibling, same collided name
        }
    domain:
        kids: <visible array-of-Child1 spelling for this target>
        solo: <Child2 per target idiom> = @@Child2()
}
```

Assertions: every child instance advanced independently; the scalar sibling
advanced; values match across N ticks. The **visible element-type spelling** is
part of the point — hidden native typedefs (`GhostArr`) are opaque to
type-ignorant framec by design, and the fixture documents the supported spelling
per language (C: `kids: Child1*[4]` → emitted declarator `Child1* kids[4];`).

---

## Part 4 — Per-language sections

Each section: **General challenges** (how this language's semantics interact
with Frame's model) and **Specific examples** (concrete gotchas, with issue
references). C is the worked exemplar; the other sections start from the known
record and grow as each language goes through the same process.

---

### C — `max_c.fc` *(exemplar)*

**General challenges**

- **No methods, no `self`.** Every Frame call construct must lower to a
  free-function family (`Sys_method(instance, args)`); nothing call-shaped can
  pass through natively. C is therefore the backend where *every* call-lowering
  path runs — and the one where skipping a portable form (R1) hides the most.
- **No type erasure.** `@@:params.x` / `@@:data.x` are `void*`; float/double
  args need the RFC-0048 `_Generic` value-dispatch; ints round-trip via
  `(void*)(intptr_t)`. Fixtures must exercise the marshalling casts explicitly.
- **Declarator syntax.** Types wrap the name (`Child* kids[4];`), so array
  domain fields need framec's declarator emission (#159); the type as written in
  Frame (`kids: Child*[4]`) is not the type as emitted.
- **Type-opacity is sharpest here.** Native `typedef`s are the C idiom for
  compound types, and framec cannot see through them; the supported spellings
  must keep the system name visible.
- **Manual lifecycle.** framec emits `_new`/`_create` but no `_destroy` for
  cross-system pointers; fixtures own cleanup (or accept the leak in a
  short-lived TAP binary and say so).
- **Persist = libcjson**, `char*` blob; the C runner links `-lcjson`.

**Specific examples**

- **The #159 family (all three waves), the origin lesson of this document:**
  `@@:self.kids[i].tick(dt)` must lower to `Child_tick(self->kids[i], dt)` —
  including when `tick` is on the caller and on multiple children. Requires the
  visible array spelling `kids: Child*[4]`; a `typedef Child* Kids[4]` hides the
  element type and (with shared method names) cannot resolve — documented in
  `docs/per_language_guides/c.md` § "Arrays of embedded systems".
- **The hand-lowering trap:** `Sensor_bump(self->sensor);` under a
  `[composition]` tag exercised nothing in framec. Portable form + a separate
  `[control:]` native call is the corrected pattern (R1).
- **Statement terminators:** native C statements need `;`; Frame statements
  (`-> $S`, `push$`, `@@:(e)`, `=> $^`) must not get one — the forward
  closed-rule termination (framec#116/#117) is exercised by mixing both in one
  handler.
- **Brace-init domain fields** are `memcpy`d (stage-2 fix); enter-args with
  doubles heap-box via `pack_double` (RFC-0046/#81).
- **Async is EXCLUDED — and now hard-fails:** `@@[async]` on C is **E722**
  (framec#111 R4), not a warning. The fixture must not contain async members.
- **`@@:system.state` is reserved** (E608) — the accessor is
  `@@:system.state.name`.

---

### Go — `max_go.fgo`

**General challenges**

- **Export case-mapping.** framec capitalizes generated interface methods
  (`tick` → `Tick`); every portable call must case-map, and a missed mapping is
  a compile error only if the fixture actually contains that call shape (#159
  reopen reproduced here identically).
- **Child-field spelling is load-bearing:** the bare system type
  (`pen: GhostPen = @@GhostPen()`) is the documented convention; `*GhostPen`
  historically opted out of case-mapping (hardened in #159, but the bare form
  remains canonical). Slices spell leading (`kids: []*Child`), which framec's
  resolution now strips.
- **Prolog is structural:** `package main` + imports must be present and
  minimal (unused imports are compile errors — fixtures pin `var _ = json.Marshal`
  style suppressions when persist pulls imports conditionally).

**Specific examples**

- Cross-product block with `kids: []*Child1` (leading-group spelling) — both
  reopen shapes case-map (`.Tick(dt)`).
- Persist round-trip with `string` blob; multi-binary build batching is a
  runner concern, not a fixture concern.

---

### Erlang — `max_erlang.ferl` *(target DEPRECATED as of framec 4.6.1 — W901)*

**General challenges**

- **One system per file (E406)** — the multi-system parts of the contract
  (including the cross-product block) are structurally impossible in one
  `.ferl`; multi-file fixtures live under `tests/erlang/multi/`, and the
  single-file fixture documents the exclusion (R6).
- **No mutation, no C-brace control flow.** The corpus historically wrote
  non-native handler bodies that framec's Erlang backend *translated* — the
  practice under redesign (framec#119/#125; fixture rewrite tracked as
  test-env#25). Until the design fork lands, this fixture is frozen: it pins
  current behavior, and new contract items are **not** back-ported to it.
- **Sidecar driver convention:** assertions live in `<name>.driver.escript`;
  without one, the generic export-walking smoke driver runs.
- Reserved words as state names need quoting; domain fields lowercase.

**Specific examples**

- The mixed-terminal `else if` + trailing statements shape emits invalid Erlang
  (framec#125) — deliberately absent here; the in-tree
  `erlang_control_flow_matrix.rs` net carries it as the known-red case.
- `@@[persist]` uses the bare + `@@[save]`/`@@[load]` form (ETF/binary), not a
  typed blob.

---

### Lua — `max_lua.flua`

**General challenges**

- **Colon-call discipline:** system method calls need `:` (implicit self);
  a `.` call silently shifts arguments (framec#120/#134 class). Portable forms
  must be asserted to emit `:`.
- **`--` comments only** — a `//` anywhere in generated or fixture code is a
  syntax error (this class shipped twice: framec#124's `end else if`, and the
  async-init placeholder fixed in #158's sweep).
- **Table literals vs Frame braces:** `{...}` constructors inside handler
  control flow must survive the block lowering (framec#122).

**Specific examples**

- `table.insert(t, {size = i, tags = {1, 2}})` inside a `while` in a handler —
  the #122 regression shape (`control_flow/table_literal_in_loop.flua` is the
  focused twin; the max fixture carries a representative).
- Cross-product block with a Lua table of children, colon-called.

---

### Kotlin — `max_kotlin.fkt`

**General challenges**

- **Multiplatform correctness:** no JVM-only annotations in generated code —
  `@JvmStatic` broke Kotlin/JS/Native/wasm (framec#157). The fixture compiles on
  the JVM in CI, so multiplatform regressions need the generated-code assertion
  (absence of `kotlin.jvm.*`), not just compilation.
- **Definite initialization:** deferred domain fields (initializer references a
  system param, RFC-0017) need `lateinit var` (framec#147).
- **Async = `suspend`** — calls are bare (no `await` keyword); the async
  surface asserts signatures, not call-site keywords.
- Jackson on the classpath for persist; `!!` at null-asserted derefs.

**Specific examples**

- Companion factory is `fun __create(...)` inside `companion object` —
  annotation-free (#157 regression pin).
- Cross-product block with `kids: MutableList<Child>`-style typed container.

---

### Swift — `max_swift.fswift`

**General challenges**

- **Definite initialization:** deferred reference-typed domain fields emit
  implicitly-unwrapped optionals (`Dep!`, framec#156); primitives keep
  zero-value placeholders.
- **`init` is reserved** — the async entry is renamed `initAsync` (RFC-0043).
- Type-erased returns need `as!` casts in native assertion code; `defer` is the
  scope-exit idiom (RFC-0049 exception policy).

**Specific examples**

- A parameterized system with a reference-typed deferred field (the #156
  shape) plus the cross-product block.

---

### Python — `max_python_3.fpy`

**General challenges**

- **The reference backend** — every construct is expected to work; its fixture
  is the semantic oracle others mirror.
- Runner history: `if __name__ == "__main__":` guards silently no-op'd under
  import-style execution (282 tests were no-ops once) — the runner exec's with
  `__name__='__main__'`; fixtures keep the guard.
- Persist is **JSON, not pickle** (since 4.2.0); `bytes` blob type.

**Specific examples**

- Async block: `async def` chain + `await system.init()` two-phase start
  (RFC-0043) — Python is the async reference too.

---

### JavaScript / TypeScript — `max_javascript.fjs` / `max_typescript.fts`

**General challenges**

- **ESM output** (`export class`) — drivers run as `.mjs`/via tsx; a bare
  `node file.js` fails on `export`.
- TS strict mode: `null` vs `any[]` in FrameEvent params (D-TS-1); casts
  (`as number`) in assertions.
- These are the **shipped-baseline** languages for the games ports — their max
  fixtures double as the behavioral oracle for other targets' ports.

**Specific examples**

- Save/restore are camelCase (`saveState`/`restoreState`) by attr convention.
- Unindexed container calls (`this.items.push(c)`) must stay native — the #159
  guard case lives here (a system named method `push` must not capture it).

---

### Java — `max_java.fjava`

**General challenges**

- **One public class per file (E430):** exactly one `@@system` is public; every
  sibling is `@@system private` (package-private) — the max fixture is the
  canonical demonstration (7 systems).
- **Async is structurally different:** `CompletableFuture<T>` boundary, sync
  internals, no-op `init()` — assertions target the future's value, not
  awaited-keyword shapes.
- Jackson for persist; boxed-cast idioms (`(int) obj`) in assertions.

---

### C# — `max_csharp.fcs`

**General challenges**

- PascalCase save/load attr names (`SaveState`/`RestoreState`) by convention;
  `System.Text.Json` persist.
- First-`dotnet`-run warmup is a runner concern (cold restore hangs) — fixtures
  stay single-project.

---

### C++ — `max_cpp.fcpp`

**General challenges**

- **Exception policy (RFC-0049):** core dispatch is exception-free (RAII scope
  guards) and must compile `-fno-exceptions`; persist/async opt in via
  `#if defined(__cpp_exceptions)` fallbacks. The fixture should compile under
  both regimes where practical.
- Type-erased returns are `std::any` — assertions cast
  (`std::any_cast<int>(...)`); embedded systems are `shared_ptr` (deref `->`).
- Async is coroutines: `co_await`/`co_return`; handler bodies lacking a
  coroutine keyword get a synthesized `co_return;`.
- Persist needs `#include <nlohmann/json.hpp>` (framec#94).

---

### Dart — `max_dart.fdart`

**General challenges**

- `dart:convert` required for persist, `dart:io` for `exit()` — prolog imports
  are the fixture's job.
- Null-safety asserts (`!`) at parent-forward derefs.

---

### GDScript — `max_gdscript.fgd`

**General challenges**

- Host shape: `extends SceneTree` + `func _init():` + `quit()` — the driver IS
  the scene; forgetting `quit()` hangs the runner.
- No exceptions: E703/async surfaces via `push_error` + typed-zero returns;
  `assert()` for TAP-ish checks.
- Godot startup (~500ms) makes per-fixture cost real — batching is a runner
  concern, but fixtures stay single-file.

---

### Ruby — `max_ruby.frb`

**General challenges**

- `require 'json'` in the prolog for persist (its absence is a runtime
  `NameError`, not a compile error — only caught by running, R5).
- `#` comments only (same class as Lua's `--`); `attr_accessor` makes
  `self.field =` work as both l/rvalue.

---

### PHP — `max_php.fphp`

**General challenges**

- Native handler code is real PHP: `$this->field`, `$param` — the `$`-sigil is
  the most common porting error from other fixtures.
- Prolog text lands inside `<?php` — `//` comments fine; `echo`/`exit(1)`
  driver convention.

---

### Rust — `max_rust.frs`

**General challenges**

- Real Rust types in Frame declarations (`i32`, `String`, `Vec<T>`) — no alias
  tables exist by design; String returns need `.clone()`/`.to_string()` in
  handlers (RFC-0033 arg-expr contract handles dispatch-site borrows).
- Postfix `.await`; typed event enums (RFC-0025 Track B) mean match-shaped
  dispatch — fixture asserts against the typed surface.
- serde/serde_json for persist; the runner provides the workspace.
- `@@[*persist]` broadcast: max_rust is currently the ONLY runtime exercise of
  the module-position broadcast trio — keep it (the dedicated
  `capabilities/broadcast_persist.*` stem covers the other backends).

---

## Amendment log

- **2026-07-03** — Document created from the framec#159 post-mortem (three
  waves through max_c: hand-lowered composition tag + missing
  indexed/collision cross-products). C section written as the exemplar;
  cross-product block (Part 3) added to the contract; per-language sections
  seeded from the shipped-bug record, to be deepened language by language.
