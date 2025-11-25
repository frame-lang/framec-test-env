# Framepiler Test Env — Adapter Smoke

Quick validation for V3 TS generated systems without workspace path dependencies.

Usage:

```
FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec \
  ./adapter_protocol/scripts/run_adapter_smoke.sh
```

Expected output:
- `ADAPTER_SMOKE_OK` on success.

Notes:
- Uses a minimal `frame_runtime_ts.d.ts` shim; does not require @types/node.
- Generates a temp tsconfig with path mapping so `import { FrameEvent, FrameCompartment } from 'frame_runtime_ts'` resolves.
