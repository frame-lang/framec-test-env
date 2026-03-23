# Frame Test Environment

Test infrastructure for Frame V4 language validation.

## Quick Start

```bash
# Run all tests locally
cd tests
./run_tests.sh

# Run specific language or category
./run_tests.sh --python
./run_tests.sh --category primary
./run_tests.sh --help
```

## Directory Structure

```
framepiler_test_env/
├── tests/                   # Test sources
│   ├── run_tests.sh         # Unified test runner
│   ├── common/              # Cross-language tests
│   │   ├── positive/        # Positive tests (transpile + compile + run OK)
│   │   │   ├── primary/     # Core reference tests (49 tests)
│   │   │   ├── automata/    # Mealy/Moore machines
│   │   │   ├── capabilities/# Actions, operations, persistence
│   │   │   ├── control_flow/# If/else, while, forwards
│   │   │   ├── core/        # Core language features
│   │   │   ├── data_types/  # Lists, dicts, strings
│   │   │   ├── exec_smoke/  # Execution smoke tests
│   │   │   ├── interfaces/  # Interface methods
│   │   │   ├── operators/   # Arithmetic, comparison, logical
│   │   │   ├── scoping/     # Variable scoping
│   │   │   ├── systems/     # State machines, HSM
│   │   │   └── validator/   # Validation tests
│   │   ├── compile-error/   # Expected compile failures
│   │   ├── transpile-error/ # Expected transpile failures
│   │   └── runtime-error/   # Expected runtime failures
│   ├── python/              # Python-specific tests (.fpy)
│   ├── typescript/          # TypeScript-specific tests (.fts)
│   ├── rust/                # Rust-specific tests (.frs)
│   └── c/                   # C-specific tests (.fc)
├── output/                  # Generated code (build artifacts)
│   ├── python/tests/
│   ├── typescript/tests/
│   ├── rust/tests/
│   └── c/tests/
├── docker/                  # Docker test runners
├── bug/                     # Bug tracking
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

## Test Counts

| Scope | Python | TypeScript | Rust | C | Total |
|-------|--------|------------|------|---|-------|
| common/ | 146 | 137 | 140 | 147 | 570 |
| language-specific/ | 15 | 6 | 7 | 0 | 28 |
| **Total** | **161** | **143** | **147** | **147** | **598** |

All 598 tests passing (100%).

## File Extensions

- `.fpy` - Python target (`@@target python_3`)
- `.fts` - TypeScript target (`@@target typescript`)
- `.frs` - Rust target (`@@target rust`)
- `.fc` - C target (`@@target c`)

## Test Output

All tests emit TAP (Test Anything Protocol) output for CI integration.

Last verified: 2026-03-23 — Python 161, TypeScript 143, Rust 147, C 147 (598 total, 100% passing)
