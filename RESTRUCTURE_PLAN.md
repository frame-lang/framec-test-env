# Test Environment Restructure Plan

## Overview
This document proposes a restructured test environment that provides clear segregation between the Framepiler team and the VS Code Extension team, while maintaining a common area for shared artifacts.

## Proposed Directory Structure

```
/Users/marktruluck/projects/framepiler_test_env/
├── framepiler/          # Framepiler team's isolated space
│   ├── tests/           # Transpiler test cases
│   ├── fixtures/        # Test data/fixtures for transpilation
│   ├── scripts/         # Framepiler test scripts
│   └── docs/            # Framepiler-specific test documentation
│       ├── README.md    # How to run framepiler tests
│       ├── test-cases.md # Description of test scenarios
│       └── ci-cd.md     # Framepiler CI/CD test procedures
│
├── extension/           # VS Code extension team's isolated space
│   ├── tests/           # Extension integration tests
│   ├── fixtures/        # Frame files for testing debugger
│   ├── mocks/           # Mock VS Code APIs
│   ├── scripts/         # Extension test runners
│   └── docs/            # Extension-specific test documentation
│       ├── README.md    # How to run extension tests
│       ├── debug-tests.md # Debugger test scenarios
│       └── docker-setup.md # Container test environment
│
└── common/              # Shared artifacts (read-only for tests)
    ├── builds/          # Published framec binaries
    │   ├── stable/      # Released versions (e.g., v0.81.5/)
    │   ├── nightly/     # Dev builds with timestamps
    │   └── wasm/        # WASM builds for browser testing
    ├── test-frames/     # Canonical Frame test files
    │   ├── basic/       # Simple test cases
    │   ├── advanced/    # Complex state machines
    │   └── edge-cases/  # Error conditions, boundary tests
    ├── schemas/         # Shared protocol definitions
    │   ├── dap/         # Debug Adapter Protocol schemas
    │   ├── frame/       # Frame language schemas
    │   └── runtime/     # Runtime protocol specifications
    └── docs/            # Shared documentation
        ├── README.md    # Overview of test environment
        ├── common-rules.md # Rules for common folder usage
        └── versioning.md # Version compatibility matrix
```

## Ownership and Responsibilities

### Framepiler Team Owns:
- `/framepiler/` - Complete control over their test space
- `/common/builds/` - Publishing new framec binaries
- `/common/test-frames/` - Maintaining canonical Frame test files
- `/framepiler/docs/` - Their test documentation

### Extension Team Owns:
- `/extension/` - Complete control over their test space
- `/extension/docs/` - Extension test documentation
- May contribute to `/common/test-frames/` for debugger-specific test cases

### Shared Ownership:
- `/common/schemas/` - Both teams collaborate on protocol definitions
- `/common/docs/` - Joint documentation for shared resources

## Common Folder Rules

1. **Read-Only During Tests**: Test suites should treat `/common/` as read-only
2. **Versioning Required**: All artifacts in `/common/builds/` must be versioned
3. **Append-Only Policy**: Never delete old versions (enables regression testing)
4. **Clear Documentation**: Each subfolder must have a README explaining:
   - What it contains
   - Who maintains it
   - How to add new content
   - Version compatibility

## Docker Integration Strategy

### Extension Team Docker Mounts:
```yaml
volumes:
  - ./test_env/extension:/workspace/tests:ro      # Their tests
  - ./test_env/common:/workspace/common:ro        # Shared resources
  # Note: NOT mounting framepiler/ - complete isolation
```

### Framepiler Team Docker Mounts:
```yaml
volumes:
  - ./test_env/framepiler:/workspace/tests:ro     # Their tests
  - ./test_env/common:/workspace/common:ro        # Shared resources
  # Note: NOT mounting extension/ - complete isolation
```

## Binary Version Management

