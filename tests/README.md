# Frame V4 Test Suite

Test sources for Frame V4 language validation.

## Quick Start

```bash
# Run all tests
./run_tests.sh

# Run only Python tests
./run_tests.sh --python

# Run only a specific category
./run_tests.sh --category primary

# Verbose output
./run_tests.sh -v

# Compile only (no execution)
./run_tests.sh --compile-only

# Show help
./run_tests.sh --help
```

## Test Runner

**`run_tests.sh`** is the single, unified test runner. It dynamically discovers all tests based on directory structure - no configuration file needed.

### Command Line Options

| Option | Description |
|--------|-------------|
| `--python`, `--py` | Run only Python tests |
| `--typescript`, `--ts` | Run only TypeScript tests |
| `--rust`, `--rs` | Run only Rust tests |
| `--c` | Run only C tests |
| `--category NAME`, `-c NAME` | Run only tests in category NAME |
| `--verbose`, `-v` | Show detailed output on failures |
| `--compile-only` | Only transpile, don't execute |
| `--help`, `-h` | Show help |

### Examples

```bash
# Run all tests for all languages
./run_tests.sh

# Run only the primary reference tests
./run_tests.sh --category primary

# Run only TypeScript control_flow tests
./run_tests.sh --ts --category control_flow

# Compile only, useful for checking transpilation
./run_tests.sh --compile-only

# Debug a failing test with verbose output
./run_tests.sh -v --category primary --python
```

## Directory Structure

The directory structure IS the configuration. Tests are discovered automatically.

```
tests/
├── run_tests.sh          # THE test runner (use this!)
│
├── common/               # Tests for ALL languages
│   ├── primary/          # Core reference tests (36 tests)
│   ├── automata/         # Mealy/Moore machines
│   ├── capabilities/     # Actions, operations, persistence
│   ├── control_flow/     # If/else, while, forwards
│   ├── core/             # Core language features
│   ├── data_types/       # Lists, dicts, strings
│   ├── exec_smoke/       # Execution smoke tests
│   ├── interfaces/       # Interface methods
│   ├── operators/        # Arithmetic, comparison, logical
│   ├── scoping/          # Variable scoping
│   ├── systems/          # State machines, HSM
│   └── validator/        # Validation tests
│
├── python/               # Python-only tests
│   ├── async/
│   ├── capabilities/
│   ├── control_flow/
│   ├── core/
│   ├── data_types/
│   ├── interfaces/
│   └── systems/
│
├── typescript/           # TypeScript-only tests
│   ├── control_flow/
│   ├── core/
│   ├── imports/
│   └── systems/
│
├── rust/                 # Rust-only tests
│   └── control_flow/
│
└── c/                    # C-only tests
    └── (add categories as needed)
```

## File Extensions

| Extension | Language | Target Flag |
|-----------|----------|-------------|
| `.fpy` | Python | `@@target python_3` |
| `.fts` | TypeScript | `@@target typescript` |
| `.frs` | Rust | `@@target rust` |
| `.fc` | C | `@@target c` |

## Test Markers

Add markers in the first 10 lines of a test file to control behavior:

```frame
@@target python_3
// @@skip - Do not run this test
// @@xfail - Expected to fail (runs, counts as failure)
// @@timeout 60 - Custom timeout in seconds (default: 30)

@@system MyTest {
    ...
}
```

### Marker Reference

| Marker | Effect |
|--------|--------|
| `// @@skip` | Test is skipped entirely |
| `// @@xfail` | Test runs, expected to fail (counts as failure in reporting) |
| `// @@timeout N` | Override default 30-second timeout |

## Test Counts (2026-03-01)

| Scope | Python | TypeScript | Rust | C | Total |
|-------|--------|------------|------|---|-------|
| common/ | 129 | 120 | 123 | 139 | 511 |
| language-specific/ | 15 | 6 | 7 | 0 | 28 |
| **Total** | **144** | **126** | **130** | **139** | **539** |

**All 539 tests passing (100%)**

## Adding New Tests

### 1. Universal Test (all languages)

Create files in `common/<category>/`:
```
common/operators/my_new_test.fpy
common/operators/my_new_test.fts
common/operators/my_new_test.frs
common/operators/my_new_test.fc   # optional
```

### 2. Language-Specific Test

Create file in `<language>/<category>/`:
```
python/async/my_async_test.fpy
```

### 3. New Category

Just create the directory. The runner discovers it automatically:
```bash
mkdir -p common/my_new_category
# Add test files...
./run_tests.sh --category my_new_category
```

## Test Requirements

A test **passes** if its output contains the string `PASS`.

A test **fails** if:
- Transpilation fails
- Compilation fails (C, Rust)
- Execution fails
- Output does not contain `PASS`

### Example Test Structure

```frame
@@target python_3

@@system MyTest {
    interface:
        run_test(): void

    machine:
        $Start {
            run_test() {
                # Test logic here
                print("PASS: my test works")
            }
        }
}

if __name__ == "__main__":
    t = MyTest()
    t.run_test()
```

## Output Locations

Generated files are written to:

| Language | Output Directory |
|----------|------------------|
| Python | `output/python/tests/*.py` |
| TypeScript | `output/typescript/tests/*.ts` |
| Rust | `output/rust/tests/*.rs` |
| C | `output/c/tests/*.c` |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRAMEC` | Path to framec binary | `target/release/framec` |
| `FRAMEPILER_TEST_ENV` | Test environment root | Auto-detected |

## Troubleshooting

### Tests not discovered?
- Check file extension matches language (.fpy, .fts, .frs, .fc)
- Ensure file is in a category subdirectory, not directly in `common/`

### Test timing out?
- Add `// @@timeout 60` marker for longer timeout
- Check for infinite loops in test

### Need to skip a broken test?
- Add `// @@skip` marker temporarily
- Or `// @@xfail` if it's expected to fail (still counts as failure)
