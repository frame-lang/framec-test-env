# Framepiler Team Test Directory

This directory contains all transpiler-specific test resources.

## Directory Structure

```
framepiler/
├── docker/              # Docker test runner (Rust implementation)
│   ├── src/
│   │   └── main.rs     # Rust test runner implementation
│   ├── Cargo.toml      # Builds frame-docker-runner binary
│   ├── Dockerfile.python    # Python test container
│   ├── Dockerfile.typescript # TypeScript test container
│   ├── Dockerfile.rust      # Rust test container
│   └── target/release/
│       └── frame-docker-runner  # Test runner binary
├── frame_runtime_py/    # Python Frame runtime
├── frame_runtime_ts/    # TypeScript Frame runtime
├── scripts/             # Legacy test automation scripts
├── results/             # Test execution results (gitignored)
└── docs/                # Transpiler-specific test documentation
```

**Note**: All test fixtures (607 tests) are now in `../common/test-frames/v3/` shared with other teams.

## Running Tests

### Docker Test Runner (Current Architecture)
The test runner is a Rust binary located at `docker/target/release/frame-docker-runner`.

```bash
# Set environment variable
export FRAMEPILER_TEST_ENV=/path/to/framepiler_test_env

# Run Python tests
./docker/target/release/frame-docker-runner python_3 v3_data_types \
  --framec /path/to/framec

# Run TypeScript tests with verbose output
./docker/target/release/frame-docker-runner typescript v3_operators \
  --framec /path/to/framec --verbose

# Run Rust tests with JSON output
./docker/target/release/frame-docker-runner rust v3_systems \
  --framec /path/to/framec --json

# Run all categories for a language
for category in data_types operators scoping systems async persistence imports; do
  ./docker/target/release/frame-docker-runner python_3 v3_${category} \
    --framec /path/to/framec
done
```

### Building the Docker Runner
```bash
cd docker/
cargo build --release
```

### With Custom Environment
```bash
export FRAMEPILER_TEST_ENV=/path/to/test/env
export TEST_RUN_ID=custom-run-123
cd docker/
./run-transpiler-tests.sh
```

## Docker Configuration

All transpiler containers use the namespace `frame-transpiler-*`:
- **Container prefix**: `frame-transpiler-`
- **Image name**: `frame-transpiler/test-prt:latest`
- **Network**: `frame-transpiler-test-net-{RUN_ID}`
- **Subnet**: `172.28.0.0/16`

## Test Categories

**Total: 558 test files** across 19 V3 categories:

| Category | Tests | Description |
|----------|-------|-------------|
| `v3_core` | 12 | Core transpilation tests |
| `v3_control_flow` | 40 | Control flow constructs |
| `v3_systems` | 13 | System-level tests |
| `v3_data_types` | 5 | Data type handling |
| `v3_operators` | 5 | Operator transpilation |
| `v3_scoping` | 3 | Scope resolution |
| `v3_exec_smoke` | 8 | Execution smoke tests |
| `v3_validator` | 10 | Validation tests |
| `v3_mir` | 30 | MIR generation |
| `v3_async` | 1 | Async/await support |
| `v3_persistence` | 3 | Persistence features |
| `v3_prolog` | 4 | Prolog tests |
| `v3_imports` | 8 | Import handling |
| `v3_outline` | 6 | Outline generation |
| `v3_expansion` | 1 | Macro expansion |
| `v3_closers` | 3 | Closure tests |
| `v3_mapping` | 3 | Type mapping |
| `v3_capabilities` | 16 | Capability tests |
| `common` | 36 | Shared/common tests |

## Adding New Tests

1. Add test fixtures to `fixtures/`
2. Create test scripts in `scripts/`
3. Update Docker configuration if needed
4. Run tests and verify results in `results/`

## Results

Test results are stored in `results/` with the format:
```
results/{test-run-id}/
├── summary.json
├── python/
├── typescript/
└── rust/
```

## Cleanup

To clean up test artifacts:
```bash
# Remove all transpiler containers
docker ps -aq --filter 'label=frame.component=transpiler' | xargs docker rm -f

# Remove test networks
docker network ls --format '{{.Name}}' | grep "frame-transpiler-" | xargs docker network rm

# Clean results directory
rm -rf results/*
```

## Monitoring

Check for conflicts before running:
```bash
../../common/docker/monitoring/check-conflicts.sh
```

## Contact

- Team channel: #frame-transpiler
- Test issues: #frame-testing-conflicts