# Divergence Journal — framec-ng vs legacy framec 4.6.0.x (latest local build)

**The faithfulness invariant:** framec-ng emits **byte-identical to legacy**, EXCEPT for the deltas
journaled below. Every delta between ng and legacy MUST have an entry here; an **unjournaled delta
is a defect** (either ng is silently wrong, or an intentional change was never recorded — both
forbidden). The faithfulness warden gates on this (F1/F1b): a fixture passes iff it is byte-identical
or every delta matches a journal entry that carries a passing runtime validator.

**Owner ruling (2026-07-24):** legacy's *bugs* are FIXED in ng, not reproduced. Each fix is a
journaled delta with a runtime validator (a test that BUILDS AND RUNS the emitted program and
asserts the correct behavior — it would FAIL on legacy and PASSES on ng). Everything not journaled
is held to strict byte-identity.

Each entry records: **construct** (the delta's signature) · **legacy** emits · **ng** emits ·
**why legacy is wrong** · **validator** (`compiler/tests/legacy_bug_fixes.rs`) · **affected**
(which fixtures/targets show it). `intentional_divergences.txt` is the machine-readable fixture list
derived from the "affected" lines here (what `faithfulness_diff.sh` excludes from the denominator).

---

## D1 — `push$` transition drops state args (all targets)
- **construct:** `push$ -> $Paid("cola, diet", 5)`
- **legacy:** `__prepareEnter("Paid", [], [])` — args dropped; the destination then reads
  `state_args[0]` → **`IndexError` at runtime**. (Non-push `-> $Paid(...)` passes them correctly.)
- **ng:** delivers the args into the pushed compartment.
- **why wrong:** args are in the source, the destination declares params, the program crashes.
- **validator:** `push_transition_delivers_state_args`.
- **affected:** fixtures using `push$ -> $S(args)` (pushpop + state-args).

## D2 — constructor cannot construct (all targets)
- **construct:** a system with domain fields and/or system params.
- **legacy:** `def __init__(self)` takes no header params (params bind only in `_create`); domain
  seeding lives in `_create`. `Sys(args)` → **`TypeError`**; `Sys()` → domain fields unassigned.
- **ng:** `__init__(self, <params>)` seeds domain + builds the start compartment; `_create` calls it.
- **why wrong:** a class whose own constructor cannot construct a usable instance is broken.
- **validator:** `plain_constructor_builds_a_usable_system`.
- **affected:** ~most systems with domain/params — **structural** delta (`__init__`/`_create`
  signatures differ). This is the pervasive one surfaced by the structural-skeleton check.

## D3 — state-vars only seed via `_create` (all targets)
- **construct:** a state with `$.var` initializers.
- **legacy:** initializers go into a synthesized `$>` handler guarded by `if "n" not in
  compartment.state_vars:`, which only runs via `_create`. `SV().peek()` → **`KeyError`**.
- **ng:** seeds where the compartment is built; `SV().peek()` works.
- **why wrong:** object validity must not depend on which constructor the caller used.
- **validator:** `state_vars_are_seeded_for_a_plain_constructor`.
- **affected:** fixtures with state-var initializers — **structural** (legacy emits an extra
  `_s_<S>_hdl_frame_enter`; ng does not).

## D4 — multi-line `@@:( … )` inside an action (Python; deferred elsewhere)
- **construct:** an action whose `@@:(expr)` spans lines.
- **legacy:** `return a\n    + b` — an `IndentationError`; the module does not import.
- **ng:** supplies the implicit-continuation parens the `@@:()` syntax already implies.
- **why wrong:** the emitted module is not valid Python.
- **validator:** (recorded at the emit site; **0** corpus fixtures exercise it — journaled so it can
  never be a silent surprise).
- **affected:** none currently.

## D5 — Rust `var` local declaration (Rust; deferred until a fixture needs it)
- **construct:** a local `var x = …` in a handler body (Rust target).
- **legacy:** leaks `var x = self.g();` verbatim (and `var y: i32 = 7` even drops the `;`) — invalid
  Rust; untested/unsupported in the legacy Rust backend.
- **ng:** emits correct `let` / `let mut`.
- **why wrong:** the emitted Rust does not compile.
- **validator:** (to add when a Rust fixture exercises a local decl).
- **affected:** none currently (M1 Rust fixtures avoid `var`).

---

## Pending owner ruling (NOT yet journaled — do not treat as intentional until decided)
- **D2/D3 as the *intended* structural bar.** Keeping D2/D3 means ~40+ fixtures are permanently
  "correct-divergent" (byte-identity impossible; the bar becomes "byte-identical OR journaled").
  Confirm vs. reverting ng to legacy's `_create`-only structure. (Leaning: keep — it is the
  fix-legacy-bugs ruling applied to structure.)
