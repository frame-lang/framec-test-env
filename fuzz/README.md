# Frame codegen fuzzer

Structural fuzzer for framec. Generates small Frame systems varying
structural combinations — HSM depth, push$/pop$, state variables,
enter/exit handlers, enter args, action control flow, handler control
flow, return type — then transpiles and syntax-checks each across every
target backend. Failures surface codegen bugs the hand-written test
matrix doesn't exercise.

## Top-level meta-runner (`run_all.sh`)

Iterates all configured phases (2-10) with a shared
`--tier=smoke|core|full`, `--tag=<comma-list>`, `--lang=<name>` flag
contract. See `TEST_INFRA_ROADMAP.md` for the contract design and
`TAG_VOCABULARY.md` for available tags.

```bash
./run_all.sh --tier=smoke                  # cross-phase smoke
./run_all.sh --tier=full --lang=python_3   # one-lang full
./run_all.sh --tier=smoke --phases=9,10    # subset
./run_all.sh --tag=hsm                     # cross-section
```

Phases 2-7 use `diff_harness/run_fuzz.py` (case + .meta files).
Phases 8/9/10 use shell runners. The meta-runner delegates with
flag passthrough.

## Usage

```bash
# Generate 500 cases per language (defaults) and run every target
python3 gen.py --max 500
./run.sh

# Single language
./run.sh rust

# Transpile only (fast — skips the target-compiler phase)
TRANSPILE_ONLY=1 ./run.sh

# Single language, small batch
python3 gen.py --max 50 --lang frs
./run.sh rust
```

Results land in `logs/summary.tsv` (one row per case per stage).

## What it covers

Each generated case varies the following independently:

| Axis | Values |
|---|---|
| state count | 2, 3, 5, 8 |
| HSM depth | flat / 2-level / 3-level / 4-level |
| push$/pop$ | on/off |
| state variables | on/off |
| enter/exit handlers | on/off |
| enter args | on/off |
| action body | none / assign / if / nested if |
| handler body | simple / conditional / nested if / forward (`=> $^`) |
| return type | void / str / int |

With 4 × 4 × 2 × 2 × 2 × 2 × 4 × 4 × 3 = 12,288 configurations in the
full cross-product, `--max` samples a random subset for tractability.
Default seed (42) keeps runs reproducible.

## What it does NOT cover (yet)

These Frame features are not exercised by the fuzzer; extending it to
include them is a known follow-up:

- `@@persist` (needs a runtime round-trip, not just a compile check)
- `async` (same — runtime semantics)
- `@@:self` reentrant interface calls
- Multi-system interactions
- `operations:` blocks with return types
- `Any`/`Vec<T>`/`HashMap<K,V>`/user-defined types
- `@@:params` / `@@:event` / `@@:data` magic references

## How it stays language-valid

Each LangSpec in `gen.py` configures per-target syntax:
- `self.x` vs `this.x` vs `s.x` vs `$this->x` vs `@x` vs `self->x`
- `if X:` vs `if X {` vs `if (X) {` vs `if X then`
- statement terminators (`;` in C family, nothing in Kotlin/Swift/Go)
- string literal syntax (plain quotes vs `.to_string()` for Rust vs
  `std::string("...")` for C++)
- optional language prolog (Go needs `package main`)

Generated Frame source is verified valid per target **before** blaming
framec for a failure. If a new failure class emerges, first check
whether the generator is producing invalid source for that language.

## How to add a language

1. Add a `LangSpec` entry to `LANGS` in `gen.py` with the target's
   syntax conventions.
2. Add a `compile_check` arm in `run.sh` that runs the target's
   parser/type-checker (not a full build — we want fast feedback).
3. Run a small batch (`python3 gen.py --max 10 --lang <ext> && ./run.sh <target>`)
   and fix any generator issues surfaced by `logs/<target>-case_*.err`.

## Why transpile + syntax-check, not run

The fuzzer tests **codegen correctness** — does framec emit valid
target-language source? A full build-and-run would add 10-100× wall
time for marginal additional signal: if the output parses and
type-checks, the codegen is structurally sound. The existing Docker
matrix (`docker/make test`) handles runtime validation on hand-written
fixtures; this fuzzer is its structural complement.

---

## Phase 9: nested-frame fuzz (curated regressions, runtime-asserted)

