# Restructure Plan Addendum - Docker Segregation Updates

## Enhanced Directory Structure with Docker Segregation

Building on the original restructure plan, add Docker-specific segregation:

```
/Users/marktruluck/projects/framepiler_test_env/
├── framepiler/          # Framepiler team's isolated space
│   ├── tests/           # Transpiler test cases
│   ├── fixtures/        # Test data/fixtures for transpilation
│   ├── scripts/         # Framepiler test scripts
│   ├── docker/          # Framepiler Docker configurations (NEW)
│   │   ├── transpiler-test-base.dockerfile
│   │   ├── docker-compose.transpiler-test.yml
│   │   └── run-transpiler-tests.sh
│   ├── results/         # Test execution results (NEW)
│   │   └── <test-run-id>/
│   └── docs/
│
├── extension/           # VS Code extension team's isolated space
│   ├── tests/
│   ├── fixtures/
│   ├── mocks/
│   ├── scripts/
│   ├── docker/          # Extension Docker configurations (NEW)
│   │   ├── debugger-test-base.dockerfile
│   │   ├── docker-compose.debugger-test.yml
│   │   └── run-debugger-tests.sh
│   ├── results/         # Test execution results (NEW)
│   │   └── <test-run-id>/
│   └── docs/
│
└── common/
    ├── builds/
    ├── test-frames/
    ├── schemas/
    ├── docker/          # Shared Docker policies (NEW)
    │   ├── SEGREGATION_POLICY.md
    │   ├── base-images/  # Optional shared base layers
    │   └── monitoring/   # Shared monitoring scripts
    └── docs/
```

## Docker Namespace Segregation

### Framepiler Team (Transpiler):
- **Container prefix**: `frame-transpiler-*`
- **Image namespace**: `frame-transpiler/*`
- **Network prefix**: `frame-transpiler-test-net-*`
- **Network subnet**: `172.28.0.0/16`
- **Volume prefix**: `frame-transpiler-*`
- **Container labels**: `frame.component=transpiler`
- **Mount paths**: `/transpiler/*`
- **Port range**: `9000-9499`

### Extension Team (Debugger):
- **Container prefix**: `frame-debugger-*`
- **Image namespace**: `frame-debugger/*`
- **Network prefix**: `frame-debugger-test-net-*`
- **Network subnet**: `172.29.0.0/16`
- **Volume prefix**: `frame-debugger-*`
- **Container labels**: `frame.component=debugger`
- **Mount paths**: `/debugger/*`
- **Port range**: `9500-9999`

## Updated Docker Integration Strategy

### Framepiler Team Docker Mounts:
```yaml
volumes:
  # Team-specific mounts
  - ./framepiler/tests:/transpiler/tests:ro
  - ./framepiler/fixtures:/transpiler/fixtures:ro
  - ./framepiler/results:/transpiler/results:rw
  
  # Common resources (read-only)
  - ./common/builds:/transpiler/builds:ro
  - ./common/test-frames:/transpiler/test-frames:ro
  
  # Binary under test
  - ./common/builds/nightly/latest/framec:/transpiler/framec:ro
  
  # NOT mounting extension/ - complete isolation
```

### Extension Team Docker Mounts:
```yaml
volumes:
  # Team-specific mounts
  - ./extension/tests:/debugger/tests:ro
  - ./extension/fixtures:/debugger/fixtures:ro
  - ./extension/results:/debugger/results:rw
  
  # Common resources (read-only)
  - ./common/builds:/debugger/builds:ro
  - ./common/test-frames:/debugger/test-frames:ro
  
  # Extension under test
  - ./extension/vsix/latest:/debugger/extension:ro
  
  # NOT mounting framepiler/ - complete isolation
```

## Environment Variable Namespacing

### Framepiler Variables:
```bash
FRAME_TEST_NAMESPACE=transpiler
FRAME_TEST_COMPONENT=<component>
FRAME_TRANSPILER_VERSION=<version>
TEST_RUN_ID=transpiler-<timestamp>-<pid>
```

### Extension Variables:
```bash
FRAME_TEST_NAMESPACE=debugger  
FRAME_TEST_COMPONENT=<component>
FRAME_DEBUGGER_VERSION=<version>
TEST_RUN_ID=debugger-<timestamp>-<pid>
```

## Resource Management

