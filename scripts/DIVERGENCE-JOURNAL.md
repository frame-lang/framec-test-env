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
