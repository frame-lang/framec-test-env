# Frame Docker Test Runner (Rust)

A pure Rust implementation for running Frame transpiler tests in Docker containers. This replaces the previous Python-based harness with a faster, more maintainable Rust solution.

## Architecture

The Docker test runner is implemented entirely in Rust with no Python dependencies:

- **docker_executor.rs** - Core Docker execution logic
- **src/main.rs** - CLI application for running tests
- **run_docker_test.sh** - Shell script for individual test execution (called by Rust)
- **build.sh** - Build script for the Rust binary
- **run_tests.sh** - Convenience wrapper for running tests

## Building

```bash
# From this directory
./build.sh

# Or manually
cargo build --release
```

This creates the binary at `target/release/frame-docker-runner`.

## Usage

### Direct Binary Usage

```bash
# Run a specific category
./target/release/frame-docker-runner python_3 v3_data_types --framec ../../../target/release/framec

# With JSON output
./target/release/frame-docker-runner typescript v3_operators --json

# Verbose mode
./target/release/frame-docker-runner rust v3_systems -v
```

### Using the Wrapper Script

```bash
# Run Python tests
./run_tests.sh python v3_data_types

# Run TypeScript tests with verbose output  
./run_tests.sh typescript v3_operators --verbose

# Run Rust tests with JSON output
./run_tests.sh rust v3_systems --json
```

## Docker Images

The runner expects these Docker images to be available:
- `frame-transpiler-python:latest` - Python test environment
- `frame-transpiler-typescript:latest` - TypeScript/Node.js test environment
- `frame-transpiler-rust:latest` - Rust test environment

Build them using:
```bash
./build_images.sh
```

## Test Discovery

The runner automatically:
1. Finds test files in the shared environment (`common/test-frames/v3/`)
2. Filters tests by `@target` annotations
3. Transpiles using framec
4. Executes in appropriate Docker container
5. Reports results

## Language Support

- **Python**: Direct execution with frame_runtime_py mounted
- **TypeScript**: Compiles to JavaScript using esbuild, then executes with Node.js
- **Rust**: Compiles with rustc and executes the binary

## Environment Variables

- `FRAMEPILER_TEST_ENV` - Path to shared test environment (required)
- `FRAMEC_PATH` - Path to framec binary (defaults to `./target/release/framec`)

## Output Formats

### Human-Readable (default)
```
Running 3 tests for python/v3_data_types
============================================================
Running array_ops.frm... ✓ PASSED
Running dict_ops.frm... ✓ PASSED  
Running list_ops.frm... ✓ PASSED
============================================================
Summary for python/v3_data_types:
  3 Passed
  0 Failed
  Total: 3
============================================================
```

### JSON (with --json flag)
```json
{
  "language": "python_3",
  "category": "v3_data_types",
  "passed": 3,
  "failed": 0,
  "tests": [
    {
      "test": "array_ops.frm",
      "language": "python_3",
      "transpiled": true,
      "executed": true,
      "passed": true,
      "output": "...",
      "error": null,
      "duration_ms": 1234
    }
  ]
}
```

## Architecture Benefits

1. **No Python dependency** - Pure Rust implementation
2. **Fast execution** - Compiled binary vs interpreted Python
3. **Type safety** - Rust's type system prevents many errors
4. **Better error handling** - Result types and proper error propagation
5. **Consistent with transpiler** - Both transpiler and test runner in Rust

## Integration with CI

The runner exits with:
- 0 if all tests pass
- 1 if any test fails

This makes it suitable for CI/CD pipelines:

```yaml
- name: Run Docker tests
  run: |
    ./framepiler_test_env/framepiler/docker/run_tests.sh python v3_data_types
    ./framepiler_test_env/framepiler/docker/run_tests.sh typescript v3_data_types
    ./framepiler_test_env/framepiler/docker/run_tests.sh rust v3_data_types
```