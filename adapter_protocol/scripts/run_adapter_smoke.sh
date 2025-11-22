#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-framec}"
command -v "$FRAMEC_BIN" >/dev/null 2>&1 || FRAMEC_BIN="/Users/marktruluck/projects/frame_transpiler/target/release/framec"
OUT_DIR="$(mktemp -d)"

# 1) Generate TS from FRM
"$FRAMEC_BIN" --version || true
"$FRAMEC_BIN" compile -l typescript -o "$OUT_DIR" "$ROOT/adapter_protocol_minimal.frm"

# 2) Create temp tsconfig mapping frame_runtime_ts to local d.ts
cat > "$OUT_DIR/tsconfig.json" <<JSON
{
  "compilerOptions": {
    "target": "es2019",
    "module": "commonjs",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": { "frame_runtime_ts": ["$ROOT/runtime/frame_runtime_ts.d.ts"] },
    "outDir": "./out"
  },
  "files": ["adapter_protocol_minimal.ts", "$ROOT/runtime/frame_runtime_ts.d.ts"]
}
JSON

# 3) Compile to JS using local TypeScript (no network)
TS_BIN="$ROOT/node_modules/.bin/tsc"
if [ ! -x "$TS_BIN" ]; then
  echo "error: TypeScript compiler not found at $TS_BIN" >&2
  exit 1
fi
"$TS_BIN" -p "$OUT_DIR/tsconfig.json"
# Provide a runtime shim so Node can resolve 'frame_runtime_ts'
mkdir -p "$OUT_DIR/out/node_modules/frame_runtime_ts"
cat > "$OUT_DIR/out/node_modules/frame_runtime_ts/index.js" <<'JS'
class FrameEvent { constructor(message, parameters){ this.message=String(message); this.parameters=parameters||null; } }
class FrameCompartment { constructor(state, enterArgs, exitArgs, stateArgs, stateVars){ this.state=String(state); this.enterArgs=enterArgs; this.exitArgs=exitArgs; this.stateArgs=stateArgs||{}; this.stateVars=stateVars||{}; } }
module.exports = { FrameEvent, FrameCompartment };
JS
OUT_JS="$OUT_DIR/out/adapter_protocol_minimal.js"

# 4) Run node harness
OUT_JS="$OUT_JS" node "$ROOT/scripts/node_harness.js"
