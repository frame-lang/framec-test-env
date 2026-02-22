# Frame Test Environment

Shared test infrastructure for Frame V4 language validation.

## Quick Start

```bash
cd common/test-frames/v4/common/primary
./run_tests.sh
```

## Documentation

See [docs/README.md](docs/README.md) for the complete test architecture.

## Directory Structure

```
framepiler_test_env/
├── docs/                    # Documentation
├── common/
│   └── test-frames/
│       └── v4/              # V4 tests
│           ├── common/      # Tests passing in all 3 languages
│           ├── python/      # Python-specific tests
│           ├── typescript/  # TypeScript-specific tests
│           └── rust/        # Rust-specific tests
├── python_test_crate/       # Python test output
├── typescript_test_crate/   # TypeScript test output
└── rust_test_crate/         # Rust test output
```

## Test Counts

| Location | Files |
|----------|-------|
| common/  | 393   |
| python/  | 15    |
| typescript/ | 7  |
| rust/    | 7     |
