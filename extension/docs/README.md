# Frame VS Code Extension Test Documentation

## Overview
This directory contains the segregated test environment for the Frame VS Code Extension (Debugger) team. We operate in the `frame-debugger-*` namespace, completely isolated from the framepiler team's `frame-transpiler-*` namespace.

## Namespace Allocation
- **Container prefix**: `frame-debugger-*`
- **Network subnet**: `172.29.0.0/16`
- **Port range**: `9500-9999`
- **Mount paths**: `/debugger/*`
- **Docker labels**: `frame.component=debugger`

## Directory Structure
```
extension/
├── docker/              # Docker configurations
│   ├── debugger-test-base.dockerfile
│   ├── docker-compose.debugger-test.yml
│   └── run-debugger-tests.sh
├── tests/               # Test suites
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── smoke/          # Smoke tests
├── fixtures/           # Test Frame files
│   ├── simple/         # Basic test cases
│   └── complex/        # Advanced scenarios
├── mocks/              # Mock VS Code APIs
├── scripts/            # Test utilities
├── results/            # Test execution results
│   └── <test-run-id>/  # Timestamped results
└── docs/               # This documentation

```

## Quick Start

### Running Tests
```bash
# From extension/docker directory
./run-debugger-tests.sh          # Run all tests
./run-debugger-tests.sh unit     # Run unit tests only
./run-debugger-tests.sh smoke    # Run smoke tests
./run-debugger-tests.sh debug    # Debug mode (container stays running)
```

### Checking Status
```bash
./run-debugger-tests.sh status   # Show all debugger containers/networks/volumes
./run-debugger-tests.sh logs     # View test logs
```

### Cleanup
```bash
./run-debugger-tests.sh clean    # Remove all debugger resources (safe - won't touch transpiler)
```

## Docker Configuration

### Key Settings
- **Image**: `frame-debugger/test-base:latest`
- **Network**: `frame-debugger-test-net-main` (172.29.0.0/24)
- **Volumes**: All prefixed with `frame-debugger-*`
- **Resource Limits**: 4 CPUs, 8GB memory per container

### Port Mappings
- `9501`: Frame debug server
- `9510`: Node.js debugger
- `9511`: Python debugger
- `9500-9999`: Available for additional services

## Test Organization

### Unit Tests (`/tests/unit/`)
- Frame state machine tests
- Debug adapter protocol tests
- Source mapping tests

### Integration Tests (`/tests/integration/`)
- Full debugging session flows
- Breakpoint verification
- Variable inspection
- Call stack generation

### Smoke Tests (`/tests/smoke/`)
- Basic connection tests
- Minimal debugging scenarios
- Quick validation

## Writing Tests

### Test File Naming
```
test-<feature>-<type>.js
Example: test-breakpoints-unit.js
```

### Test Structure
```javascript
// tests/unit/test-breakpoints-unit.js
describe('Breakpoint Management', () => {
    it('should map Frame lines to Python lines', () => {
        // Test implementation
    });
});
```

## Common Tasks

### Adding a New Test
1. Create test file in appropriate directory (`unit/`, `integration/`, `smoke/`)
2. Follow naming convention
3. Run locally: `./run-debugger-tests.sh unit`
4. Results saved to `results/<timestamp>/`

### Debugging Failed Tests
```bash
# Start debug container
./run-debugger-tests.sh debug

# In another terminal, connect to container
docker exec -it frame-debugger-test-debug bash

# Run specific test
cd /debugger
npm test -- --grep "specific test name"
```

### Using Common Resources
Common test frames are available at:
- `/debugger/test-frames/` (mounted from `common/test-frames/`)
- `/debugger/builds/` (mounted from `common/builds/`)

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run debugger tests
  run: |
    cd test_env/extension/docker
    ./run-debugger-tests.sh all
```

### Test Reports
Test results are stored with unique IDs:
- Format: `debugger-YYYYMMDD-HHMMSS-<pid>`
- Location: `extension/results/<test-run-id>/`
- Contains: logs, test output, coverage reports

## Troubleshooting

### Container Won't Start
```bash
# Check for conflicts
./run-debugger-tests.sh status

# Clean and retry
./run-debugger-tests.sh clean
./run-debugger-tests.sh build --no-cache
```

### Out of Resources
```bash
# Check resource usage
docker stats --filter "label=frame.component=debugger"

# Clean up old containers
docker system prune -f --filter "label=frame.component=debugger"
```

### Network Issues
Ensure you're using the correct subnet:
- Debugger: `172.29.0.0/16`
- Transpiler: `172.28.0.0/16` (different - no conflict)

## Best Practices

1. **Always use namespace prefix**: All resources must start with `frame-debugger-`
2. **Label everything**: Add `frame.component=debugger` to all Docker resources
3. **Stay in port range**: Use ports 9500-9999 only
4. **Mount at /debugger/**: All container paths should be under `/debugger/`
5. **Clean up regularly**: Run `./run-debugger-tests.sh clean` after test sessions
6. **Document changes**: Update this README when adding new test types

## Contact
Frame VS Code Extension Team
- Repository: https://github.com/frame-lang/vscode_editor
- Test Environment: This directory (`extension/`)

## See Also
- [Common Resources Documentation](../../common/docs/README.md)
- [Segregation Policy](../../common/docker/SEGREGATION_POLICY.md)
- [VS Code Extension Main Repo](https://github.com/frame-lang/vscode_editor)