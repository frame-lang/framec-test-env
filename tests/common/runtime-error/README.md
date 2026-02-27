# Runtime-Error Tests

Tests that verify certain Frame constructs **transpile and compile successfully** but **fail at runtime** with expected errors.

## Purpose

These tests ensure that Frame state machines correctly detect and report
runtime errors like invalid state transitions, assertion failures, etc.

## Running

```bash
./run_tests.sh
```

(Runner not yet implemented)

## Test Naming Convention

- `description.{fc,fpy,fts,frs}` - Descriptive test names
- Each test file contains a comment explaining what runtime error is expected

## Current Tests

(No tests yet)

## Adding New Runtime-Error Tests

1. Create test file that should fail at runtime
2. Add comment explaining expected runtime error
3. Add test to runner when implemented

## How It Works

For each test:
1. Transpile Frame → target language (should succeed)
2. Compile the generated code (should succeed)
3. Run the compiled program
4. **PASS** if runtime **fails** with expected error
5. **FAIL** if runtime **succeeds** (unexpected)