`gen_nested.py` + `run_nested.sh` — 5 named patterns × 17 backends
that pin axes the depth-2 cross-product (Phase 10) doesn't reach,
plus runtime-verified regressions for cross-backend codegen fixes:

- p7: depth-2 nesting (`@@:self.a(@@:self.b(x))`)
- p8: depth-3 nesting
- p9: `@@:return = expr`, `@@:self.X()`, then `-> $State` — the
  return-slot value must survive the transition to be reported back.
- p11: cross-handler `$.field` round-trip — write in handler A, read in
  handler B.
- p14: `self.n = @@:self.foo() + 1` — domain-LHS embedded self-call.
  Pins the D1 fix (2026-04-28) that defers the transition guard
  until end-of-statement.

These are runtime-asserted (each generated case asserts a specific
final domain value), unlike Phase 10's transpile-only structural
fuzz. ~30s wall clock across all 17 langs.

```bash
python3 gen_nested.py
./run_nested.sh
```

## Phase 10: full-permutation expression fuzz (tiered)

`gen_perm.py` + `run_perm.sh` — single-statement, depth ≤ 2
cross-product of `LHS × receiver × operator × receiver`. Each case
is value-asserted (generator simulates Frame execution to compute the
expected return). 462 cases × 17 langs = 7,854 case-runs at full tier.

Dimensions:
- LHS targets (3): `@@:return =`, `self.<dom> =`, `$.<sv> =`
- Receivers (7): two integer literals, domain field read, state-var
  read, parameter read, two self-call shapes (`@@:self.compute()` and
  `@@:self.add_one(2)`)
- Operators (3): `+`, `-`, `*`

```bash
python3 gen_perm.py                          # generate all 17 langs
./run_perm.sh --tier=smoke                   # ~90 cases/lang, ~30s matrix
./run_perm.sh --tier=core                    # delegates to run_nested.sh
./run_perm.sh --tier=full                    # 462 cases/lang, 20-30 min
./run_perm.sh --tier=full --lang=python_3    # one lang only
```

### Tier model

| Tier | Source | Cases / lang | Wall clock | When to run |
|---|---|---|---|---|
| smoke | gen_perm.py, one per coarse equiv class | ~30-90 | ~30s matrix | Every iteration |
| core | gen_nested.py (Phase 9 patterns p7+p8+p9+p11) | 4 | ~20s matrix | Before commit |
| full | gen_perm.py, all combos | 462 | 20-30 min matrix | Nightly / pre-release |
| stress | smoke + core + full + Phase 6/7/8 | All | 1hr+ | Pre-release |

### Output

- `cases_perm/_index.tsv` — sidecar (lang, case_id, equiv_class, smoke,
  expected). Smoke filter reads this; non-Erlang langs don't carry
  metadata in-source because `# FUZZ_*` would land in JS/Java output
  where `#` isn't a comment.
- `logs_perm/per_lang/summary_<lang>.tsv` — per-lang results so
  concurrent `--lang=X` / `--lang=Y` invocations don't clobber.
- `logs_perm/summary.tsv` — rebuilt at end-of-run from per-lang files.

---

## Phase 11: statement-pair sequencing fuzz (wave 1)

`gen_stmt_pair.py` + `run_stmt_pair.sh` — two-statement handler
bodies. Each case is `S1; S2;` where the simulator computes the
post-state and the driver asserts the result.

What this exercises that earlier phases don't:
- Read-after-write within a single handler (does S2 see S1's
  domain/sv/return-slot write?).
- Last-write-wins on the same slot.
- Self-call result flowing through a domain field into the next
  statement (`self.f = @@:self.compute()` → `@@:return = self.f + L`).
- @@:return survival when subsequent statements modify
  domain/state-var.

Axes:
- S1 (5): `dom_w`, `sv_w`, `ret_w`, `sc_bare`, `sc_assign_dom`
- S2 (5): `dom_to_ret`, `sv_to_ret`, `dom_plus_lit`, `sv_plus_lit`,
  `dom_w_lit`
- LIT (4): 1, 5, -3, 0
- Total: 5 × 5 × 4 = 100 cases per lang × 17 langs = 1,700.

Smoke selects one case per (S1, S2) pair (LIT=1) → 25 smoke
cases per lang.

