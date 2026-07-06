# Frame Test Environment — docs

Test infrastructure for the Frame transpiler (`framec`) across **17 target
language backends**. This directory holds the guides; the authoritative
top-level overview is [`../README.md`](../README.md).

## Quick Start

```bash
cd tests
./run_tests.sh              # Run all languages
./run_tests.sh --help       # Options
./run_tests.sh --langs py,ts,rs        # Subset of languages
./run_tests.sh --category primary      # One category
```

Docker (reproducible, all toolchains bundled) — see [docker.md](docker.md):

```bash
cd docker && make test
```

## Languages

17 backends. See the full table with target names and stability in
[`../README.md`](../README.md#supported-languages):
Python, TypeScript, JavaScript, Rust, C, C++, C#, Java, Go (stable);
PHP, Kotlin, Swift, Ruby, Lua, Dart, GDScript (experimental);
Erlang (**deprecated — being retired this release**).

## Directory Structure

```
framec-test-env/
├── tests/
│   ├── run_tests.sh              # native test runner (TAP output)
│   ├── run_single_test.sh        # per-(file,lang) helper
│   ├── common/
│   │   ├── positive/<category>/  # tests that should pass (per-language files)
│   │   ├── compile-error/        # generated code that must fail to compile
│   │   ├── transpile-error/      # Frame source framec must reject
│   │   │   └── fsm/              # @@fsm diagnostic suite (expect-error codes)
│   │   └── runtime-error/        # compiles but must fail at runtime
│   ├── <lang>/                   # language-specific tests (python, rust, java, …)
│   └── ...
├── output/                       # generated code (gitignored build artifacts)
├── docker/                       # 17-language container matrix + Makefile
├── fuzz/                         # generator-driven fuzz suites (gen_*.py + runners)
├── scripts/                      # check_coverage.py + check_docs.py (gates) + utilities
├── bug/                          # bug-tracking system
└── docs/                         # these guides
```

## Test Corpus (snapshot 2026-07)

`tests/common/positive/` holds **~5,800 fixtures across 22 categories**
(`primary`, `control_flow`, `demos`, `frame_machines`, `fsm`, `linux`,
`robotics`, `scientific`, `security`, `core`, `system_params`, `operators`,
`data_types`, `systems`, `capabilities`, `automata`, `behavior_trees`,
`interfaces`, `scoping`, `segmenter`, `max_coverage`, `validator`). Each
fixture stem is expected to exist for every applicable backend as either a
real port (`<stem>.f<ext>`) or a documented skip (`<stem>.f<ext>.skip.md`) —
see **Coverage gate** below. Run the suite for live counts; the numbers move
with every wave.

## Coverage gate

`scripts/check_coverage.py` enforces that every positive fixture stem has all
16 backends — a real port **or** a `<stem>.f<ext>.skip.md` placeholder that
documents why the backend is intentionally absent. Run it to see any gaps; each
gap needs a real fixture or a `.skip.md` naming the reason. See
[partial-coverage-audit.md](partial-coverage-audit.md) for the classification
methodology and the gap analysis.

## Doc-freshness gate

`scripts/check_docs.py` keeps the human docs from drifting away from the code.
The backend dispatch in `docker/runners/runner.sh` (language → framec target →
extensions) and the enforced set in `check_coverage.py` are the sources of
truth; the script verifies the README **Supported Languages** table (target
names, rows, the deprecated flag) and the "N backends" counts against them.
Run `python scripts/check_docs.py` to verify, or `--fix` to regenerate. A
stale table or an off-by-one count fails the check instead of misleading a
reader.

## Negative / error tests

Three categories under `tests/common/` assert that *invalid* input is
rejected, not silently miscompiled:

| Category | Asserts |
|---|---|
| `compile-error/` | generated code fails to compile |
| `transpile-error/` | framec rejects the Frame source |
| `transpile-error/fsm/` | framec rejects invalid `@@fsm` **with the right diagnostic code** (`# expect-error: EXXX`); see its [README](../tests/common/transpile-error/fsm/README.md) |

## Guides

- [docker.md](docker.md) — container matrix, cross-compilation, disk cleanup
- [writing-tests.md](writing-tests.md) — fixture format, markers, conventions
- [adding-a-language.md](adding-a-language.md) — new backend setup
- [runtime-capability-matrix.md](runtime-capability-matrix.md) — per-language conformance
- [partial-coverage-audit.md](partial-coverage-audit.md) — coverage-gap analysis
- [future-enhancements.md](future-enhancements.md) — perf/optimization backlog
