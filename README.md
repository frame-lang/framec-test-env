# Frame Test Environment

Test infrastructure for Frame V4 language validation.

## Quick Start

```bash
# Run all tests via Docker (recommended)
docker compose -f docker/docker-compose.yml up --build

# Or run locally
cd tests/common/primary
./run_tests.sh
```

## Directory Structure

```
framepiler_test_env/
├── tests/                   # Test sources
│   ├── common/              # Cross-language tests
│   │   ├── primary/         # Primary reference tests (32 tests)
│   │   ├── control_flow/    # Control flow tests
│   │   ├── operators/       # Operator tests
│   │   └── ...
│   ├── python/              # Python-specific tests
│   ├── typescript/          # TypeScript-specific tests
│   └── rust/                # Rust-specific tests
├── output/                  # Generated code (build artifacts)
│   ├── python/tests/
│   ├── typescript/tests/
│   └── rust/tests/
├── docker/                  # Docker test runners
├── bug/                     # Bug tracking
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

## Test Counts

| Location | Files |
|----------|-------|
| common/  | ~400  |
| python/  | 15    |
| typescript/ | 7  |
| rust/    | 7     |

## File Extensions

- `.fpy` - Python target
- `.fts` - TypeScript target
- `.frs` - Rust target

## Docker Test Results

All tests emit TAP (Test Anything Protocol) output for CI integration.

Last verified: Python 147, TypeScript 127, Rust 127 (401 total, 100% passing)
