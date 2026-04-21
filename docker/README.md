# Frame Test Environment — Docker Infrastructure

Dockerized test infrastructure for validating the Frame transpiler (`framec`) across all 17 target language backends. Each language runs in its own isolated container with the correct toolchain. The `framec` binary is mounted at runtime — never baked into images.

## Quick Start

```bash
cd docker/

# Build all container images (one-time, ~5 min)
FRAMEC_BIN=/dev/null docker compose build

# Cross-compile framec for Linux (required on macOS)
./run.sh --build-framec /path/to/framepiler/repo

# Run all 17 languages
./run.sh ./framec-linux

# Run a single language
./run.sh ./framec-linux python

# Run with clean output (removes stale artifacts first)
./run.sh --clean ./framec-linux

# Compare two framec binaries
./run.sh --compare ./framec-old ./framec-new
```

## Architecture

### Principle: Mount, Don't Bake

Container images contain **only the language toolchain**. The `framec` binary and test files are mounted as Docker volumes at runtime. This means:

- Swap any framec binary without rebuilding containers
- Container images are built once, reused indefinitely
- Two binaries can be tested in parallel via compose projects

### Why a Linux Binary?

Docker containers run Linux. On macOS (Apple Silicon), the `framec` binary must be cross-compiled for `linux/arm64`. The `run.sh` orchestrator can do this automatically:

```bash
./run.sh --build-framec /path/to/framepiler/source
```

This builds inside a `rust:latest` Docker container and produces `framec-linux`. The build takes ~30 seconds and the result is cached.

**Why not WASM?** The framec CLI (`cli.rs`) uses filesystem I/O, process management, and argument parsing that don't exist in WASM. The WASM entry point (`lib.rs`) exposes only `run(source, format) -> string` — it can't replace the CLI. A Node.js wrapper would add complexity and 10-20x performance overhead with no benefit.

### Container Design

Each of the 17 containers:
1. Starts from the official language base image
2. Installs compile/run dependencies
3. Copies the shared `runner.sh` test script
4. Mounts `framec` binary, test files, and output directory at runtime

### Test Execution Flow

Per container, the `runner.sh` script:
1. Discovers test files: `find /tests/common/positive -name "*.<ext>"`
2. For each test file:
   - Check `@@skip` / `@@xfail` markers
   - **Transpile**: `framec compile -l <target> -o /tmp/out <test_file>`
   - **Compile** (if needed): gcc, javac, kotlinc, etc.
   - **Execute**: Run the generated code
   - Check output for PASS/FAIL
3. Emit TAP (Test Anything Protocol) output
4. Exit with failure count

### Parallel Execution

All containers launch simultaneously via `docker compose up -d`. The `collect-results.sh` script polls until every container exits, then reads per-service logs via `docker compose logs --no-log-prefix <service>` to extract TAP results without interleaving. A summary report lists per-language pass/fail counts, with all failure lines grouped at the end.

All 17 containers share the same mounted `framec` binary. The GDScript image runs natively on both ARM64 and x86_64 (Godot 4.6.2 ships linux.arm64 + linux.x86_64 builds; see `docker/base/gdscript/Dockerfile`).

```bash
# Via Makefile (recommended):
make test          # 16 native-arch languages in parallel
make test-all      # All 17 including GDScript
make test-python   # Single language (sequential, for debugging)
```

## Container Reference

### Stable Backends (9 languages)

| Language | Base Image | Compile | Execute | Time |
|----------|-----------|---------|---------|------|
| Python | `python:3.12-slim` | — | `python3 file.py` | ~3s |
| TypeScript | `node:20-slim` | — | `ts-node file.ts` | ~77s |
| JavaScript | `node:20-slim` | — | `node file.mjs` | ~4s |
| Rust | `rust:latest` | `cargo build` | binary | ~23s |
| C | `gcc:14` | `gcc -lcjson` | binary | ~5s |
| C++ | `gcc:14` | `g++ -std=c++23` | binary | ~43s |
| C# | `dotnet/sdk:8.0` | `dotnet build` | `dotnet run` | ~69s |
| Java | `temurin:21-jdk` | `javac` | `java Main` | ~40s |
| Go | `golang:1.23` | — | `go run` | ~13s |

