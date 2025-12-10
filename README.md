# Frame Test Environment

Shared test environment for the Frame transpiler and VS Code extension teams.

## Directory Structure

This repository is organized to provide complete isolation between teams while maintaining shared resources:

```
framepiler_test_env/
├── framepiler/          # Transpiler team's isolated space
├── extension/           # VS Code extension team's isolated space
├── common/              # Shared resources (read-only during tests)
├── bug/                 # Bug tracking and artifacts
├── sandbox/             # Experimental code and prototypes
└── adapter_protocol/    # Protocol testing (to be moved to extension/)
```

## Team Spaces

### Transpiler Team (`framepiler/`)
- **Owner**: Frame transpiler team
- **Purpose**: All transpiler-specific tests and fixtures
- **Docker namespace**: `frame-transpiler-*`
- **Network subnet**: `172.28.0.0/16`
- **Port range**: `9000-9499`

### Extension Team (`extension/`)
- **Owner**: VS Code extension team
- **Purpose**: All debugger/extension tests and fixtures
- **Docker namespace**: `frame-debugger-*`
- **Network subnet**: `172.29.0.0/16`
- **Port range**: `9500-9999`

### Shared Resources (`common/`)
- **Owner**: Joint ownership
- **Purpose**: Shared binaries, test frames, schemas
- **Access**: Read-only during test execution
- See `common/README.md` for details

## Docker Segregation

Both teams use Docker for test isolation with strict namespace segregation:

### Check for Conflicts
Before running tests, check for potential conflicts:
```bash
./common/docker/monitoring/check-conflicts.sh
```

### Run Transpiler Tests
```bash
cd framepiler/docker
./run-transpiler-tests.sh
```

### Run Extension Tests
```bash
cd extension/docker
./run-debugger-tests.sh
```

## Segregation Policy

See `common/docker/SEGREGATION_POLICY.md` for complete details on:
- Container naming conventions
- Network isolation
- Resource limits
- Cleanup procedures
- Emergency protocols

## Quick Start

### For Transpiler Team
1. Place test fixtures in `framepiler/fixtures/`
2. Add test scripts to `framepiler/scripts/`
3. Run tests using `framepiler/docker/run-transpiler-tests.sh`
4. Results will be in `framepiler/results/`

### For Extension Team
1. Place test fixtures in `extension/fixtures/`
2. Add test scripts to `extension/scripts/`
3. Run tests using `extension/docker/run-debugger-tests.sh`
4. Results will be in `extension/results/`

### Legacy Adapter Protocol Tests
Quick validation for V3 TS generated systems:
```bash
FRAMEC_BIN=/path/to/framec ./adapter_protocol/scripts/run_adapter_smoke.sh
```

## Adding Shared Resources

### New framec Binary
```bash
# For stable releases
version="v0.86.71"
mkdir -p common/builds/stable/$version
cp /path/to/framec common/builds/stable/$version/

# For nightly builds
date_stamp=$(date +%Y%m%d)
commit="abc123"
mkdir -p common/builds/nightly/${date_stamp}-${commit}
cp /path/to/framec common/builds/nightly/${date_stamp}-${commit}/
```

### New Test Frames
Add canonical test files to `common/test-frames/`:
- `basic/` - Simple test cases
- `advanced/` - Complex state machines
- `edge-cases/` - Error conditions

## Important Rules

1. **Never** modify another team's directory
2. **Always** use proper Docker namespaces
3. **Check** for conflicts before running tests
4. **Document** any changes to shared resources
5. **Preserve** old versions for regression testing

## Recent Updates

- **2024-12-10**: Restructured environment with team segregation
- **2024-12-10**: Added Docker namespace isolation
- **2024-12-10**: Implemented monitoring scripts
- **2024-12-10**: Created shared resource management

## Documentation

- `RESTRUCTURE_PLAN.md` - Original restructuring proposal
- `RESTRUCTURE_PLAN_ADDENDUM.md` - Docker segregation enhancements
- `SHARED_TEST_ENV_PROPOSAL.md` - Initial environment proposal
- `common/docker/SEGREGATION_POLICY.md` - Docker namespace rules

## Contact

- **Transpiler team**: #frame-transpiler
- **Extension team**: #frame-debugger
- **Conflicts**: #frame-testing-conflicts
