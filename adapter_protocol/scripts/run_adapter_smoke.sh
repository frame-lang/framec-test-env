#!/usr/bin/env bash
set -euo pipefail

# FRAMEC_BIN should point to the framec binary from the PT repo.
# Default assumes framepiler_test_env and frame_transpiler are sibling repos.
FRAMEC_BIN="${FRAMEC_BIN:-../../frame_transpiler/target/release/framec}"

if [ ! -x "$FRAMEC_BIN" ]; then
  echo "ERROR: FRAMEC_BIN does not point to an executable framec (FRAMEC_BIN=$FRAMEC_BIN)" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$(mktemp -d)"

echo "[adapter_smoke] Using OUT_DIR=$OUT_DIR"

# 1) Generate TypeScript from the minimal AdapterProtocol fixture
"$FRAMEC_BIN" compile -l typescript -o "$OUT_DIR" "$ROOT_DIR/adapter_protocol_minimal.frm"

# 2) Compile TS -> JS using an in-memory tsconfig and runtime types
cat > "$OUT_DIR/tsconfig.json" <<JSON
{
  "compilerOptions": {
    "target": "ES2019",
    "module": "commonjs",
    "baseUrl": "$ROOT_DIR",
    "paths": {
      "frame_runtime_ts": ["runtime/frame_runtime_ts"]
    },
    "esModuleInterop": true,
    "strict": true,
    "noImplicitAny": false,
    "skipLibCheck": true,
    "types": ["node"],
    "typeRoots": ["$ROOT_DIR/node_modules/@types"],
    "outDir": "$OUT_DIR/out"
  },
  "include": [
    "$OUT_DIR/adapter_protocol_minimal.ts",
    "$ROOT_DIR/runtime/frame_runtime_ts.d.ts",
    "$ROOT_DIR/scripts/node_harness.ts"
  ]
}
JSON

npx -y tsc -p "$OUT_DIR/tsconfig.json"

# Locate the compiled JS for the minimal adapter protocol and harness.
OUT_JS="$(find "$OUT_DIR/out" -type f -name 'adapter_protocol_minimal.js' | head -n 1 || true)"
HARNESS_JS="$(find "$OUT_DIR/out" -type f -name 'node_harness.js' | head -n 1 || true)"

if [ -z "$OUT_JS" ] || [ ! -f "$OUT_JS" ]; then
  echo "ERROR: Could not find generated adapter_protocol_minimal.js under $OUT_DIR/out" >&2
  exit 1
fi

if [ -z "$HARNESS_JS" ] || [ ! -f "$HARNESS_JS" ]; then
  echo "ERROR: Could not find compiled node_harness.js under $OUT_DIR/out" >&2
  exit 1
fi

# Provide a minimal runtime stub so that the generated adapter module can
# import 'frame_runtime_ts' without depending on the full Node-based runtime.
RUNTIME_STUB_DIR="$(dirname "$OUT_JS")/node_modules/frame_runtime_ts"
mkdir -p "$RUNTIME_STUB_DIR"
cat > "$RUNTIME_STUB_DIR/index.js" <<'JS'
class FrameEvent {
  constructor(message, parameters) {
    this.message = message;
    this.parameters = parameters;
  }
}
class FrameCompartment {
  constructor(
    state,
    enterArgs,
    exitArgs,
    stateArgs,
    stateVars,
    enterArgsCollection,
    exitArgsCollection,
    forwardEvent
  ) {
    this.state = state;
    this.enterArgs = enterArgs;
    this.exitArgs = exitArgs;
    this.stateArgs = stateArgs;
    this.stateVars = stateVars;
    this.enterArgsCollection = enterArgsCollection;
    this.exitArgsCollection = exitArgsCollection;
    this.forwardEvent = forwardEvent;
  }
}
module.exports = { FrameEvent, FrameCompartment };
JS

echo "[adapter_smoke] Running Node harness..."
OUT_JS="$OUT_JS" node "$HARNESS_JS"
echo "ADAPTER_SMOKE_OK"
