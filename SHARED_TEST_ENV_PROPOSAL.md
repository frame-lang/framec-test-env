# Framepiler Shared Test Environment Proposal

**Scope**  
Shared, hermetic test environment for the Frame Transpiler (PT) team and Debugger Adapter (DAP) team, focused on V3 TypeScript systems (e.g., AdapterProtocol) while remaining extensible to Python and other targets.

**Goals**
- Make adapter‑level semantics (guard/deferral, ready/handshake, stopped state) reproducible on any machine with the same commands.
- Eliminate drift between:
  - PT’s V3 tests (`framec_tests` in the main repo), and
  - DAP’s external validator scripts (e.g., `/tmp/frame_transpiler_repro/bug_081/run_validate.sh`).
- Keep the shared environment self‑contained and versioned, with minimal external dependencies beyond:
  - A `framec` binary from the PT repo.
  - A Node + `tsc` toolchain.

---

## 1. Repository Layout (This Folder)

This directory (`framepiler_test_env`) is the shared home for adapter‑level integration tests. Proposed structure:

```text
framepiler_test_env/
  README.md                     # High-level overview + quickstart
  SHARED_TEST_ENV_PROPOSAL.md   # This document

  adapter_protocol/
    adapter_protocol_minimal.frm    # Minimal in-tree FRM capturing core semantics
    adapter_protocol_full.frm       # (optional) Full AdapterProtocol, if desired

    tsconfig.json                   # Pinned TS config for tests
    package.json                    # Local dev deps (typescript, @types/node, etc.)

    runtime/
      frame_runtime_ts.d.ts         # Copied or symlinked from PT repo

    scripts/
      run_adapter_smoke.sh          # High-level CLI entrypoint for both teams
      node_harness.ts               # Node test driver (guard/deferral/stopped)

  docker/
    Dockerfile                      # Optional containerized test shell
    docker-compose.yml              # (optional) if multi-service is needed later
```

Key principles:
- **No absolute `/Users/...` paths** in test scripts. Everything is relative to this repo and/or accepts an environment variable (e.g., `FRAMEC_BIN`).
- **Runtime + types** come from the PT repo (or a package built from it), but are exposed here in a stable, importable way.

---

## 2. Single Source of Truth for Runtime and Types

To avoid the environment-specific failure we saw in Bug #081 (TS2580 errors on `require`/`process` because a local `frame_runtime_ts/index.ts` was compiled without Node typings):

**Proposal**
- Treat the PT repo’s `frame_runtime_ts` as canonical:
  - Implementation: `frame_runtime_ts/index.ts`.
  - Types: `frame_runtime_ts/index.d.ts`.
- In this shared env:
  - Add `@types/node` and `typescript` to `devDependencies` in `adapter_protocol/package.json`.
  - Use a `tsconfig.json` that:
    - Targets the agreed runtime (e.g., `"target": "es2019", "module": "commonjs"`).
    - Includes `"types": ["node"]` or `"lib": ["ES2019"]` as needed.
  - Compile *generated adapter TS* against:
    - The published `frame_runtime_ts` `.d.ts` (preferably), or
    - The runtime implementation plus `@types/node` if the implementation is part of the compilation unit.

**Impact**
- Both PT and DAP teams see the *same* runtime surface in TypeScript.
- No validator relies on whatever happens to be in `~/vscode_editor/frame_runtime_ts`.

---

## 3. Minimal AdapterProtocol Fixture (FRM)

Instead of only using the full external `AdapterProtocol.frm`, this env should define a **minimal, self-contained fixture** that still exercises the critical semantics:

**`adapter_protocol_minimal.frm` (example sketch)**
- System with:
  - `interface:` methods for:
    - `start()`, `runtimeConnected()`, `runtimeMessage(payload)`, `enqueueCommand(action, data)`, `drainCommands()`.
  - `machine:` logic that encodes:
    - Guarded commands that defer until `ready`.
    - A single in-flight command rule.
    - `stopped` event updates (`isPaused`, `lastStoppedReason`, `lastThreadId`).
  - `actions:` helpers to manipulate the queue and flags.
  - `domain:` fields for:
    - `commandQueue`, `pendingAction`, `isPaused`, `lastStoppedReason`, `lastThreadId`.

This fixture should live in **both**:
- This shared repo (`framepiler_test_env/adapter_protocol/adapter_protocol_minimal.frm`), and
- The PT repo (under `framec_tests/language_specific/typescript/v3_cli/`), to keep both sides in sync.

---

## 4. Node Harness and Test Execution

The current `/tmp` validator for Bug #081 is essentially:
- Compile FRM → TS via `framec`.
- Compile TS → JS via `tsc`.
- Run a Node script that:
  - Constructs `AdapterProtocol`.
  - Drives a scenario:
    - `start()` → drain → expect empty.
    - `runtimeConnected()` → drain → expect `initialize` + `ping`.
    - Guarded command before ready → expect deferral.
    - `hello/ready` + `continue` → expect single in-flight.
    - `stopped` → expect `isPaused === true`.

**Proposal**
- Move that logic into this shared env as `adapter_protocol/scripts/node_harness.ts` and a small shell wrapper:
  - `run_adapter_smoke.sh`:
    ```bash
    #!/usr/bin/env bash
    set -euo pipefail
    FRAMEC_BIN="${FRAMEC_BIN:-/path/to/framec}"
    OUT_DIR="$(mktemp -d)"

    # 1) Generate TS from FRM (from this repo)
    "$FRAMEC_BIN" compile -l typescript -o "$OUT_DIR" adapter_protocol_minimal.frm

    # 2) Compile TS -> JS via local tsconfig
    (cd "$(dirname "$0")/.." && npx -y tsc -p tsconfig.json --project "$OUT_DIR")

    # 3) Run Node harness
    OUT_JS="$OUT_DIR/out/adapter_protocol_minimal.js" \
      node scripts/node_harness.js
    ```