### Per-Team Docker Limits:
```yaml
framepiler_resources:
  cpus: '8.0'
  memory: 16GB
  containers: 20
  disk: 100GB

extension_resources:
  cpus: '8.0'
  memory: 16GB
  containers: 20
  disk: 100GB
```

## Conflict Detection Scripts

Add to `/common/docker/monitoring/`:

```bash
#!/bin/bash
# check-conflicts.sh

# Check for cross-team container usage
if docker ps | grep -E "frame-(transpiler|debugger)-"; then
    echo "Active containers detected:"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep frame-
fi

# Check network conflicts
docker network ls --format "{{.Name}}" | grep -E "frame-(transpiler|debugger)-"

# Check volume conflicts  
docker volume ls --format "{{.Name}}" | grep -E "frame-(transpiler|debugger)-"

# Report resource usage
echo "Resource usage by team:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
  --filter "label=frame.component=transpiler" \
  --filter "label=frame.component=debugger"
```

## CI/CD Pipeline Updates

### Framepiler CI:
```yaml
jobs:
  test-transpiler:
    runs-on: ubuntu-latest
    env:
      FRAME_TEST_NAMESPACE: transpiler
    steps:
      - uses: actions/checkout@v3
      - name: Run transpiler tests
        run: |
          cd framepiler/docker
          ./run-transpiler-tests.sh
```

### Extension CI:
```yaml
jobs:
  test-debugger:
    runs-on: ubuntu-latest
    env:
      FRAME_TEST_NAMESPACE: debugger
    steps:
      - uses: actions/checkout@v3
      - name: Run debugger tests
        run: |
          cd extension/docker
          ./run-debugger-tests.sh
```

## Registry Structure (When Published)

```
ghcr.io/frame-lang/
├── transpiler/
│   ├── test-base:latest
│   ├── test-base:v0.86.71
│   └── test-runner:latest
└── debugger/
    ├── test-base:latest
    ├── test-base:v1.0.0
    └── mock-vscode:latest
```

## Cleanup Policies

### Automatic Cleanup Cron Jobs:
```cron
# Clean up old transpiler containers (daily at 2am)
0 2 * * * docker system prune -f --filter "label=frame.component=transpiler" --filter "until=24h"

# Clean up old debugger containers (daily at 3am)
0 3 * * * docker system prune -f --filter "label=frame.component=debugger" --filter "until=24h"

# Clean up orphaned networks (hourly)
0 * * * * docker network prune -f
```

## Test Result Aggregation

### In `/common/reports/` (NEW):
```
reports/
├── transpiler/
│   ├── latest -> 2024-12-08-143022/
│   └── 2024-12-08-143022/
│       ├── summary.json
│       ├── python.json
│       ├── typescript.json
│       └── rust.json
└── debugger/
    ├── latest -> 2024-12-08-143523/
    └── 2024-12-08-143523/
        ├── summary.json
        └── integration.json
```

## Monitoring Dashboard

Consider adding a simple monitoring page at `/common/dashboard/`:

```html
<!DOCTYPE html>
<html>
<head><title>Frame Test Environment Status</title></head>
<body>
  <h1>Test Environment Status</h1>
  
  <h2>Transpiler Team</h2>
  <div id="transpiler-status">
    <!-- Real-time container status -->
  </div>
  
  <h2>Debugger Team</h2>
  <div id="debugger-status">
    <!-- Real-time container status -->
  </div>
  
  <h2>Resource Usage</h2>
  <div id="resource-graph">
    <!-- CPU/Memory usage graphs -->
  </div>
</body>
</html>
```

## Migration Checklist Updates

Add to Phase 3:
- [ ] Create team-specific Docker directories
- [ ] Move Docker configurations to team directories
- [ ] Update image names to use team namespaces
- [ ] Verify network subnet segregation
- [ ] Test concurrent execution without conflicts
- [ ] Set up container label filtering
- [ ] Configure resource limits
- [ ] Test cleanup scripts preserve other team's resources

## Enforcement Mechanisms

1. **Pre-commit Hooks**: Validate Docker configs use correct namespaces
2. **CI Gates**: Reject PRs that violate segregation
3. **Runtime Checks**: Scripts verify namespace before execution
4. **Audit Logs**: Track which team ran what and when
5. **Alerts**: Notify when approaching resource limits

## Success Metrics

- Zero container name collisions
- Zero network conflicts  
- Independent CI pipelines run in parallel
- Each team can clean up without affecting the other
- Resource usage stays within limits
- Clear audit trail of test executions