- **Action trailing whitespace** (faithfulness vs. quality) — reproducing legacy means emitting
  trailing spaces. Not yet decided; NOT a journaled divergence until ruled.

## Category: CODE-QUALITY divergence (ng-cleaner; run-result IDENTICAL) — owner ruling 2026-07-25
A distinct journal kind: ng emits **cleaner** code than legacy while the emitted programs **run
identically**. No bug, so no fails-on-legacy validator — the validator is the differential RESULT
gate proving identical behavior (`code=journaled result=identical`).
- **Q1 — action-body trailing whitespace:** legacy's action-body span runs to the byte before `}`, so
  `h() { pass }` emits `        pass ` (trailing space); **ng trims** it. Owner ruled KEEP ng clean.
  Affected: the ~16 action-body fixtures (`linux/*`, `capabilities/*`) whose ng-vs-legacy delta is
  trailing-whitespace-only. To be enumerated + added to intentional_divergences.txt when M8 lands.

---

## D2-rust — parameterized `Sys::new(param)` cannot construct in legacy (Rust) — added 2026-07-26
Rust spelling of D2. Verified vs the LOCAL 4.6.0.33 oracle (`-l rust`) by emitting with both, `cmp`,
and building + running the emitted Rust (gated by workflow, 6/6 lenses PASS).
- **construct:** a system WITH constructor params (domain/state/enter), e.g. `@@system Cell(seed: i64)`.
- **legacy:** emits NO `pub fn new(<params>)`; inlines the struct literal straight into
  `pub fn __create(<params>) -> Self { let mut c = Self { …seed…, __compartment: Comp::new("S") }; …lifecycle… c }`.
  So `Cell::new(5)` is a compile error and the ONLY way to obtain a `Cell` is the lifecycle-running factory.
- **ng:** `pub fn new(seed) -> Self { Self { …seeded…, __compartment: Comp::new("S"), __next_compartment: None } }`
  + `pub fn __create(seed) { let mut c = Self::new(seed); …lifecycle… c }` — the plain ctor builds a
  usable instance; the factory still runs the enter lifecycle.
- **why legacy is wrong:** a type whose plain constructor cannot build a usable value (only a
  lifecycle-running factory can) is broken by construction — cannot be built without a live kernel,
  cannot be composed as another system's domain field via `new`. Same defect as Python D2.
- **scope:** PARAMETERIZED-only. A PARAMLESS Rust system is byte-identical (legacy already emits
  `new()` + a delegating `__create()`). Only parameterized systems are allowlisted.
- **validator:** `compiler/tests/rust_acceptance.rs::plain_constructor_builds_a_usable_system_rust`
  (builds `Ctor::new(7)` directly — absent in legacy — seeds+reads the domain; then the factory path).
  Fails on legacy (no `new(i64)` → rustc error), passes on ng.
- **emit site:** `compiler/src/text/emit/rust.rs` `emit_kernel_open` (`pub fn new(<plist>)` always
  emitted + `__create` delegating via `Self::new(<ctor_args>)`).
- **affected:** `construction/m2_construction.frs` (anchor) — entire delta is two D2 relocations
  (`Inner(start)`, `Cell(seed)`); both programs compile and print identical TAP (`ok 1..3`).

