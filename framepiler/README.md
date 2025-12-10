# Framepiler Team Test Directory

This directory contains all transpiler-specific test resources.

## Directory Structure

```
framepiler/
├── docker/              # Docker configurations for transpiler tests
│   ├── transpiler-test-base.dockerfile
│   ├── docker-compose.transpiler-test.yml
│   └── run-transpiler-tests.sh
├── tests/               # Test cases and test runners
├── fixtures/            # Test fixtures and Frame files
├── scripts/             # Test automation scripts
├── results/             # Test execution results (gitignored)
└── docs/                # Transpiler-specific test documentation
```

## Running Tests

### Quick Start
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

Tests are organized by V3 categories:
- `v3_core` - Core transpilation tests
- `v3_control_flow` - Control flow constructs
- `v3_data_types` - Data type handling
- `v3_operators` - Operator transpilation
- `v3_systems` - System-level tests
- `v3_async` - Async/await support
- `v3_persistence` - Persistence features

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