# Frame V4 Test Architecture

## Overview

Frame V4 tests run in parallel Docker containers, one per target language. Each container mounts the shared test directory, discovers tests by file extension, compiles and runs them, and emits TAP (Test Anything Protocol) output.

## Directory Structure

```
framepiler_test_env/
├── tests/               # Test source files
│   ├── common/          # Tests that pass in ALL 3 languages
│   │   ├── primary/     # 32 primary reference tests
│   │   ├── operators/   # Arithmetic, comparison, logical
│   │   ├── control_flow/# If/else, while, try/catch
│   │   ├── core/        # Core language features
│   │   └── ...
│   ├── python/          # Python-specific tests
│   ├── typescript/      # TypeScript-specific tests
│   └── rust/            # Rust-specific tests
├── output/              # Generated code (build artifacts)
│   ├── python/tests/
│   ├── typescript/tests/
│   └── rust/tests/
├── docker/              # Docker test runners
└── docs/                # This documentation
```

## File Extensions

| Extension | Language   | Container        |
|-----------|------------|------------------|
| `.fpy`    | Python     | python-runner    |
| `.fts`    | TypeScript | typescript-runner|
| `.frs`    | Rust       | rust-runner      |

## Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host System                              │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Python    │  │ TypeScript  │  │    Rust     │              │
│  │  Container  │  │  Container  │  │  Container  │              │
│  │             │  │             │  │             │              │
│  │ 1. Find     │  │ 1. Find     │  │ 1. Find     │              │
│  │    *.fpy    │  │    *.fts    │  │    *.frs    │              │
│  │ 2. Compile  │  │ 2. Compile  │  │ 2. Compile  │              │
│  │ 3. Run      │  │ 3. Run      │  │ 3. Run      │              │
│  │ 4. TAP out  │  │ 4. TAP out  │  │ 4. TAP out  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                       │
│                          ▼                                       │
│              ┌───────────────────────┐                          │
│              │   Shared Volume       │                          │
│              │   tests/     │                          │
│              └───────────────────────┘                          │
│                          │                                       │
│                          ▼                                       │
│              ┌───────────────────────┐                          │
│              │   TAP Aggregator      │                          │
│              │   (merge 3 streams)   │                          │
│              └───────────────────────┘                          │
│                          │                                       │
│                          ▼                                       │
│              ┌───────────────────────┐                          │
│              │   Final Report        │                          │
│              └───────────────────────┘                          │
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
| `---` / `...` | YAML block for structured diagnostics |
| `# SKIP` | Test skipped |
| `# TODO` | Test expected to fail |

### Example Test Output

```tap
TAP version 14
1..2
ok 1 - arithmetic addition
ok 2 - arithmetic subtraction
```

## Container Isolation

All temporary files stay inside the container. The host remains clean.

**Inside Container (ephemeral):**
- `/tmp/out/` - compiled output from framec
- Cargo target directories
- node_modules (baked into image)
- Any logs or intermediate files

**Mounted Read-Only from Host:**
- `tests/` - source test files only

**Output to Host:**
- TAP stream via stdout (captured by docker-compose)

When containers stop, all compilation artifacts disappear. Only the TAP output is retained.

## Container Workflow

Each container performs these steps:

### 1. Discovery
```bash
# Find tests for this language
find /tests/common /tests/<language> -name "*.<ext>"
```

### 2. Compilation
```bash
# Compile Frame source to target language
framec compile -l <language> -o /tmp/out <test_file>
```

### 3. Execution
```bash
# Run compiled test
python3 /tmp/out/test.py        # Python
npx ts-node /tmp/out/test.ts    # TypeScript
cargo run --bin test            # Rust
```

### 4. Output
Test subprocess emits TAP to stdout. Container streams it through.

## Parallelism

All three containers run simultaneously:

```bash
docker-compose up
```

Each container:
- Mounts `tests/` read-only
- Has framec binary available
- Has language runtime installed
- Outputs TAP stream to stdout

## Result Aggregation

TAP streams from all containers are merged using `tap-merge` or equivalent:

```bash
docker-compose up | tap-merge | tap-summary
```

Or capture individually:

```bash
docker logs python-runner > python.tap
docker logs typescript-runner > typescript.tap
docker logs rust-runner > rust.tap
tap-merge *.tap > combined.tap
```

## Test File Structure

Each test file is a complete, standalone program:

```python
# example.fpy
@@target python_3

@@system Lamp {
    machine:
        $Off {
            turnOn() { -> $On }
        }
        $On {
            turnOff() { -> $Off }
        }
}

# TAP output
def main():
    lamp = Lamp()
    print("TAP version 14")
    print("1..2")

    # Test 1
    if lamp.state == "Off":
        print("ok 1 - initial state is Off")
    else:
        print("not ok 1 - initial state is Off")

    # Test 2
    lamp.turnOn()
    if lamp.state == "On":
        print("ok 2 - turnOn transitions to On")
    else:
        print("not ok 2 - turnOn transitions to On")

if __name__ == "__main__":
    main()
```

## Adding New Tests

1. Create test file with appropriate extension:
   - `common/<category>/test_name.fpy` + `.fts` + `.frs` for universal tests
   - `<language>/<category>/test_name.<ext>` for language-specific tests

2. Test must emit valid TAP to stdout

3. Test will be discovered and run automatically on next container execution

## CI Integration

TAP is widely supported:

| CI System | TAP Support |
|-----------|-------------|
| GitHub Actions | `tap-xunit` converts to JUnit XML |
| Jenkins | TAP Plugin |
| GitLab CI | Custom parser or JUnit conversion |
| CircleCI | JUnit conversion |

Example GitHub Actions:

```yaml
- name: Run Frame V4 Tests
  run: docker-compose up | tee results.tap

- name: Convert TAP to JUnit
  run: cat results.tap | tap-xunit > results.xml

- name: Publish Results
  uses: mikepenz/action-junit-report@v3
  with:
    report_paths: results.xml
```

## Dependencies

### Host
- Docker
- docker-compose
- tap-merge (optional, for aggregation)

### Python Container
- Python 3.x
- framec binary

### TypeScript Container
- Node.js
- npx / ts-node
- framec binary

### Rust Container
- Rust toolchain (rustc, cargo)
- framec binary
- serde (for persistence tests)
