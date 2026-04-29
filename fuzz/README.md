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