```bash
python3 gen_stmt_pair.py                          # generate all 17 langs
./run_stmt_pair.sh --tier=smoke                   # ~40s parallel
./run_stmt_pair.sh --tier=full                    # ~8 min
./run_stmt_pair.sh --tier=full --lang=python_3    # one lang only
```

Wave 1 result (2026-04-28): 1,700 / 1,700 passing across all 17
backends. No new defects surfaced — the statement-pair semantics
hold across every backend, including the cases that previously
exercised the D1 cross-backend fix (`sc_assign_dom` × any S2 that
reads `self.f`). Per the wave methodology, this signals that
Phase 11's first wave landed in a healthy state; next-wave work
either expands Phase 11 axes (transitions, more S1/S2 shapes) or
moves to a different phase based on bug-finding density.

---

## Phase 12: control-flow embedding fuzz (wave 1)

`gen_ctrl_flow.py` + `run_ctrl_flow.sh` — Frame statements
embedded inside native `if cond { body }`. Tests that framec
correctly emits transitions, self-calls, return-writes, and
domain/state-var writes when nested inside per-target native
control flow.

What this exercises that earlier phases don't:
- Frame statements inside native if-bodies.
- Per-language if-syntax variation: indent (Python/GDScript),
  braces with parens (JS/TS/Java/C/C++/C#/PHP/Kotlin/Dart),
  braces without parens (Rust/Go/Swift), end-keyword (Ruby/Lua).
- Cond expressions reading domain fields.

Axes:
- Cond (4): `lit_true`, `lit_false`, `dom_eq_hit`, `dom_arith_eq_hit`
- Body (5): `dom_w`, `sv_w`, `ret_w`, `sc_assign_dom`, `transition`
- LIT (5): 1, 5, -3, 0, 100
- Total: 4 × 5 × 5 = 100 cases per lang × 16 langs = 1,600.

Erlang excluded for wave 1 — `if X -> body ; true -> body end` is
too structurally different from the other 16 langs to share a
renderer. Wave 2 candidate.

Smoke selects one case per (cond, body) pair (LIT=1) → 20 smoke
cases per lang.

```bash
python3 gen_ctrl_flow.py                          # generate 16 langs
./run_ctrl_flow.sh --tier=smoke                   # ~32s parallel
./run_ctrl_flow.sh --tier=full                    # ~7 min serial
./run_ctrl_flow.sh --tier=full --lang=python_3    # one lang only
```

Wave 1 result (2026-04-28): 1,600 / 1,600 passing across all 16
backends. Two generator bugs surfaced and fixed during bring-up:
- Kotlin requires parens around the cond (was rendering as Rust-
  style); fixed in `IF_RENDERERS["kotlin"]`.
- State vars are state-scoped — $S1 (transition target) reading
  `$.s` declared in $S0 emits invalid Rust enum-variant access.
  Generator now emits only `get_n` (domain read) in $S1 for
  transition cases. This pins a real Frame contract: state-vars
  do not propagate across transitions; only domain fields do.

---

## Phase 13: identifier shadowing fuzz (wave 1)

`gen_shadow.py` + `run_shadow.sh` — same identifier `x` declared
in three scopes (domain field, state-var, handler param) at once.
Tests framec's scope resolution.

What this exercises:
- `self.x` always resolves to the domain field.
- `$.x` always resolves to the state-var.
- Unqualified `x` (inside a handler that takes `x` as a param)
  resolves to the param.
- `@@:params.x` resolves to the param via the params object.
- Cross-slot reads in one expression compose correctly:
  `self.x + $.x + x` returns the sum of all three.

Axes:
- 10 read shapes: `self_only`, `sv_only`, `param_only`,
  `params_obj_only`, `self+sv`, `self+param`, `sv+param`,
  `all_three`, `self+lit`, `self-sv+param`.
- 10 value tuples — `(dom_x, sv_x, param_x, lit)` per case, chosen
  to exercise sign/zero edges and minimize coincidental equality.
- Total: 10 × 10 = 100 cases per lang × 17 langs = 1,700.

Smoke selects one case per shape (first value tuple) → 10 smoke
cases per lang.

```bash
python3 gen_shadow.py                          # generate 17 langs
./run_shadow.sh --tier=smoke                   # ~25s parallel
./run_shadow.sh --tier=full                    # ~7:44 serial
./run_shadow.sh --tier=full --lang=python_3    # one lang only
```

Wave 1 result (2026-04-28): 1,700 / 1,700 passing across all 17
backends. Zero defects. Frame's qualified syntax (`self.`, `$.`)
makes scope resolution unambiguous, so this wave largely confirms
that the qualification contract holds; bugs would more likely
surface in write paths or native local shadowing (wave 2 axes).

---

## Phase 14: HSM × everything fuzz (wave 1)

`gen_hsm_cross.py` + `run_hsm_cross.sh` — depth-2 HSM (parent +
child) and one depth-3 pattern, with handler bodies that exercise
`=> $^` forwarding, `@@:self.X()` interface dispatch, and
domain/return-slot writes. Phase 4 covers HSM enter/exit cascades
narrowly; this phase tests the orthogonal axis: do Frame
statements compose correctly when the state has ancestors?

Patterns (8):
- `p1_child_dom_w` — child handles, writes domain.
- `p2_parent_dom_w` — child forwards (`=> $^`), parent writes
  domain.
- `p3_child_ret_w` — child sets `@@:return = lit`.
- `p4_parent_ret_w` — child forwards, parent sets `@@:return`.
- `p5_child_writes_then_fwd` — child writes domain then forwards;
  parent reads + arithmetic.
- `p8_child_overrides_compute` — parent declares `compute()`,
  child overrides; parent's body calls `@@:self.compute()` —
  dispatch must hit child's override.
- `p9_dom_arith_through_hsm` — domain arithmetic composes through
  the cascade (child-write + parent-read).
- `p10_three_level` — Grandparent / Parent / Child cascade.

Value tuples (10): `(LIT, dom_init)` exercising sign/zero edges.
Total: 8 × 10 = 80 cases per lang × 17 langs = 1,360.

Smoke selects one case per pattern (first value tuple) → 8 smoke
cases per lang.

```bash
python3 gen_hsm_cross.py                          # generate 17 langs
./run_hsm_cross.sh --tier=smoke                   # ~25s parallel
./run_hsm_cross.sh --tier=full                    # ~6 min serial
./run_hsm_cross.sh --tier=full --lang=python_3    # one lang only
```

Wave 1 result (2026-04-28): 1,360 / 1,360 passing across all 17
backends, **after fixing two real framec defects** (committed in
framepiler `5749f44`):

1. **Erlang `=> $^` forward dropped parent's reply value** —
   `frame_unwrap_forward__` was a 2-tuple, hardcoded `[{reply,
   From, ok}]` after the unwrap. Fix: 3-tuple including reply
   value extracted from parent's action list.

2. **Erlang post-dispatch transition guard hardcoded `undefined`
   in `_ ->` arm** — when `@@:self.X()` caused a transition, the
   alternative reply was wrong. Fix: scope-aware variable extraction
   from the matched arm's terminal tuple.

Generator-side: P6/P7 (no `=> $^` cascade in child + `@@:self.X()`)
were dropped as inherently per-language divergent — they expose
typed-lang 0 vs dynamic-lang None vs Java/C# NPE for unwritten
return slot, which can't be a uniform corpus test.

This wave produced the highest defect-density of the program so
far: 2 framec bugs from 100 patterns. Confirms the wave
methodology — feature-cross-product axes (HSM × dispatch × forward
× return-write) catch what isolated single-feature axes miss.

---

## Phase 15: State-arg propagation × everything fuzz (wave 1)

`gen_state_args.py` + `run_state_args.sh` — state-args declared on
states (`$S(x: int) { ... }`) and used at every site Frame allows:
literal arg, domain-field arg, arithmetic, self-call result, multi-
arg, chained transitions, HSM with parent vs child params, and
state-arg reads in non-enter handlers.

Patterns (10):
- `p1_lit_arg` — literal value in `-> $S1(5)`.
- `p2_dom_arg` — domain field as transition arg.
- `p3_arith_arg` — arithmetic expression as arg.
- `p4_selfcall_arg` — `@@:self.compute()` result as arg.
- `p5_multi_arg` — two-arg state, both threaded.
- `p6_chained_transition` — transition-then-transition with state-
  arg flowing through enter cascade.
- `p7_child_hsm_arg` — `$Child(x: int) => $Parent` (parent unit
  variant, leaf tuple variant) — verifies Rust StateContext enum
  doesn't write to a unit-variant ancestor.
- `p8_arg_in_event` — non-enter event handler reads the state-arg.
- `p9_three_lvl_uniform` (wave 2) — 3-level HSM, all three layers
  tuple variant; ancestor walk writes at every depth.
- `p10_three_lvl_mixed` (wave 2) — 3-level HSM, leaf + root tuple
  variant, mid unit; ancestor walk skips mid (E0532 guard) and
  writes to root.

Value tuples (10): mixed sign + magnitude.
Total: 10 × 10 = 100 cases per lang × 17 langs = 1,700.

All patterns are **verify-via-getter** — `drive()` triggers the
transition (void), then `get_x()` reads the state-arg. This sidesteps
per-backend transition-return-value semantics (especially Erlang
gen_statem's hardcoded `ok` reply on transitions).

```bash
python3 gen_state_args.py                          # generate 17 langs
./run_state_args.sh --tier=smoke                   # ~25s parallel
./run_state_args.sh --tier=full                    # ~6 min serial
./run_state_args.sh --tier=full --lang=erlang      # one lang only
```

Wave 2 result (2026-04-29): **1,700 / 1,700 passing across 17
backends** with zero new framec defects. The 3-level HSM patterns
(P9 + P10) confirmed the conditional ancestor walk works for both
uniform and mixed-shape chains.

Wave 1 result (2026-04-29): **1,360 / 1,360 passing across 17
backends**, after fixing four real framec defects (committed in
framepiler `2120a1c` + `cc4de80`):

1. **Erlang `$>` enter handler did not bind state-args** — the enter
   prelude looped only `state.enter_params`, missing the loop over
   `state.params` that maps positional `frame_state_args` slots to
   local variables. State-args declared on `$S(x: int)` were
   unresolved when the enter cascade fired.

2. **Erlang chained-transition emitter dropped state-args** —
   the state_timeout pattern for sequenced transitions parsed
   only the target from `frame_transition__(...)` and discarded
   exit/enter/state-args. Fix: paren-aware split of all 7 args,
   full Data record update with capitalised state-arg references.

3. **Erlang `frame_transition__(...)` lines containing
   `self.<iface>(...)` calls** fell through to the blanket
   `self.` → `Data#data.` substitution, emitting invalid
   `Data#data.method()` (record-field-call). Fix: a self-call
   hoisting pre-pass that lifts each call into a preceding
   `frame_dispatch__` bind and substitutes the result variable
   back into the transition's arg slot.

4. **Rust HSM enum: state-args written to unit-variant ancestors**
   — `rust_system.rs` cascaded args to all chain ancestors under
   "signature-match guarantees uniform args", which is wrong when
   only the leaf declares params. Fix: condition the ancestor walk
   on `ctx.state_param_names[ancestor]` non-empty (tuple variant)
   — skip unit-variant ancestors whose StateContext can't carry
   args.

Generator-side: PHP variable references use `{spec.param_prefix}x`
(resolves to `$x`); Erlang section in the runner is conditional on
`FUZZ_DRIVE_ARG` empty (drive/1) vs present (drive/2 with arg).

---

## Phase 16: Comments + whitespace robustness fuzz (wave 1)

`gen_comments.py` + `run_comments.sh` — line comments at multiple
positions in handler bodies and inside the machine block. Frame
source for a target uses that target's comment leader (Oceans
Model — `#` for Python/Ruby/GDScript, `//` for C-family/Java/etc.,
`--` for Lua, `%` for Erlang).

Patterns (4):
- `p1_comment_before_stmt` — native line comment BEFORE the
  assignment in a handler body.
- `p2_comment_after_stmt` — line comment AFTER the assignment,
  on its own line.
- `p3_comment_between_stmts` — comment line BETWEEN two native
  statements (both must still emit).
- `p4_native_machine_comments` — native-leader comments inside
  the machine block (between state declarations + between
  handlers). Tests Frame's section-comment capture round-trips
  through codegen.

Total: 4 × 10 = 40 cases per lang × 17 langs = 680.

```bash
python3 gen_comments.py
./run_comments.sh --tier=smoke
./run_comments.sh --tier=full
```

Wave 1 result (2026-04-29): **680 / 680 passing across 17
backends**, zero framec defects (after target-leader convention
adopted — see FUZZ_PLAN.md "Defect surfaced (parked)" note for
the Frame `//` leak found during P4 development).

---

## Phase 18: Stress / boundary fuzz (wave 1)

`gen_stress.py` + `run_stress.sh` — endurance tests for the Frame
runtime's event-dispatch loop, transition pipeline, and modal-stack
discipline. Tests are unrolled (no language-native loops in the
driver) so the case file scales linearly with N — keeping
language-agnostic.

Patterns (3):
- `p1_many_dispatches` — bump() called N times. Tests handler
  dispatch loop endurance.
- `p2_transition_pingpong` — alternating $S0↔$S1 transitions, N
  cycles. Tests transition kernel under load.
- `p3_push_pop_depth` — push$ then pop$ cycle, N times. Tests
  modal-stack discipline at depth.

Stress levels (tier-driven): smoke N=10, full N=100. Capped at 100
to keep wall-clock under ~5s/backend; for deeper stress, run
manually with a higher N or extend the generator with language-
native loops.

Total: 3 patterns × 2 tiers × 17 langs = 102 case-runs.

```bash
python3 gen_stress.py
./run_stress.sh --tier=smoke    # N=10
./run_stress.sh --tier=full     # N=100
```

Wave 1 result (2026-04-29): **102 / 102 passing across 17 backends**,
zero framec defects. Frame runtimes are durable at modest N.

---

## Phase 21: Arithmetic edge fuzz (wave 1)

`gen_arith.py` + `run_arith.sh` — int arithmetic edge cases. Frame
has no type system; expressions pass through to the target. Wave 1
verifies Frame's expression passthrough preserves operator
precedence, associativity, and explicit parenthesisation across
17 backends for portable int arithmetic.

Patterns (4):
- `p1_add_chain` — 4-operator chain (a + b + a + b + a).
- `p2_precedence` — `a + b * a` (multiplication binds tighter).
- `p3_subtraction` — `a - b - a` (left-to-right associativity).
- `p4_paren_grouping` — `(a + b) * a` (explicit parens preserved).

Value tuples: 10 pairs covering simple, negative, zero, mixed-sign
(values fit in signed-32-bit so results agree across backends).

Total: 4 × 10 = 40 cases per lang × 17 langs = 680.

Wave 1 result (2026-04-29): **680 / 680 passing across 17
backends**, zero framec defects.

```bash
python3 gen_arith.py
./run_arith.sh --tier=smoke
./run_arith.sh --tier=full
```

Wave 2 candidates (int ↔ str / float / signed-unsigned coercions)
were intentionally deferred — those test target-side type behavior,
not framec.

---

## Phase 20: Const + @@:system access fuzz (wave 1)

`gen_const_sys.py` + `run_const_sys.sh` — `const` domain fields and
`@@:system.state` reads. Two Frame features that hadn't been fuzzed.

Patterns (3):
- `p1_const_field` — `const k: int = LIT` initialized to a literal,
  read back via `get_const(): int`.
- `p2_sys_state_initial` — `@@:system.state` read immediately after
  construction returns `"S0"`.
- `p3_sys_state_after_xfer` — drive transitions to $S1; reading
  `@@:system.state` returns `"S1"`. Verifies the runtime updates
  the state name across transitions.

Total: 3 × 10 = 30 cases per lang × 16 langs = 480.

Erlang is **skipped** in wave 1: Erlang represents state names as
atoms (`s0`, lowercase) vs other backends emit strings (`S0`,
source-cased). The atom-vs-string mismatch isn't a framec defect
— it's a representation choice. Wave 2 design question.

```bash
python3 gen_const_sys.py
./run_const_sys.sh --tier=smoke
./run_const_sys.sh --tier=full
```

Wave 1 result (2026-04-29): **480 / 480 passing across 16
backends**, zero framec defects.

---

## Phase 17: Multi-event traces fuzz (wave 1)

`gen_multievent.py` + `run_multievent.sh` — event sequences fired
in order, with/without transitions between, accumulating effects on
state. Most other phases test ONE event in isolation; multi-event
surfaces ordering/cascade bugs that single-event tests can't see.

Patterns (4):
- `p1_three_event_same_state` — 3 events on the same state, each
  bumping $.f. Tests mutation accumulation.
- `p2_event_then_transition` — A in $S0 transitions to $S1; B in
  $S1 bumps. Tests state-identity across event boundaries.
- `p3_chain_three_states` — 4-event sequence chaining $S0 → $S1
  → $S2 with bumps in each.
- `p4_event_in_hsm_chain` — drive into HSM child; bump direct on
  child; fwd_bump forwarded (=> $^) to parent. Tests mixed
  direct/forwarded handling across an event sequence.

Value tuples (10): mixed sign + magnitude.
Total: 4 × 10 = 40 cases per lang × 17 langs = 680.

```bash
python3 gen_multievent.py
./run_multievent.sh --tier=smoke                 # ~20s parallel
./run_multievent.sh --tier=full                  # ~3-4 min
./run_multievent.sh --tier=full --lang=erlang    # one lang only
```

Wave 1 result (2026-04-29): **680 / 680 passing across 17
backends**, zero framec defects.

---

## Phase 19: Push/pop modal stack fuzz (wave 1)

`gen_pushpop.py` + `run_pushpop.sh` — `push$` / `-> pop$` modal
stack interactions. Frame's modal stack saves a compartment
reference on push and restores it on pop, including state-vars.
Domain fields are global; their changes during the pushed state
survive the pop.

Patterns (6):
- `p1_dom_persists` — push from $S0, bump domain in pushed $S1,
  pop back: domain value preserved.
- `p2_sv_restored` — both $S0 and $S1 declare $.x; modifying $S1's
  $.x doesn't leak to $S0 after pop (separate compartments).
- `p3_depth_two` — two pushes deep, two pops, domain bumps from
  both sticky.
- `p4_pop_then_event` — state-var on $S0 reads back the original
  default after a push/pop cycle.
- `p5_push_from_hsm_child` (wave 2) — push from HSM child; saved
  compartment's parent_compartment chain survives pop.
- `p6_push_into_hsm_chain` (wave 2) — push from HSM leaf, transition
  to sibling, pop back; restored leaf's handlers still dispatch.
- `p7_state_args_round_trip` (wave 3) — push from a state with
  `(x: int)`; pop; state-arg `x` restored faithfully.
- `p8_enter_args_round_trip` (wave 3) — push from a state with
  `$>(a: int)` enter handler; pop; enter-args restored.
- `p9_combined_args` (wave 3) — both state-args + enter-args
  together — both contexts must survive a push/pop.
- `p10_hsm_state_args_push_pop` (wave 3) — HSM × state-args ×
  push/pop. Push from HSM child carrying state-args, transition
  to sibling, pop back; both state-args and parent_compartment
  chain restored.

Value tuples (10): mixed sign + magnitude.
Total: 10 × 10 = 100 cases per lang × 17 langs = 1,700.

```bash
python3 gen_pushpop.py
./run_pushpop.sh --tier=smoke                    # ~20s parallel
./run_pushpop.sh --tier=full                     # ~3-4 min
./run_pushpop.sh --tier=full --lang=erlang       # one lang only
```

Wave 3 result (2026-04-29): **1,700 / 1,700 passing across 17
backends** after fixing two framec defects (committed in framepiler
`3f0cd24`):
1. **Erlang push/pop discarded state-args + enter-args.** The
   push side stored only the state atom on `frame_stack`, so pop
   restored the state name but left the arg lists at the pushed
   destination's values. Fix: push a 3-tuple
   `{state_atom, state_args, enter_args}`; pop pattern-matches
   and restores both lists.
2. **Rust prepareEnter/prepareExit on negative literals.** Codegen
   emitted `-3.to_string()` which parses as `-(3.to_string())`
   (E0600). Fix: wrap as `(-3).to_string()`.

Wave 2 result (2026-04-29): **1,020 / 1,020 passing across 17
backends**, zero framec defects. HSM × push/pop confirmed clean.

Wave 1 result (2026-04-29): **680 / 680 passing across 17
backends**, zero framec defects.

**Frame-spec note (relevant for wave 2 design):** `pop$` re-fires
the saved state's `$>` handler. State-vars have a re-init guard
("if not in compartment.state_vars" pattern) but user-written
enter-handler logic is NOT auto-guarded. Any test that relies on
post-pop state must either avoid state-mutating `$>` handlers or
make them idempotent.
