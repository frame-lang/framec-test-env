# Transpile-Error Tests

Tests that verify certain **invalid Frame constructs** are **rejected by the transpiler**.

## Purpose

These tests ensure that the Frame transpiler correctly validates Frame syntax
and rejects invalid constructs with clear error messages.

## Running

```bash
./run_tests.sh
```

Output is TAP (Test Anything Protocol) format for CI integration.

## Test Naming Convention

- `description.{fc,fpy,fts,frs}` - Descriptive test names
- Each test file contains a comment explaining what error is expected

## Current Tests

| Test | Description | Expected Error |
|------|-------------|----------------|
| handler_outside_state | Handler defined outside state block | "handler must be inside a state block" |

## Adding New Transpile-Error Tests

1. Create test file with invalid Frame construct
2. Add comment explaining expected transpiler error
3. Run `./run_tests.sh` to verify transpilation fails correctly

## How It Works

For each test:
1. Attempt to transpile Frame source
2. **PASS** if transpilation **fails** (expected)
3. **FAIL** if transpilation **succeeds** (unexpected)

## Note

Some tests may currently fail because the transpiler doesn't yet validate
certain constructs. These tests document the expected behavior and will
pass once validation is implemented.
