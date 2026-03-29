# Frame V4 Test Suite

Test sources for Frame V4 language validation across 11 backends.

## Quick Start

```bash
./run_tests.sh              # Run ALL tests, all languages
./run_tests.sh --python     # Run only Python
./run_tests.sh --go         # Run only Go
./run_tests.sh --category primary  # Run only primary category
./run_tests.sh -v           # Verbose output
./run_tests.sh --help       # Show all options
```

## Supported Languages

| Flag | Extension | Target | Tests |
|------|-----------|--------|-------|
| `--python`, `--py` | `.fpy` | `@@target python_3` | 161 |
| `--typescript`, `--ts` | `.fts` | `@@target typescript` | 143 |
| `--javascript`, `--js` | `.fjs` | `@@target javascript` | 137 |
| `--rust`, `--rs` | `.frs` | `@@target rust` | 147 |
| `--c` | `.fc` | `@@target c` | 147 |
| `--cpp`, `--c++` | `.fcpp` | `@@target cpp_17` | 137 |
| `--java` | `.fjava` | `@@target java` | 133 |
| `--csharp`, `--cs` | `.fcs` | `@@target csharp` | 133 |
| `--go` | `.fgo` | `@@target go` | 133 |
| `--php` | `.fphp` | `@@target php` | 133 |
| `--kotlin`, `--kt` | `.fkt` | `@@target kotlin` | 133 |

**Total: ~1537 tests, all passing.**

## Test Structure Principles

### Common vs Language-Specific

```
tests/
├── common/                    # Tests that validate ALL languages
│   ├── positive/              # Transpile + compile + run = PASS
│   │   ├── primary/           # 49 core reference tests (01-51)
│   │   ├── automata/          # Mealy/Moore machines
│   │   ├── behavior_trees/    # AI agent pattern
│   │   ├── capabilities/      # Actions, operations, header defaults
│   │   ├── control_flow/      # Transitions, forwards, stack ops
│   │   ├── core/              # Basic compilation, snapshot
│   │   ├── data_types/        # Lists, dicts, strings, ints
│   │   ├── interfaces/        # Interface methods, params
│   │   ├── operators/         # Arithmetic, comparison, logical, ternary
│   │   ├── protocols/         # TCP connection pattern
│   │   ├── scoping/           # Function scope, shadowing
│   │   ├── segmenter/         # Universal parser tests
│   │   ├── systems/           # Multi-handler, nested systems
│   │   └── validator/         # Terminal statement validation
│   ├── compile-error/         # Expected transpile-time failures
│   ├── transpile-error/       # Expected transpile rejections
│   └── runtime-error/         # Expected runtime failures
│
├── python/                    # Python-specific tests
│   └── positive/              # Async, Python string handling
├── typescript/                # TypeScript-specific tests
│   └── positive/              # Async, type annotations
├── javascript/                # JavaScript-specific tests
│   └── positive/              # Async, ESM, template literals
├── rust/                      # Rust-specific tests
│   └── positive/              # Async, ownership patterns
├── c/                         # C-specific tests
│   └── positive/              # Smoke tests, string handling
├── cpp/                       # C++-specific tests
│   └── positive/              # Template literal handling
├── java/                      # Java-specific tests
│   └── positive/
├── csharp/                    # C#-specific tests
│   └── positive/
├── go/                        # Go-specific tests
│   └── positive/
├── php/                       # PHP-specific tests
│   └── positive/
└── kotlin/                    # Kotlin-specific tests
    └── positive/
```

### What goes in `common/`

A test belongs in `common/positive/` if and only if:
- The **Frame syntax** being tested is universal (transitions, state vars, HSM, etc.)
- The test can be **ported to every language** with only native code differences
- The test validates **Frame semantics**, not language-specific behavior

Every common test must have a file for every supported language (same base name, different extension).

### What goes in `<language>/`

A test belongs in a language-specific directory if:
- It tests a **language-specific feature** (async/await, template literals, ownership)
- It cannot be **meaningfully ported** to all languages
- It tests **scanner/parser behavior** specific to that language's string/comment syntax

Examples:
- `python/positive/async_basic.fpy` — async/await (only two-color languages)
- `c/positive/stack_ops.fc` — C-specific smoke tests
- `javascript/positive/frame_tokens_in_strings.fjs` — JS template literal scanner test

### Negative Tests

| Directory | What it tests |
|-----------|---------------|
| `common/compile-error/` | Frame syntax errors that ALL languages should reject |
| `common/transpile-error/` | Valid Frame that should produce transpilation errors |
| `common/runtime-error/` | Valid Frame that should fail at runtime |
| `<lang>/negative/` | Language-specific error cases |

### Rules

1. **Never skip tests** — debug and fix instead. Compare against working backends.
2. **No apostrophes in handler comments** — `can't` → `cannot` (lexer bug workaround)
3. **Frame statements on own lines** — `native(); -> $State` doesn't parse. Split to separate lines.
4. **Domain vars use target language syntax** — the domain section is native code.
5. **Test harness is native code** — `main()`, assertions, output are in the target language.
6. **`@@target` must match** — every test file needs the correct target pragma.

## Adding New Tests

### Universal Test (all languages)

Create one file per language in `common/positive/<category>/`:
```
common/positive/operators/my_test.fpy
common/positive/operators/my_test.fts
common/positive/operators/my_test.fjs
common/positive/operators/my_test.frs
...
```

The Frame syntax inside `@@system` should be identical. Only the native prolog/epilog/handler bodies differ.

### Language-Specific Test

Create in `<language>/positive/`:
```
python/positive/async_coroutines.fpy
```

### New Category

Just create the directory — the runner discovers it automatically:
```bash
mkdir -p common/positive/my_category
```

## Test Pass Criteria

A test **passes** if:
- Transpilation succeeds (exit 0)
- Compilation succeeds (compiled languages)
- Execution exit code is 0
- Output contains `ok` (TAP) or `PASS`
- Output contains no `not ok` or `FAIL`

## Output

Generated files are written to `output/<language>/tests/` (gitignored). These are regenerated by the test runner on each run.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRAMEC` | Path to framec binary | Auto-detected |
| `FRAMEPILER_TEST_ENV` | Test environment root | Auto-detected |
