# Negative Tests

Tests that verify certain Frame constructs **fail** to compile in target languages.

## Purpose

These tests ensure that Frame V4's native pass-through correctly rejects
Frame-specific syntax that is not valid in the target language.

## Running

```bash
./run_negative_tests.sh
```

Output is TAP (Test Anything Protocol) format for CI integration.

## Test Naming Convention

- `NN_description.{fc,fpy,fts,frs}` - Numbered tests by category
- Each test file contains a comment explaining what error is expected

## Current Tests

| Test | Description | Expected Error |
|------|-------------|----------------|
| 01_domain_frame_syntax | Frame `var x: type` in domain | Syntax error in all languages |

## Adding New Negative Tests

1. Create test file with invalid Frame construct
2. Add comment explaining expected error
3. Run `./run_negative_tests.sh` to verify it fails correctly

## How It Works

For each test:
1. Transpile Frame → target language
2. Attempt to compile the generated code
3. **PASS** if compilation **fails** (expected)
4. **FAIL** if compilation **succeeds** (unexpected)