### Experimental Backends (8 languages)

| Language | Base Image | Compile | Execute | Time |
|----------|-----------|---------|---------|------|
| PHP | `php:8.3-cli` | — | `php file.php` | ~2s |
| Kotlin | `temurin:21-jdk` + kotlinc | `kotlinc -include-runtime` | `java -jar` | ~5m30s |
| Swift | `swift:5.10` | — | `swift file.swift` | ~19s |
| Ruby | `ruby:3.3-slim` | — | `ruby file.rb` | ~5s |
| Erlang | `erlang:27` | `erlc` | `escript run_test.escript` | ~4s |
| Lua | `ubuntu:24.04` + lua5.4 | — | `lua file.lua` | ~2s |
| Dart | `dart:3.4` | — | `dart run` | ~varies |
| GDScript | `ubuntu:24.04` + Godot 4.6.2 | — | `godot --headless` | ~5s* |

*GDScript: native ARM64 image built from source (`docker/base/gdscript/`)
**Erlang: the per-test escript driver (auto-generated in `erlang_batch.sh`) calls each interface export with dummy args and reports `ok` if none crash — semantic correctness is checked via pattern-match assertions inside the test source, which fault the runtime if a Frame guarantee regresses.

### Dependencies

- **Java/Kotlin**: `json-20231013.jar` (org.json) downloaded at build time for persist tests
- **C**: `libcjson-dev` for JSON serialization
- **C++**: `nlohmann-json3-dev` for JSON serialization
- **TypeScript**: `ts-node`, `typescript`, `@types/node` globally installed
- **Lua**: `lua-cjson` via luarocks

## Files

```
docker/
├── Makefile                    # Build orchestration, parallel test targets
├── docker-compose.yml          # 17 services, parameterized FRAMEC_BIN
├── collect-results.sh          # Waits for parallel containers, collects TAP results
├── run.sh                      # Orchestrator: clean, run, compare
├── framec-native               # Cached native-arch Linux binary (gitignored)
├── README.md                   # This file
├── base/                       # One Dockerfile per language
│   ├── python/Dockerfile
│   ├── typescript/Dockerfile
│   ├── javascript/Dockerfile
│   ├── rust/Dockerfile
│   ├── c/Dockerfile
│   ├── cpp/Dockerfile
│   ├── csharp/Dockerfile
│   ├── java/Dockerfile
│   ├── go/Dockerfile
│   ├── php/Dockerfile
│   ├── kotlin/Dockerfile
│   ├── swift/Dockerfile
│   ├── ruby/Dockerfile
│   ├── erlang/Dockerfile
│   ├── lua/Dockerfile
│   ├── dart/Dockerfile
│   └── gdscript/Dockerfile
└── runners/
    └── runner.sh               # Shared test runner (TAP output)
```

## Known Issues

1. **Kotlin was slow (~5m30s)** historically because `kotlinc` has significant JVM startup per test. Now mitigated by `kotlin_batch.sh` — all `.kt` files in a test set are compiled together into a single JAR and dispatched by a pre-built `TestRunner.jar`. Total Kotlin runtime ~50s.

2. **Alpine images incompatible**: The mounted `framec` binary is dynamically linked against glibc. Alpine images (which use musl) can't execute it. All containers use Debian/Ubuntu base images.

3. **Java async** uses `CompletableFuture` (no native async/await); callers `.get()` to await. **C++ async** uses a generated `FrameTask<T>` coroutine promise and needs `-std=c++23` (or ≥ `c++20`). See `docs/framepiler_design.md § Async Dispatch Per Language` in the framepiler repo for the per-language model.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FRAMEC_BIN` | Path to Linux framec binary (native arch) | Required |
| `COMPILE_ONLY` | Skip execution, transpile+compile only | `false` |

## Adding a New Language

1. Create `base/<lang>/Dockerfile` with the language toolchain
2. Add a case to `runners/runner.sh` for the compile and execute steps
3. Add a service to `docker-compose.yml`
4. Rebuild: `FRAMEC_BIN=/dev/null docker compose build <lang>`