## D3-rust — state-var seeding is NOT a Rust divergence (recorded to prevent mis-listing) — 2026-07-26
The shared D3 entry is dynamic-target-shaped (Python: a guarded synthesized `$>` handler that only
runs via `_create`). It does NOT apply to Rust.
- **legacy (`-l rust`):** `$.x = V` is seeded structurally in the state's typed-context `Default` impl
  (`impl Default for <S>Context { fn default() { Self { x: V } } }`), built through
  `<S>Compartment::new(..)`, which runs in BOTH `new()` and `__create()`. So legacy Rust already seeds
  `$.x` for a plain-constructed instance.
- **ng:** identical — `m2_construction.frs`'s `$.count: i64 = 100` shows zero delta.
- **conclusion:** do NOT add any Rust fixture under a D3 allowlist; Rust state-var seeding is byte-faithful.

## (leaf FIX, NOT a divergence) `@@Inner()` domain sub-system → `Inner::__create(..)` — 2026-07-26
Recorded to explain a Rust-leaf change; NOT an allowlist entry (it moves ng TOWARD the oracle).
- **before:** `domain_field_init` lowered `inner: Inner = @@Inner(7)` to `Inner::new(7)`, skipping the
  sub-system's start `$>` lifecycle.
- **legacy + fixed ng:** `Inner::__create(7)` — FRAME instantiation is the two-phase factory (runs
  `$>`), the same lowering `@@Inner(7)` gets in native water; byte-identical to legacy.
- **emit site:** `compiler/src/text/emit/rust.rs` `domain_field_init`. The scanner path
  (`open_scanner`) deliberately keeps `new` (a scanner constructs WITHOUT running; RFC-0042 `over()`),
  a separate site, unaffected.
- This is the **Rust half of the M2 grid gap** "system-typed domain field not lowered through `_create`".

## D-RUST-1 — nested persist: the parent embedded the child's STRUCT (rust)
- **construct:** a `@@[persist]` system with a domain field typed as another `@@system`
  (`child: Inner = @@Inner()`).
- **legacy:** composes — the parent stores the child's OWN snapshot and delegates
  (`serde_json::from_str(&self.child.save_state())`; restore = `Inner::new()` +
  `child.restore_state(...)`).
- **ng (before):** put `child: Inner` in a serde-derived `__Snap` and wrote `self.child.clone()`.
- **why that was wrong:** a system struct derives no serde (it holds compartments, context stacks,
  `Rc`s), so this demanded `Serialize`/`Deserialize`/`Clone` it does not have — the emitted program
  **did not compile** (E0277/E0599) on every nested-persist fixture.
- **ng (now):** composition, per the owner ruling and `frame_language.md` "Composed systems" —
  Frame has no embedded-machine concept, so the parent stores the child's blob and rebuilds it
  through its own constructor + load. Recurses to any depth (proven on an L1→L5 chain).
- **byte status:** ng keeps its `__Snap` design rather than legacy's `serde_json::Value` assembly,
  so the two differ in spelling while agreeing in SEMANTICS. Journaled as a deliberate divergence.
- **validator:** `composed_child_persists_through_its_own_api` (BUILDS AND RUNS: mutates parent and
  child, snapshots, mutates again, restores, and requires both to come back).
- **affected:** `primary/{25,71,82,83,84}_persist*` (rust).

## D-RUST-2 — a bare `@@:self.<event>()` statement lost the transition guard (rust)
- **construct:** `@@:self.go()` as a whole statement, where `go()` transitions, followed by more
  statements.
- **legacy:** emits the reentrancy guard after the call
  (`if ... ctx._transitioned { return; }`), so the trailing statements do not run.
- **ng (before):** emitted the guard only for the EXPRESSION-position twin (`x = @@:self.g()`), so
  the statements after a bare call ran **in the wrong state**. It compiled and ran — a byte-diff
  and a compile check both called it green.
- **ng (now):** the guard fires on the `Stmt::SelfCall` path too, with the same two exclusions
  (kernel model only; not an `actions:` call).
