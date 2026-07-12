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
| `primary/` | Core reference tests — interface, transitions, HSM, persistence, async |
| `core/` | Basic compilation and project structure |
| `control_flow/` | If/else, while, forwards, branching |
| `systems/` | Multi-handler, nested states |
| `capabilities/` | Actions, operations, system return |
| `interfaces/` | Interface method patterns |
| `system_params/` | System parameters and enter/exit args |
| `data_types/` | Lists, dicts, strings, type handling |
| `operators/` | Arithmetic, comparison, logical, ternary |
| `scoping/` | Variable scope, nested functions |
| `segmenter/` | Native code segmentation edge cases |
| `automata/` | Mealy/Moore machines |
| `behavior_trees/` | AI agent patterns |
| `fsm/` | `@@fsm` recognizers (RFC-0042): regex match stages, captures, Mode-C composition |
| `frame_machines/` | Broad `@@system` behavioral fixtures |
| `demos/` | End-to-end demo programs |
| `linux/`, `robotics/`, `scientific/`, `security/` | Cookbook / domain application suites |
| `max_coverage/` | Per-language maximal-surface fixtures |
| `validator/` | Validation edge cases |

(Run `ls tests/common/positive/` for the live list — categories are added per wave.)

Error tests live in separate directories — they assert that *invalid* input is
**rejected**, not silently miscompiled:

| Directory | What It Tests |
|---|---|
| `common/compile-error/` | Generated code that should fail to compile |
| `common/transpile-error/` | Frame source that `framec` should reject |
| `common/transpile-error/fsm/` | Invalid `@@fsm` rejected **with the right diagnostic code** (see below) |
| `common/runtime-error/` | Code that compiles but should fail at runtime |

### Negative `@@fsm` diagnostics (`transpile-error/fsm/`)

`@@fsm` validator diagnostics (E7xx) are raised before codegen and are
target-independent, so these fixtures run on **one** target (`python_3`), not
×17. Each declares its expectation in a header comment and a dedicated TAP
runner asserts framec fails with that exact code:

```
# expect-error: E732    → framec must fail AND the error must contain E732
# expect-ok             → framec must succeed (positive control)
```

Run `tests/common/transpile-error/fsm/check_fsm_diagnostics.sh`. See that
directory's [README](../tests/common/transpile-error/fsm/README.md) for the
covered codes and how to add a case.

## Coverage gate (`.skip.md`)

Every positive fixture stem must exist for all 16 backends — a real port
(`<stem>.f<ext>`) **or** a `<stem>.f<ext>.skip.md` placeholder documenting why
that backend is intentionally absent. `scripts/check_coverage.py` enforces this
(run it to list gaps). A `.skip.md` should name the concrete reason
(capability-matrix skip, language-shape constraint, single-target regression
net, etc.) — see [partial-coverage-audit.md](partial-coverage-audit.md).

## Verifying a fixture locally

`scripts/verify_local.sh` is the host-side counterpart to the Docker matrix:
give it one or more fixture files and it runs framec transpile → native
compile → run → PASS check for each, on the backend implied by the extension.

```bash
scripts/verify_local.sh tests/common/positive/data_types/dict_ops.frs
scripts/verify_local.sh tests/common/positive/primary/23_persist_basic.*   # whole stem
```

Unlike `run_single_test.sh` (Docker-oriented), it **provisions the per-language
deps** a bare host lacks — a serde+tokio cargo crate (rust), Jackson + org.json
(java/kotlin), a `net10.0` project (c#), coroutines (kotlin), and picks the
arm64 Homebrew `cjson`/`nlohmann` on Apple Silicon. A backend whose toolchain
or dep is genuinely missing is reported `SKIP` (not a false fail); Erlang is
`SKIP` (deprecated). Exit code is non-zero if any file fails, so it drops into
CI or a pre-push hook. Deps are cached under `output/.verify_local/`.

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
