# Framepiler Team Test Directory

This directory contains all transpiler-specific test resources.

## Directory Structure

```
framepiler/
├── docker/              # Docker configurations for transpiler tests
│   ├── transpiler-test-base.dockerfile
│   ├── docker-compose.transpiler-test.yml
│   └── run-transpiler-tests.sh
├── test_runner/         # Test execution infrastructure (NEW)
│   ├── docker_orchestrator.py    # Docker container management
│   └── shared_env_test_runner.py # Main test runner
├── tests/               # Test cases and test runners
├── fixtures/            # Test fixtures and Frame files (558 tests)
│   └── test-frames/     # Migrated V3 test fixtures
│       ├── v3/          # V3 architecture tests (19 categories)
│       └── common/      # Common/shared tests
├── frame_runtime_py/    # Python Frame runtime
├── scripts/             # Test automation scripts
├── results/             # Test execution results (gitignored)
└── docs/                # Transpiler-specific test documentation
```

## Running Tests

### New Test Runner (Recommended)
```bash
# Run all Python tests
python3 test_runner/shared_env_test_runner.py \
  --framec /path/to/framec \
  --test-root fixtures \
  --language python

# Run specific category with Docker
python3 test_runner/shared_env_test_runner.py \
  --framec /path/to/framec \
  --test-root fixtures \
  --category v3_core \
  --verbose

# Run tests in parallel
python3 test_runner/shared_env_test_runner.py \
  --framec /path/to/framec \
  --test-root fixtures \
  --parallel 4 \
  --format junit \
  --output results/test-results.xml
```

### Legacy Docker Compose Method
```bash
cd docker/
./run-transpiler-tests.sh
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