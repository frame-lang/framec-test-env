# Frame V4 Test Architecture

## Overview

Frame V4 tests run in parallel Docker containers, one per target language. Each container mounts the shared test directory, discovers tests by file extension, compiles and runs them, and emits TAP (Test Anything Protocol) output.

## Directory Structure

```
framepiler_test_env/
├── tests/                   # Test source files
│   ├── common/              # Tests that pass in ALL 3 languages
│   │   ├── primary/         # 32 primary reference tests
│   │   ├── operators/       # Arithmetic, comparison, logical
│   │   ├── control_flow/    # If/else, while, try/catch
│   │   ├── core/            # Core language features
│   │   ├── capabilities/    # System return, persistence
│   │   ├── data_types/      # Lists, dicts, basic types
│   │   ├── exec_smoke/      # Execution smoke tests
│   │   ├── interfaces/      # Interface method tests
│   │   ├── scoping/         # Function scope, shadowing
│   │   ├── systems/         # State transitions, HSM, forwards
│   │   └── validator/       # Terminal transitions, stack ops
│   ├── python/              # Python-specific tests (.fpy)
│   ├── typescript/          # TypeScript-specific tests (.fts)
│   └── rust/                # Rust-specific tests (.frs)
├── output/                  # Generated code (build artifacts)
│   ├── python/tests/        # Compiled Python tests
│   ├── typescript/tests/    # Compiled TypeScript tests
│   └── rust/tests/          # Compiled Rust tests
├── docker/                  # Docker test infrastructure
│   ├── docker-compose.yml   # Main orchestration
│   ├── python/              # Python container config
│   ├── typescript/          # TypeScript container config
│   └── rust/                # Rust container config
├── bug/                     # Bug tracking system
│   ├── bugs/                # Bug files
│   ├── releases/            # Historical framec binaries
│   └── artifacts/           # Reproduction artifacts
├── docs/                    # This documentation
└── scripts/                 # Utility scripts
```

## File Extensions

| Extension | Language   | Container          |
|-----------|------------|--------------------|
| `.fpy`    | Python     | frame-python-runner|
| `.fts`    | TypeScript | frame-typescript-runner|
| `.frs`    | Rust       | frame-rust-runner  |

## Running Tests

### Docker (Recommended)
```bash
cd framepiler_test_env
docker compose -f docker/docker-compose.yml up --build
```

### Local - Primary Reference Tests
```bash
cd tests/common/primary
./run_tests.sh
```

### Local - All Tests
```bash
cd tests
./run_all_tests.sh
```

## Test Counts (2025-02-22)

| Language   | Tests | Status |
|------------|-------|--------|
| Python     | 147   | 100%   |
| TypeScript | 127   | 100%   |
| Rust       | 127   | 100%   |
| **Total**  | **401** | **100%** |

## Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host System                             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Python    │  │ TypeScript  │  │    Rust     │             │
│  │  Container  │  │  Container  │  │  Container  │             │
│  │             │  │             │  │             │             │
│  │ 1. Find     │  │ 1. Find     │  │ 1. Find     │             │
│  │    *.fpy    │  │    *.fts    │  │    *.frs    │             │
│  │ 2. Compile  │  │ 2. Compile  │  │ 2. Compile  │             │
│  │ 3. Run      │  │ 3. Run      │  │ 3. Run      │             │
│  │ 4. TAP out  │  │ 4. TAP out  │  │ 4. TAP out  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                         │
│              │   Shared Volume       │                         │
│              │   tests/ (read-only)  │                         │
│              └───────────────────────┘                         │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                         │
│              │   TAP Output          │                         │
│              │   (stdout per runner) │                         │
│              └───────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## TAP Output Format

Each test emits TAP (Test Anything Protocol) to stdout:

```tap
TAP version 14
1..3
ok 1 - lamp initializes in Off state
ok 2 - turnOn transitions to On state
not ok 3 - switch state after turnOff
  ---
  expected: false
  actual: true
  ---
```

### TAP Elements

| Element | Meaning |
|---------|---------|
| `1..N` | Plan: N tests will run |
| `ok N` | Test N passed |
| `not ok N` | Test N failed |
| `# comment` | Diagnostic info |
| `# SKIP` | Test skipped |
| `# TODO` | Test expected to fail |

## Container Workflow

### 1. Discovery
```bash
find /tests/common /tests/<language> -name "*.<ext>"
```

### 2. Compilation
```bash
framec compile -l <language> -o /tmp/out <test_file>
```

### 3. Execution
```bash
python3 /tmp/out/test.py        # Python
npx ts-node /tmp/out/test.ts    # TypeScript
cargo run --bin test            # Rust
```

### 4. Output
Test emits TAP to stdout. Container streams it through.

## Container Isolation

**Inside Container (ephemeral):**
- `/tmp/out/` - compiled output from framec
- Cargo target directories
- node_modules (baked into image)

**Mounted Read-Only from Host:**
- `tests/` - source test files only

**Output to Host:**
- TAP stream via stdout

When containers stop, all compilation artifacts disappear.

## Test File Structure

Each test file is a complete, standalone program:

```python
# example.fpy
@@target python

@@system Lamp {
    interface:
        turnOn()
        turnOff()
    machine:
        $Off {
            turnOn() { -> $On }
        }
        $On {
            turnOff() { -> $Off }
        }
}

if __name__ == "__main__":
    print("TAP version 14")
    print("1..2")
    lamp = Lamp()
    print("ok 1 - initial state" if lamp._state == "_sOff" else "not ok 1")
    lamp.turnOn()
    print("ok 2 - after turnOn" if lamp._state == "_sOn" else "not ok 2")
```

## Adding New Tests

1. **Universal tests** (pass in all 3 languages):
   - Add to `tests/common/<category>/`
   - Create all 3 extensions: `.fpy`, `.fts`, `.frs`

2. **Language-specific tests**:
   - Add to `tests/<language>/<category>/`
   - Use appropriate extension

3. Test must emit valid TAP to stdout

4. Test will be discovered automatically on next run

## CI Integration

TAP is widely supported:

| CI System | TAP Support |
|-----------|-------------|
| GitHub Actions | `tap-xunit` converts to JUnit XML |
| Jenkins | TAP Plugin |
| GitLab CI | Custom parser or JUnit conversion |

Example GitHub Actions:

```yaml
- name: Run Frame V4 Tests
  run: docker compose -f docker/docker-compose.yml up | tee results.tap

- name: Check Results
  run: grep -q "not ok" results.tap && exit 1 || exit 0
```

## Dependencies

### Host
- Docker
- docker-compose (or `docker compose`)

### Python Container
- Python 3.x
- framec binary

### TypeScript Container
- Node.js
- ts-node
- framec binary

### Rust Container
- Rust toolchain (rustc, cargo)
- framec binary
- serde (for persistence tests)

## Bug Tracking

The `bug/` directory contains:
- `bugs/` - Individual bug files with metadata
- `releases/` - Historical framec binaries for regression testing
- `artifacts/` - Reproduction artifacts

See `bug/README.md` for the tracking process.