### In `/common/builds/stable/`:
```
stable/
├── v0.81.5/
│   ├── darwin/
│   │   └── framec
│   ├── linux/
│   │   └── framec
│   ├── windows/
│   │   └── framec.exe
│   └── version.json     # Metadata about this release
├── v0.81.4/
│   └── ...
```

### In `/common/builds/nightly/`:
```
nightly/
├── 2024-12-08-abc123/    # Date + commit hash
│   ├── darwin/
│   │   └── framec
│   └── metadata.json     # Commit info, timestamp, features
```

## Test Data Sharing Strategy

### Canonical Test Frames (`/common/test-frames/`):
- **Purpose**: Standard Frame files both teams should handle correctly
- **Examples**:
  - `basic/hello_world.frm`
  - `basic/simple_state_machine.frm`
  - `advanced/multi_system.frm`
  - `edge-cases/syntax_errors.frm`
- **Maintenance**: Framepiler team maintains, extension team can propose additions

### Team-Specific Test Data:
- **Extension**: `/extension/fixtures/` for debugger-specific Frame files
- **Framepiler**: `/framepiler/fixtures/` for transpilation test cases

## Documentation Structure

### `/framepiler/docs/`:
- How to run transpiler tests
- Test case descriptions
- Performance benchmarks
- Language-specific testing guides

### `/extension/docs/`:
- VS Code extension test setup
- Docker test environment guide
- Debugger test scenarios
- Mock VS Code API documentation

### `/common/docs/`:
- Overall test environment structure
- Version compatibility matrix
- How to add new common resources
- CI/CD integration guides

## Migration Plan

### Phase 1: Create Directory Structure
```bash
mkdir -p framepiler/{tests,fixtures,scripts,docs}
mkdir -p extension/{tests,fixtures,mocks,scripts,docs}
mkdir -p common/{builds/{stable,nightly,wasm},test-frames/{basic,advanced,edge-cases},schemas/{dap,frame,runtime},docs}
```

### Phase 2: Move Existing Content
- Identify current test files and categorize by team
- Move to appropriate directories
- Update references in scripts

### Phase 3: Update Docker/CI Configurations
- Modify volume mounts to use new paths
- Update CI scripts to reference new structure
- Test isolation between environments

### Phase 4: Documentation
- Each team creates their `/*/docs/README.md`
- Document migration for existing users
- Update main repository READMEs

## Benefits of This Structure

1. **Complete Isolation**: Teams can't accidentally interfere with each other
2. **Clear Ownership**: No ambiguity about who maintains what
3. **Shared Resources**: Common artifacts available to both teams
4. **Version Control**: Can track changes to each team's area independently
5. **Docker-Friendly**: Clean volume mount boundaries
6. **CI/CD Ready**: Each team can have independent test pipelines
7. **Documentation**: Team-specific docs stay with team's tests

## Open Questions for Team Discussion

1. **VSIX Packages**: Should extension team publish `.vsix` files to `/common/builds/`?

2. **Performance Data**: Should we have `/common/benchmarks/` for performance baselines?

3. **Integration Tests**: Need a `/common/integration/` for cross-team contract tests?

4. **Access Control**: How to enforce read-only access to `/common/` during tests?

5. **Versioning Scheme**: How to handle version dependencies between teams?
   - Extension requires framec v0.81.5
   - Framepiler testing v0.82.0-dev
   - How to manage in `/common/builds/`?

6. **Cleanup Policy**: When can old versions in `/common/builds/` be archived/removed?

7. **Test Reports**: Should test results be shared in `/common/reports/`?

## Next Steps

1. Review this plan with both teams
2. Gather feedback and modify as needed
3. Create the directory structure
4. Migrate existing content
5. Update all references and documentation
6. Test isolation with both Docker setups

## Notes

- This structure assumes the test environment repository remains at `/Users/marktruluck/projects/framepiler_test_env/`
- Each team should maintain their own `.gitignore` rules in their directories
- Consider adding a top-level `Makefile` with targets like `make test-extension` and `make test-framepiler`