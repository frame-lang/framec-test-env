# Compile-Error Tests

Tests that verify certain Frame constructs **transpile successfully** but **fail to compile** in target languages.

## Purpose

These tests ensure that Frame V4's native pass-through correctly passes through
Frame-specific syntax verbatim, and that the target compiler correctly rejects it.

## Running

```bash
./run_tests.sh
```

Output is TAP (Test Anything Protocol) format for CI integration.

## Test Naming Convention

- `NN_description.{fc,fpy,fts,frs}` - Numbered tests by category
- Each test file contains a comment explaining what error is expected

## Current Tests

| Test | Description | Expected Error |
|------|-------------|----------------|
| 01_domain_frame_syntax | Frame `var x: type` in domain | Syntax error in all languages |

## Adding New Compile-Error Tests

1. Create test file with Frame construct that produces invalid native code
2. Add comment explaining expected compile error
3. Run `./run_tests.sh` to verify compilation fails correctly

## How It Works

For each test:
1. Transpile Frame → target language (should succeed)
2. Attempt to compile the generated code
3. **PASS** if compilation **fails** (expected)
4. **FAIL** if compilation **succeeds** (unexpected)
