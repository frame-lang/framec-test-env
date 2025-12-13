# Getting Started with Frame Testing

## Quick Start for New Agents/Developers

### What You Need to Know

1. **Test Infrastructure Lives Here** - All testing is in this shared environment, NOT in the transpiler project
2. **Use the Docker Runner** - It's a Rust binary that handles everything
3. **Tests are in `common/test-frames/v3/`** - 607 tests shared across teams

### Running Tests - The One Command You Need

```bash
# From the transpiler project root:
export FRAMEPILER_TEST_ENV=$(pwd)/framepiler_test_env

# Run tests for a language and category:
framepiler_test_env/framepiler/docker/target/release/frame-docker-runner \
  python_3 v3_data_types --framec ./target/release/framec
```

That's it! The Docker runner handles:
- Finding the right tests
- Transpiling them
- Running them in Docker containers
- Reporting results

### Architecture at a Glance

```
frame_transpiler/           → Only provides framec compiler
framepiler_test_env/       → All test infrastructure (this repo)
  ├── framepiler/          → Transpiler team space
  │   └── docker/          → Docker test runner (Rust)
  ├── extension/           → VS Code extension team space  
  └── common/              → Shared test files
      └── test-frames/v3/  → 607 test files
```

### Available Languages & Categories

**Languages**: `python_3`, `typescript`, `rust`

**Categories**: 
- `v3_data_types` - Data type tests
- `v3_operators` - Operator tests
- `v3_scoping` - Scoping tests
- `v3_systems` - System tests
- `v3_async` - Async tests
- `v3_persistence` - Persistence tests
- `v3_imports` - Import tests

### Building the Docker Runner (if needed)

```bash
cd framepiler_test_env/framepiler/docker
cargo build --release
```

### Common Tasks

#### Run all tests for a language
```bash
for category in data_types operators scoping systems async persistence imports; do
  framepiler_test_env/framepiler/docker/target/release/frame-docker-runner \
    python_3 v3_${category} --framec ./target/release/framec
done
```

#### Get JSON output for CI/CD
```bash
frame-docker-runner python_3 v3_data_types --framec ./target/release/framec --json
```

#### Verbose output for debugging
```bash
frame-docker-runner rust v3_systems --framec ./target/release/framec --verbose
```

### Important Notes

- **NO SCRIPTS NEEDED** - The Docker runner is a self-contained Rust binary
- **Tests use `@target` annotations** - Tests are filtered by language automatically
- **Tests can be skipped** - Use `@skip-if` annotations for conditional skipping
- **Docker images required**: 
  - `frame-transpiler-python:latest`
  - `frame-transpiler-typescript:latest`
  - `frame-transpiler-rust:latest`

### Troubleshooting

1. **"No test files found"** - Check that FRAMEPILER_TEST_ENV is set correctly
2. **Docker errors** - Ensure Docker is running and images are built
3. **Transpilation failures** - Verify framec path is correct

### Current Test Results (as of 2025-12-13)

- **Python**: 100% (14/14 tests passing)
- **TypeScript**: 100% (11/11 tests passing)
- **Rust**: 100% (15/15 tests passing)

All PRT (Python, Rust, TypeScript) languages have 100% test success!

### For More Details

- See `framepiler/docker/README.md` for Docker runner details
- See `common/README.md` for test organization
- See `README.md` for full environment overview