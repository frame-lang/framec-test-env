# Frame V4 Test Suite

Reorganized test structure for Frame V4 language validation.

## Directory Structure

```
v4/
├── common/           # Tests that pass in ALL 3 languages (Python, TypeScript, Rust)
│   ├── primary/      # Primary reference tests (32 tests × 3 langs = 96 files)
│   ├── operators/    # Arithmetic, comparison, logical, ternary
│   ├── scoping/      # Function scope, nested functions, shadowing
│   ├── validator/    # Terminal transitions, stack ops, forwards
│   ├── core/         # Core language features
│   ├── control_flow/ # If/else, while, try/catch
│   ├── data_types/   # Lists, dicts, basic types
│   ├── capabilities/ # System return, persistence
│   ├── exec_smoke/   # Execution smoke tests
│   ├── interfaces/   # Interface method tests
│   └── systems/      # State transitions, HSM, forwards
│
├── python/           # Python-specific tests (use .fpy extension)
│   ├── async/        # Async/await (Python decorators)
│   ├── core/         # Python-specific syntax
│   └── ...
│
├── typescript/       # TypeScript-specific tests (use .fts extension)
│   ├── imports/      # TypeScript import syntax
│   ├── core/         # TypeScript-specific syntax
│   └── ...
│
├── rust/             # Rust-specific tests (use .frs extension)
│   ├── control_flow/ # Rust-specific control flow
│   └── ...
│
└── run_all_tests.sh  # Master test runner
```

## File Extensions

- `.fpy` - Python target
- `.fts` - TypeScript target
- `.frs` - Rust target

## Running Tests

### Primary Reference Tests (32 tests, all 3 languages)
```bash
cd common/primary
./run_tests.sh
```

### All Tests
```bash
./run_all_tests.sh
```

## Test Counts

| Category | Files |
|----------|-------|
| common/  | 393   |
| python/  | 15    |
| typescript/ | 7  |
| rust/    | 7     |

## Adding New Tests

1. **Universal tests** (pass in all 3 languages): Add to `common/<category>/` with all 3 extensions (.fpy, .fts, .frs)
2. **Language-specific tests**: Add to `<language>/<category>/` with the appropriate extension
