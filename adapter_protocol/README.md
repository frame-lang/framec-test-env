# Adapter Protocol — Shared Harnesses

This folder contains shared, offline harnesses for validating the V3 adapter protocol and the real VS Code Frame Debug Adapter FRM under the TypeScript target.

## Harnesses

- `scripts/run_adapter_smoke.sh`
  - Generates TS from `adapter_protocol_minimal.frm`, compiles with `tsc`, and runs `scripts/node_harness.js`.
  - Asserts core semantics: ready/handshake, guard/deferral, single‑inflight, isPaused on stopped.
  - Output: prints `ADAPTER_SMOKE_OK` on success.

- `scripts/run_fda_smoke.sh`
  - Compiles and runs the real adapter FRM (`src/debug/state_machines/FrameDebugAdapter.frm`) using a local runtime shim.
  - Runs `scripts/node_fda_harness.js` to drive a minimal flow (initialize → launch → onPythonConnected → configurationDone).
  - Output: prints `FDA_NODE_HARNESS_OK` and `FDA_SMOKE_OK` on success.

## Requirements

- `framec` binary (path via `FRAMEC_BIN` or defaults to `/Users/marktruluck/projects/frame_transpiler/target/release/framec`).
- Local TypeScript compiler installed at `adapter_protocol/node_modules/.bin/tsc` (no network).

## Commands

Adapter protocol smoke:

```bash
FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec \
./scripts/run_adapter_smoke.sh
```

Frame Debug Adapter smoke (real FRM):

```bash
FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec \
./scripts/run_fda_smoke.sh /Users/marktruluck/vscode_editor/src/debug/state_machines/FrameDebugAdapter.frm
```

## Notes

- Both harnesses create temporary output directories, compile offline, and avoid external network dependencies.
- The FDA harness injects a small local runtime shim into `OUT/out/node_modules/frame_runtime_ts` to satisfy imports and free functions expected by the generated adapter JS.
- Use the shared bug tracker at `/Users/marktruluck/projects/framepiler_test_env/bug` for filing/closing issues found via these harnesses.

