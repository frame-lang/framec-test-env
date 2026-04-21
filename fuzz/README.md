# Frame codegen fuzzer

Structural fuzzer for framec. Generates small Frame systems varying
structural combinations — HSM depth, push$/pop$, state variables,
enter/exit handlers, enter args, action control flow, handler control
flow, return type — then transpiles and syntax-checks each across every
target backend. Failures surface codegen bugs the hand-written test
matrix doesn't exercise.

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