- Ensure the harness:
  - Requires the generated JS via `OUT_JS`.
  - Logs a simple, stable marker (e.g., `ADAPTER_SMOKE_OK`) on success.

**Both teams** can then:
- Run `adapter_protocol/scripts/run_adapter_smoke.sh` locally.
- Integrate the same script into their CI (PT’s and DAP’s).

---

## 5. Integration with the PT Repo (`frame_transpiler`)

To keep this env and the main repo in sync:

1. **FRM Fixtures**
   - Mirror `adapter_protocol_minimal.frm` into `framec_tests/language_specific/typescript/v3_cli/adapter_protocol_minimal.frm`.
   - Add a v3_cli test with `@tsc-compile` and optional runtime assertions.

2. **Runtime + Types**
   - Either:
     - Treat `framepiler_test_env/adapter_protocol/runtime/frame_runtime_ts.d.ts` as generated by the PT repo (e.g., via a script), or
     - Consume the PT repo’s runtime as an npm package (`frame_runtime_ts`), with this env pinned to a specific version.

3. **Shared Commands**
   - Document a small set of canonical commands (e.g., in `README.md` in both repos):
     - `frame_transpiler` repo:
       - `python3 framec_tests/runner/frame_test_runner.py --languages typescript --categories v3_cli --framec ./target/release/framec --transpile-only`
     - `framepiler_test_env` repo:
       - `FRAMEC_BIN=../frame_transpiler/target/release/framec ./adapter_protocol/scripts/run_adapter_smoke.sh`

This ensures:
- The same FRM and runtime surface are tested in both places.
- Failures can be reproduced from either repo with identical commands.

---

## 6. Optional: Containerized Test Shell

For long‑term stability across machines and CI providers:

**Dockerfile (outline)**
```dockerfile
FROM node:20-bullseye

RUN apt-get update && apt-get install -y python3 python3-pip rustc cargo && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . /workspace

RUN npm install --prefix adapter_protocol

CMD ["bash"]
```

**Usage**
- Build: `docker build -t framepiler-test-env ./docker`
- Run:
  ```bash
  docker run --rm -it \
    -v /Users/marktruluck/projects/frame_transpiler:/frame_transpiler \
    -v /Users/marktruluck/projects/framepiler_test_env:/workspace \
    framepiler-test-env \
    bash -c 'cd /workspace && FRAMEC_BIN=/frame_transpiler/target/release/framec adapter_protocol/scripts/run_adapter_smoke.sh'
  ```

This gives both teams a pinned toolchain and a one‑command way to validate adapter semantics.

---

## 7. Summary of Recommended Steps

1. **Adopt this folder as the shared, versioned home for adapter integration tests.**
2. **Create `adapter_protocol_minimal.frm` here and mirror it into the PT repo’s `framec_tests`.**
3. **Add `tsconfig.json`, `package.json`, and `node_harness.ts` here to make the adapter smoke test hermetic.**
4. **Switch external validators (like Bug #081’s `/tmp` script) to call into this env instead of hard‑coding external paths.**
5. **Optionally, introduce the Dockerized test shell to pin Node/TS/Python/Rust versions across both teams.**

This setup keeps adapter semantics honest, portable, and aligned with the V3 architecture and runtime docs.


---

## Comments (from Debugger team)

Strengths
- Clear, hermetic test goal shared across PT and DAP; avoids local path drift.
- Single source for runtime/types; eliminates validator fragility seen in prior bugs.
- Minimal AdapterProtocol fixture + Node harness mirrors our current flow, but formalizes it.
- Dual‑home of the fixture (shared env + PT repo) keeps both sides in sync.
- Optional Docker gives a stable toolchain for CI and local reproduction.

Gaps / Clarifications
- Runtime types source: prefer a single consumption mode (npm package vs mirrored d.ts). If mirroring, document a refresh script and pin to a PT commit SHA.
- Version pinning: specify exact versions for typescript/@types/node and commit a lockfile to avoid drift.
- Success signal: standardize a harness marker (e.g., `ADAPTER_SMOKE_OK`) and exit codes for CI.
- Python parity: outline a minimal Python fixture + smoke path (PYTHONPATH/runtimes) for symmetry.
- Version matrix: small table mapping `framec` → compatible runtime/types for quick triage.
- Artifact policy: document OUT_DIR cleanup vs retention on failure, and where logs live in CI.

Suggestions / Next Steps
- Lock versions now in `adapter_protocol/package.json` and `tsconfig.json`; add a lockfile.
- Pin runtime types via an npm package for `frame_runtime_ts` (preferred) or a generated d.ts with a recorded source SHA.
- Add simple entrypoints:
  - `scripts/run_adapter_smoke.sh` that: generate TS (via FRAMEC_BIN), compile with local tsconfig, run `node_harness.ts`.
  - Makefile / npm scripts for `smoke`, `clean`.
- CI examples: add a minimal GH Actions job that runs the smoke test; PT can call the same script from its CI.
- Cross‑link V3 docs for glossary terms (wrapper/router/start state) to keep expectations aligned with spec language.

Decision Request
- Proposal: adopt this shared env as the canonical adapter‑level test harness.
- If you agree, we’ll scaffold:
  - `adapter_protocol_minimal.frm`, `tsconfig.json`, `package.json` (+ lockfile), `scripts/run_adapter_smoke.sh`, and `scripts/node_harness.ts`.
  - Mirror the FRM and add a v3_cli test in the PT repo.
- If you prefer an alternative (e.g., different structure or package source for runtime types), please reply with a counter‑proposal so we can converge this week.

— Added on 2025-11-18 by vscode_editor