- **byte status:** ng now MATCHES legacy here — this is a fixed ng bug, not a standing divergence;
  recorded so the validator has a home.
- **validator:** `bare_self_call_statement_gets_the_transition_guard` (BUILDS AND RUNS; asserts the
  post-call statement did not execute).
- **affected:** `primary/{39,52,53,72}` (rust).

## D-RUST-3 — legacy REWRITES native text to insert `.clone()`; ng passes it through (rust)
- **construct:** a bare native call whose argument is a bare native field —
  `self.do_resolve(self.name)` in a handler body, where `name: String` is a domain field.
- **legacy:** `apply_rust_auto_clone` (`framec/src/frame_c/compiler/codegen/rust_system.rs:1986`)
  walks every `NativeBlock`, pattern-matches `self.<m>(<args>)` in the emitted text, and rewrites
  any argument spelled exactly `self.<field>` to `self.<field>.clone()`.
- **ng:** emits the user's bytes unchanged.
- **why ng is right, and this is not a spelling choice:** `frame_language.md` — "A bare native
  `self.` is passthrough"; Frame recognizes exactly 7 constructs in a handler body and this is none
  of them. RFC-0046 §"Everything under `@@:self.` is framec's to lower … Anything **not** under
  `@@:` is native code and passes through untouched", and that RFC **deleted three backends'
  bare-`self.` rewrites** for this exact reason, noting they were "inconsistent … with the matrix
  green throughout because every fixture sidesteps the issue". This is the same rewrite, re-added
  on a fourth backend two RFCs later. `frame_language.md` even refuses to fix a native self-call's
  *punctuation* (`.` vs Lua's `:`) — a compiler that may not change a `.` may not append `.clone()`.
- **four defects it causes, each compile-proved:**
  1. **whitespace/paren sensitive** — `self.do_it(self.name)` and `self.do_it((self.name))` are the
     same Rust expression; the first is rewritten, the second is not and fails E0505/E0507. Same for
     `self . name`.
  2. **authors an error on non-`Clone` types** — a field whose type derives nothing gets
     `.clone()` appended and fails E0599, with `.clone()` in the message the user never wrote.
  3. **hardcoded 20-name Copy list** (`rust_type_is_copy`) — any Copy type spelled outside it
     (`(i32,i32)`, `[u8;4]`, an alias) gets a spurious clone.
  4. **corrupts UTF-8** — the rewriter's `out.push(bytes[i] as char)` is a Latin-1 widening, so a
     handler body containing a non-ASCII identifier is double-encoded:
     `let café = 1;` becomes `let cafÃ© = 1;` and rustc reports `unknown start of token: \u{83}`.
     A silent miscompile in shipped 4.6.0.33 for any such body in a system with a non-Copy domain
     field. **ng's output is byte-exact.**
- **resolution:** FIXTURE correction, not an ng change. The nine sites were a mechanical port of the
  `.fpy` siblings (byte-identical handler bodies — correct Python, invalid Rust): the types were
  ported, the native code was not. The user now writes `.clone()`, which is what the target language
  requires and what Frame's own docs tell them to do (`frame_language.md`: "Write what the target
  compiler expects").
- **byte status:** with the corrected fixtures BOTH compilers emit compiling, passing programs, so
  this costs nothing on either side and is not a standing byte divergence.
- **validator:** `golden_run rust linux/04_usb_enumeration.frs linux/08_kernel_module_loader.frs`
  (BUILDS AND RUNS; the fixtures' own assertions: "refcount blocks unload", "reload from failed").
- **affected:** `linux/08_kernel_module_loader.frs` (8 sites, `name: String`),
  `linux/04_usb_enumeration.frs` (1 site, line 85, `product: String`; its other 6 field arguments
  are `i32` and were always correct). `linux/06_oom_killer.frs` has one such call on an `i32` field
  — correct as written, untouched.
- **follow-up for the legacy tree:** `apply_rust_auto_clone` can be deleted once the fixtures land.
