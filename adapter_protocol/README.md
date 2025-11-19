# AdapterProtocol Minimal Smoke Tests

This directory hosts shared AdapterProtocol‑style semantics tests for both the
Frame Transpiler (PT) team and the Debugger Adapter (DAP) team.

The goal is to make adapter behavior (guard/deferral, ready/handshake, stopped
state flags) reproducible with the **same commands** on any machine.

## Contents

- `adapter_protocol_full.frm`  
  Full AdapterProtocol FRM copied from the external harness for reference.

- `adapter_protocol_minimal.frm`  
  Trimmed fixture that captures the core semantics:
  - Guarded commands (`continue`/`next`/`stepIn`/`stepOut`/`pause`) defer until
    both `handshakeComplete` and `isReady` are true.
  - Single in‑flight guarded command after ready (uses `pendingAction`).
  - `setBreakpoints` defers until ready/handshake.
  - `stopped` updates `isPaused`, `lastStoppedReason`, `lastThreadId`.

- `runtime/frame_runtime_ts.d.ts`  
  Canonical TypeScript runtime type surface for `frame_runtime_ts`, mirrored
  from the PT repo.

- `tsconfig.json`  
  Pinned TypeScript configuration for local smoke tests.

- `package.json`  
  Local dev dependencies (pinned `typescript` and `@types/node`) and scripts.

- `scripts/run_adapter_smoke.sh`  
  Shell entrypoint that:
  1. Compiles `adapter_protocol_minimal.frm` with `framec` into a temporary
     directory as TypeScript.
  2. Runs `tsc` using the pinned `tsconfig` and runtime types.
  3. Executes the Node harness against the generated JS.
  4. Prints `ADAPTER_SMOKE_OK` on success.

- `scripts/node_harness.ts`  
  Node test driver that:
  - Calls `start()` → `drainCommands()` → expects empty queue.
  - Calls `runtimeConnected()` → `drainCommands()` → expects `initialize` +
    `ping`.
  - Enqueues a guarded command before ready → `drainCommands()` → expects
    deferral (empty).
  - Sends `hello` + `ready` via `runtimeMessage(payload)` then enqueues
    `continue` → expects exactly one `continue` in the drained queue.
  - Sends `stopped` event → expects `isPaused === true` and stopped metadata
    populated.

## Prerequisites

- Built `framec` binary from the PT repo:
  ```bash
  cd /Users/marktruluck/projects/frame_transpiler
  cargo build --release
  ```

- Node + npm on PATH (for `npx` and `tsc`).

## One‑time setup

From this directory:

```bash
cd /Users/marktruluck/projects/framepiler_test_env/adapter_protocol
npm install
```

This will install `typescript` and `@types/node` and produce a lockfile that
should be checked in to keep versions pinned.

## Running the smoke test (host)

```bash
cd /Users/marktruluck/projects/framepiler_test_env/adapter_protocol
FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec \
  ./scripts/run_adapter_smoke.sh
```

On success, you should see:

```text
[adapter_smoke] Using OUT_DIR=/tmp/...
[adapter_smoke] Running Node harness...
ADAPTER_SMOKE_OK
```

## Relationship to PT v3_cli tests

The minimal FRM is mirrored into the PT repo as:

- `framec_tests/language_specific/typescript/v3_cli/positive/adapter_protocol_minimal.frm`

That v3_cli test uses `@tsc-compile` and `@compile-expect` to assert the
wrapper/router shape for `AdapterProtocolMinimal`. The Node harness here
asserts the **runtime semantics**; together they provide a shared contract for
AdapterProtocol‑style systems.

