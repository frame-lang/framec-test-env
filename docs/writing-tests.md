# Writing Tests

## Test File Structure

Each test is a Frame source file with a language-specific extension. A test file contains:

1. `@@target <lang>` pragma
2. `@@system` block defining the state machine
3. Native epilog code that instantiates the system, exercises it, and reports PASS/FAIL

### Example (Python)

```
@@target python_3

@@system Counter {
    interface:
        increment()
        get_count(): int

    machine:
        $Active {
            increment() {
                self.count = self.count + 1
            }
            get_count(): int {
                @@:(self.count)
                return
            }
        }

    domain:
        count = 0
}

def main():
    s = @@Counter()
    s.increment()
    s.increment()
    result = s.get_count()
    assert result == 2, f"Expected 2, got {result}"
    print("PASS: Counter works")

if __name__ == '__main__':
    main()
```

The native code after the `}` closing the `@@system` block passes through the transpiler unchanged. It's real Python (or TypeScript, Rust, etc.) that tests the generated state machine.

## File Extensions

Each language has its own extension. The same test logic exists as separate files per language:

```
tests/common/positive/primary/
├── 01_interface_return.fpy     # Python
├── 01_interface_return.fts     # TypeScript
├── 01_interface_return.fjs     # JavaScript
├── 01_interface_return.frs     # Rust
├── 01_interface_return.fc      # C
├── 01_interface_return.fcpp    # C++
├── 01_interface_return.fcs     # C#
├── 01_interface_return.fjava   # Java
├── 01_interface_return.fgo     # Go
├── 01_interface_return.fphp    # PHP
├── 01_interface_return.fkt     # Kotlin
├── 01_interface_return.fswift  # Swift
├── 01_interface_return.frb     # Ruby
├── 01_interface_return.ferl    # Erlang
├── 01_interface_return.flua    # Lua
├── 01_interface_return.fdart   # Dart
└── 01_interface_return.fgd     # GDScript
```

## Test Categories

Tests are organized under `tests/common/positive/`:

| Category | Description |
|---|---|
| `primary/` | Core reference tests — interface, transitions, HSM, persistence |
| `automata/` | Mealy/Moore machines |
| `behavior_trees/` | AI agent patterns |
| `capabilities/` | Actions, operations, system return |
| `control_flow/` | If/else, while, forwards, branching |
| `core/` | Basic compilation and project structure |
| `data_types/` | Lists, dicts, strings, type handling |
| `interfaces/` | Interface method patterns |
| `operators/` | Arithmetic, comparison, logical, ternary |
| `protocols/` | Protocol patterns |
| `scoping/` | Variable scope, nested functions |
| `segmenter/` | Native code segmentation edge cases |
| `systems/` | Multi-handler, nested states |
| `validator/` | Validation edge cases |

Error tests live in separate directories:

| Directory | What It Tests |
|---|---|
| `common/compile-error/` | Generated code that should fail to compile |
| `common/transpile-error/` | Frame source that `framec` should reject |
| `common/runtime-error/` | Code that compiles but should fail at runtime |

## Markers

Place in the first 10 lines of a test file:

```
// @@skip       — Skip this test entirely
// @@xfail     — Expected to fail (runs but counted as known failure)
// @@timeout 60 — Custom timeout in seconds (default: 30)
```

## Native Epilog Patterns

### Scripted Languages (Python, JS, TS, PHP, Ruby, Lua, Dart, GDScript)

Instantiate with `@@SystemName()`, call methods directly:

```python
s = @@MySystem()
result = s.some_method(arg1, arg2)
assert result == expected
print("PASS")
```

### Compiled Languages (Rust, C, C++, Java, C#, Go, Kotlin, Swift)

Same pattern but with language-specific syntax. The `@@SystemName()` is expanded by the transpiler.

### Erlang

Erlang is a special case. The generated code is a `gen_statem` module — there's no inline instantiation. The Docker test runner auto-generates an escript harness that starts the process and calls exported methods. No epilog code needed in `.ferl` files (though adding one is possible for complex assertions).

## PASS/FAIL Convention

Tests should print output that the runner can detect:

- **PASS**: Print `PASS` or TAP `ok N - description`
- **FAIL**: Print `FAIL`, throw/panic/exit with non-zero, or TAP `not ok N - description`
- **Clean exit with no output**: Treated as PASS (transpile + compile + run succeeded)
