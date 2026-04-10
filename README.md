# Frame Test Environment

Test infrastructure for the Frame transpiler (`framec`) across 17 target language backends.

## Quick Start (Docker — Recommended)

```bash
cd docker/

# Build everything and run all tests
make test

# Single language
make test-python

# See all commands
make help
```

The Makefile handles cross-compilation, container builds, caching, and test execution. It only rebuilds what changed.

See [docs/docker.md](docs/docker.md) for full Docker guide.

## Quick Start (Native)

```bash
cd tests/
./run_tests.sh              # Run all languages
./run_tests.sh --python     # Single language
./run_tests.sh --help       # All options
```

Requires each language's toolchain installed locally.

## Supported Languages

| Language | Extension | Target Name | Status |
|---|---|---|---|
| Python | `.fpy` | `python_3` | Stable |
| TypeScript | `.fts` | `typescript` | Stable |
| JavaScript | `.fjs` | `javascript` | Stable |
| Rust | `.frs` | `rust` | Stable |
| C | `.fc` | `c` | Stable |
| C++ | `.fcpp` | `cpp` | Stable |
| C# | `.fcs` | `csharp` | Stable |
| Java | `.fjava` | `java` | Stable |
| Go | `.fgo` | `go` | Stable |
| PHP | `.fphp` | `php` | Experimental |
| Kotlin | `.fkt` | `kotlin` | Experimental |
| Swift | `.fswift` | `swift` | Experimental |
| Ruby | `.frb` | `ruby` | Experimental |
| Erlang | `.ferl` | `erlang` | Experimental |
| Lua | `.flua` | `lua` | Experimental |
| Dart | `.fdart` | `dart` | Experimental |
| GDScript | `.fgd` | `gdscript` | Experimental |

## Directory Structure

```
framepiler_test_env/
├── tests/
│   ├── run_tests.sh              # Native test runner
│   ├── run_single_test.sh        # Per-test helper
│   ├── common/
│   │   ├── positive/<category>/  # Tests that should pass (per-language files)
│   │   ├── compile-error/        # Expected compile failures
│   │   ├── transpile-error/      # Expected transpile failures
│   │   └── runtime-error/        # Expected runtime failures
│   ├── python/                   # Python-specific tests
│   ├── typescript/               # TypeScript-specific tests
│   ├── rust/                     # Rust-specific tests
│   └── c/                        # C-specific tests
├── output/                       # Generated code (gitignored)
├── docker/                       # Docker test infrastructure
│   ├── docker-compose.yml        # 17 language containers
│   ├── run.sh                    # Orchestrator
│   ├── base/<lang>/Dockerfile    # Per-language images
│   └── runners/runner.sh         # Shared test runner
├── docs/                         # Guides
└── scripts/                      # Utilities
```

## Guides

- [Docker Testing](docs/docker.md) — Running tests in containers, cross-compilation, debugging failures
- [Writing Tests](docs/writing-tests.md) — Test file format, harness patterns, markers
- [Adding a Language](docs/adding-a-language.md) — New backend container + runner setup

## Test Output

All tests emit TAP (Test Anything Protocol) for CI integration. Summary lines:

```
# python: 161 passed, 0 failed, 0 skipped
```
