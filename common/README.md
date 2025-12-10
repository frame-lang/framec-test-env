# Common Resources Directory

This directory contains shared resources used by both the Framepiler (transpiler) and Extension (debugger) teams.

## Directory Structure

### `builds/`
Binary artifacts from both teams:
- `stable/` - Released versions of framec
- `nightly/` - Development builds with timestamps
- `wasm/` - WebAssembly builds for browser testing

**Ownership**: Framepiler team maintains framec binaries

### `test-frames/`
Canonical Frame test files that both teams should handle correctly:
- `basic/` - Simple test cases
- `advanced/` - Complex state machines  
- `edge-cases/` - Error conditions and boundary tests

**Ownership**: Framepiler team maintains, extension team can propose additions

### `schemas/`
Protocol and interface definitions:
- `dap/` - Debug Adapter Protocol schemas
- `frame/` - Frame language schemas
- `runtime/` - Runtime protocol specifications

**Ownership**: Joint - both teams collaborate

### `docker/`
Docker-related shared resources:
- `SEGREGATION_POLICY.md` - Rules for Docker namespace isolation
- `monitoring/` - Scripts to check for conflicts and resource usage
- `base-images/` - Optional shared base Docker layers

**Ownership**: Joint - both teams must follow segregation policy

### `docs/`
Shared documentation:
- Version compatibility matrices
- Integration guidelines
- Common testing procedures

**Ownership**: Joint - both teams contribute

## Usage Rules

1. **Read-Only During Tests**: Test suites should treat `/common/` as read-only
2. **Version Everything**: All artifacts must be versioned
3. **Never Delete**: Old versions should be preserved for regression testing
4. **Document Changes**: Update relevant README files when adding content

## Version Compatibility

See `docs/versioning.md` for the compatibility matrix between:
- framec versions
- Extension versions
- Runtime protocol versions

## Adding New Content

### To add a new framec binary:
```bash
# For stable releases
mkdir -p common/builds/stable/v{VERSION}/
cp framec common/builds/stable/v{VERSION}/

# For nightly builds
mkdir -p common/builds/nightly/$(date +%Y%m%d)-{COMMIT}/
cp framec common/builds/nightly/$(date +%Y%m%d)-{COMMIT}/
```

### To add a test frame:
1. Determine category (basic/advanced/edge-cases)
2. Add .frm file with descriptive name
3. Include comment header explaining what it tests
4. Update test inventory if one exists

## Monitoring

Check for Docker conflicts before running tests:
```bash
./docker/monitoring/check-conflicts.sh
```

## Contact

- Framepiler team: #frame-transpiler channel
- Extension team: #frame-debugger channel
- Conflicts: #frame-testing-conflicts channel