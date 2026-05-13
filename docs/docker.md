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

## Reclaiming Disk (Docker has leaked again)

The matrix accumulates disk in three places that ordinary cleanup misses:

- **framec transpile cache** — `output/<lang>/.framec_cache/<framec_hash>/` accumulates
  a fresh per-fixture tar set every time framec is recompiled, with **no eviction**.
  C is the worst offender by far (~2.8 GB per cache generation due to fat per-fixture
  artifacts vs. ~5 MB elsewhere); on a busy month this reaches **100+ GB in C alone**.
  Almost always the biggest leak in this repo specifically — see the dedicated section
  below.
- **Build cache** — every `make framec` cross-compile dumps cache layers. On a busy
  week this reaches 10–20 GB with *zero* of it in use.
- **The Docker VM disk image** — on macOS, Docker Desktop stores everything
  (images, containers, volumes, cache) in a single sparse file:
  `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`
  (or `~/Library/Group Containers/group.com.docker/Data/vms/0/data/Docker.raw` on
  newer Docker Desktop). **This file grows but never shrinks.** `docker system prune`
  frees space *inside* it — your Mac's free space doesn't go up. Only deleting the
  `.raw` returns host disk.

`make clean` removes the framec binary, stamps, and test output. `make clean-images`
also runs `docker compose down --rmi all`. `make clean-cache` removes the framec
transpile caches. **None of these touch the Docker build cache or the `.raw` file** —
so a "still full" after `make clean-cache && make clean-images` is expected when the
real leak is the `.raw`.

### framec transpile cache (`output/*/.framec_cache`)

**The most common big-leak source in this repo.** Diagnose:

```bash
du -hxd 1 ~/projects/framec-test-env/output/*/.framec_cache 2>/dev/null | sort -hr
```

If any language exceeds ~5 GB, you have accumulation. C is almost always the leader.

**Why it leaks.** `docker/runners/framec_cached.sh` keys cache entries by
`(framec binary sha256, target lang, source file sha256)` and lays them out as
`output/<lang>/.framec_cache/<framec_hash>/<target>/<src_hash>.tar`. Every framec
rebuild creates a new `<framec_hash>` top-level dir; previous ones are kept
indefinitely.

The script has LRU eviction (keeps the `FRAMEC_CACHE_KEEP` most-recent framec
hashes per language; default 3). If you see runaway growth anyway, either the
eviction was disabled (`FRAMEC_CACHE_KEEP=0`) or you're on a checkout that
predates it — recover with:

```bash
cd docker && make clean-cache    # or rm -rf ../output/*/.framec_cache
```

**Why C is worst.** framec's C codegen produces substantially larger per-fixture
artifacts than other targets (~2.8 GB per cache generation across the 290-fixture
C corpus vs. ~5 MB for Python). Investigating the C codegen size is a separate
issue tracked in [_scratch/matrix_perf_proposal.md](../_scratch/matrix_perf_proposal.md).

### Diagnose

```bash
docker system df                                      # what's reclaimable inside Docker
df -h /System/Volumes/Data                            # host free space (the data volume)
du -sh ~/Library/Containers/com.docker.docker 2>/dev/null
du -sh "$HOME/Library/Group Containers/group.com.docker" 2>/dev/null   # newer Docker Desktop
```

`ls -lh Docker.raw` lies — it shows the sparse file's **apparent max** (often 1 TB),
not real usage. Use `du -sh` on the Containers dir for the actual on-disk number.

If `docker system df` shows little reclaimable but `du -sh` on the Containers dir is
huge, the `.raw` has bloated past its contents — only the nuke (step 5) recovers it.

### Playbook — least → most destructive

1. **Build cache** (the usual culprit; zero runtime impact, biggest cheap win):
   ```bash
   docker builder prune -af
   ```
2. **Stopped containers + dangling images** (safe, reversible):
   ```bash
   docker container prune -f && docker image prune -f
   ```
   Or, for the matrix stack specifically: `make clean-images` (or
   `docker compose -f docker/docker-compose.yml down --remove-orphans --volumes`).
3. **All unused images** (next `make build` re-pulls the 17 bases, ~a few GB):
   ```bash
   docker system prune -af
   ```
4. **Volumes too** (`docker volume ls` first — matrix runs are stateless, so normally fine):
   ```bash
   docker system prune -af --volumes
   ```
5. **Nuke the VM disk** — last resort. Steps 1–4 free space *inside* `Docker.raw`;
   this is the only thing that gives the space back to macOS.
   ```bash
   # 1. Quit Docker Desktop completely (not just the window — fully quit).
   # 2. Delete the disk image:
   rm ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw
   #    ...or, on newer Docker Desktop:
   rm "$HOME/Library/Group Containers/group.com.docker/Data/vms/0/data/Docker.raw"
   # 3. Launch Docker Desktop, wait for "Engine running".
   # 4. Rebuild: cd docker && FRAMEC_BIN=/dev/null docker compose build
   #    (then re-cross-compile framec per "Setup" above)
   ```
   Equivalent to Docker Desktop → Settings → Troubleshoot → "Clean / Purge data".
   **Cost:** ~20–30 min to rebuild all 17 images cold + ~3 min cold `make framec`
   cross-compile + a slower-than-usual first matrix run. **Lost:** nothing repo-side
   (Dockerfiles, source, test outputs all live on the host fs; runners are stateless)
   — but *any other Docker projects' images go too*, so check if the daemon serves
   anything besides this repo first. Typically reclaims 20–100 GB depending on
   accumulation.

### Non-Docker space, while you're at it

Past cleanups also found (none Docker-related): `~/Library/Caches/JetBrains` (~8 GB),
`~/Library/Developer/CoreSimulator` (~6 GB iOS sims — skip if you do iOS dev),
`~/Library/Caches/Google` (Chrome, ~6 GB — quit Chrome first), `~/Library/Developer/Xcode/Archives`
(~5 GB), `~/Library/Caches/Raspberry Pi` (~3 GB if you've used RPi Imager),
`~/Library/Caches/*.ShipIt` (~2 GB of stale auto-updater downloads from
VSCode/Claude/Discord/Postman), `brew cleanup --prune=all` (~250 MB), and
per-project `target/` dirs (3–4 GB each — `cargo clean` in any repo you're not
actively building).

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
