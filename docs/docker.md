# Docker Testing Guide

Run Frame tests in isolated containers with the correct toolchain for each language. The framec binary is mounted at runtime — swap binaries without rebuilding containers.

## Setup

### 1. Build Container Images

One-time setup (~5 minutes, mostly downloading base images):

```bash
cd docker/
FRAMEC_BIN=/dev/null docker compose build
```

### 2. Cross-Compile framec for Linux

Docker containers run Linux. On macOS, cross-compile the framec binary:

```bash
# ARM64 (Apple Silicon — most languages)
docker run --rm \
    -v "/path/to/framepiler:/src:ro" \
    -v "$(pwd):/out" \
    rust:latest \
    bash -c "cp -r /src /build && rm -rf /build/target && cd /build && \
             cargo build --release -p framec && \
             cp target/release/framec /out/framec-linux"

# x86_64 (needed for GDScript — Godot has no ARM64 build)
docker run --rm --platform linux/amd64 \
    -v "/path/to/framepiler:/src:ro" \
    -v "$(pwd):/out" \
    rust:latest \
    bash -c "cp -r /src /build && rm -rf /build/target && cd /build && \
             cargo build --release -p framec && \
             cp target/release/framec /out/framec-linux-x86"
```

ARM64 build: ~18 seconds. x86 build: ~72 seconds (Rosetta emulation).

## Running Tests

### Single Language

```bash
FRAMEC_BIN=$(pwd)/framec-linux docker compose run --rm python
```

### All Languages

```bash
for lang in python typescript javascript rust c cpp csharp java go php kotlin swift ruby erlang lua dart; do
    FRAMEC_BIN=$(pwd)/framec-linux docker compose run --rm $lang 2>/dev/null | grep "^# "
done

# GDScript (x86 binary)
FRAMEC_BIN=$(pwd)/framec-linux-x86 docker compose run --rm gdscript
```

### Compile-Only Mode

Skip execution, validate transpilation + compilation only:

```bash
FRAMEC_BIN=$(pwd)/framec-linux COMPILE_ONLY=true docker compose run --rm rust
```

### Comparing Two Binaries

```bash
FRAMEC_BIN=$(pwd)/framec-v1 docker compose run --rm python 2>/dev/null | grep "^# "
FRAMEC_BIN=$(pwd)/framec-v2 docker compose run --rm python 2>/dev/null | grep "^# "
```

## Debugging Failures

### Get a Shell

```bash
FRAMEC_BIN=$(pwd)/framec-linux docker compose run --rm --entrypoint bash python
```

### Manual Transpile + Run

Inside the container:

```bash
framec compile -l python_3 -o /tmp/out /tests/common/positive/primary/01_interface_return.fpy
python3 /tmp/out/01_interface_return.py
```

## How It Works

Each container mounts three volumes:

| Host | Container | Purpose |
|---|---|---|
| `FRAMEC_BIN` path | `/usr/local/bin/framec` | Transpiler (read-only) |
| `../tests/` | `/tests` | Test sources (read-only) |
| `../output/<lang>/` | `/output` | Build artifacts |

The shared `runners/runner.sh` handles all languages:

1. Discover test files by extension
2. Check `@@skip` / `@@xfail` markers
3. Transpile: `framec compile -l <target> -o /tmp/out <file>`
4. Compile (gcc, javac, cargo, etc.) if needed
5. Execute and check for PASS/FAIL
6. Emit TAP output

### Erlang Special Handling

Erlang generates `gen_statem` modules (no `main/0`). The runner:
1. Compiles with `erlc`
2. Auto-generates an escript that starts the process and calls exported methods
3. Runs the escript

## Rebuilding

```bash
# After changing runner.sh (all containers use it)
FRAMEC_BIN=/dev/null docker compose build

# After changing one Dockerfile
FRAMEC_BIN=/dev/null docker compose build --no-cache <lang>

# After changing framepiler source — just re-cross-compile, no container rebuild
```

## Container Dependencies

| Language | Base Image | Extra Packages |
|---|---|---|
| Python | `python:3.12-slim` | — |
| TypeScript | `node:20-slim` | ts-node, typescript, @types/node |
| JavaScript | `node:20-slim` | — |
| Rust | `rust:latest` | serde, serde_json, tokio |
| C | `gcc:14` | libcjson-dev |
| C++ | `gcc:14` | nlohmann-json3-dev |
| C# | `dotnet/sdk:8.0` | — |
| Java | `temurin:21-jdk` | json.jar (org.json) |
| Go | `golang:1.23` | — |
| PHP | `php:8.3-cli` | — |
| Kotlin | `temurin:21-jdk` | kotlinc, json.jar |
| Swift | `swift:5.10` | — |
| Ruby | `ruby:3.3-slim` | — |
| Erlang | `erlang:27` | — |
| Lua | `ubuntu:24.04` | lua5.4, luarocks, lua-cjson |
| Dart | `dart:3.4` | — |
| GDScript | `godot-ci:4.3` | x86_64 only |

## Known Limitations

- **GDScript**: `godot-ci` is x86_64 only. On ARM64 Macs, runs under Rosetta (~7 min). No native ARM64 Godot exists.
- **Kotlin**: ~5.5 min per run due to `kotlinc` JVM startup per test.
- **Alpine incompatibility**: The framec binary is dynamically linked against glibc. All containers use Debian/Ubuntu base images (not Alpine).
