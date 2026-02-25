# Frame V4 Test Environment

## Quick Start

```bash
cd tests
./run_tests.sh          # Run all tests
./run_tests.sh --help   # Show options
```

**Full test documentation:** See [`tests/README.md`](../tests/README.md)

## Directory Structure

```
framepiler_test_env/
├── tests/                   # Test source files
│   ├── run_tests.sh         # THE test runner
│   ├── README.md            # Test documentation (READ THIS)
│   ├── common/              # Tests for all languages
│   ├── python/              # Python-only tests
│   ├── typescript/          # TypeScript-only tests
│   ├── rust/                # Rust-only tests
│   └── c/                   # C-only tests
├── output/                  # Generated code (build artifacts)
│   ├── python/tests/
│   ├── typescript/tests/
│   ├── rust/tests/
│   └── c/tests/
├── docker/                  # Docker test infrastructure
├── bug/                     # Bug tracking system
├── docs/                    # This documentation
└── scripts/                 # Utility scripts
```

## Languages Supported

| Language | Extension | Target | Status |
|----------|-----------|--------|--------|
| Python | `.fpy` | `@@target python_3` | Active |
| TypeScript | `.fts` | `@@target typescript` | Active |
| Rust | `.frs` | `@@target rust` | Active |
| C | `.fc` | `@@target c` | In Progress |

## Test Counts (2026-02-24)

| Scope | Python | TypeScript | Rust | C |
|-------|--------|------------|------|---|
| common/ | 137 | 126 | 126 | 12 |
| language-specific/ | 15 | 7 | 7 | 0 |
| **Total** | **152** | **133** | **133** | **12** |

**Total test files: 430**

## Running Tests

### Local (Recommended)

```bash
cd tests
./run_tests.sh                    # All tests, all languages
./run_tests.sh --python           # Python only
./run_tests.sh --category primary # Primary tests only
./run_tests.sh -v                 # Verbose output
```

### Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

## Test Documentation

For complete documentation on:
- Adding new tests
- Test markers (@skip, @known-fail)
- Directory conventions
- Troubleshooting

See: [`tests/README.md`](../tests/README.md)
