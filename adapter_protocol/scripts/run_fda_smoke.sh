#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"
FRM_PATH="${1:-}"

if [ -z "${FRM_PATH}" ]; then
  echo "usage: $(basename "$0") <FrameDebugAdapter.frm>" >&2
  exit 2
fi
if [ ! -f "$FRM_PATH" ]; then
  echo "error: FRM not found: $FRM_PATH" >&2
  exit 2
fi

OUT_DIR="$(mktemp -d)"
"$FRAMEC_BIN" --version || true
"$FRAMEC_BIN" compile -l typescript -o "$OUT_DIR" "$FRM_PATH"

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
  "files": ["$(basename "$FRM_PATH" .frm).ts", "$ROOT/runtime/frame_runtime_ts.d.ts"]
}
JSON

TS_BIN="$ROOT/node_modules/.bin/tsc"
if [ ! -x "$TS_BIN" ]; then
  echo "error: TypeScript compiler not found at $TS_BIN" >&2
  exit 1
fi
"$TS_BIN" -p "$OUT_DIR/tsconfig.json"

# Provide a runtime shim so Node can resolve 'frame_runtime_ts' with needed fns
mkdir -p "$OUT_DIR/out/node_modules/frame_runtime_ts"
cat > "$OUT_DIR/out/node_modules/frame_runtime_ts/index.js" <<'JS'
function now() { return Date.now(); }
function str(x){ return String(x); }
function num(x){ return Number(x); }
function keys(m){ return Object.keys(m||{}); }
class FrameEvent { constructor(message, parameters){ this.message=String(message); this.parameters=parameters||null; } }
class FrameCompartment { constructor(state, enterArgs, exitArgs, stateArgs, stateVars){ this.state=String(state); this.enterArgs=enterArgs; this.exitArgs=exitArgs; this.stateArgs=stateArgs||{}; this.stateVars=stateVars||{}; } }
let _adapter = null;
function frameRuntimeSetDebugAdapter(a){ _adapter = a; }
function frameRuntimeCreateServer(){ return { port: 5555, server: { _queue: [] } }; }
function frameRuntimeSendCommand(server, commandType, data){
  server._queue.push({type:'command', action:commandType, data});
  return true;
}
function frameRuntimeSetEnv(){ return true; }
function frameRuntimeToString(x){ return String(x); }
function frameRuntimeGetTimestamp(){ return Date.now(); }
function frameRuntimeFileExists(){ return true; }
function frameRuntimeTranspileFrame(){ return { success:true, code: "print('hello')\n", sourceMap: {} }; }
function frameRuntimeInjectFrameDebugRuntime(code){ return "# debug runtime\n" + code; }
function frameRuntimeGetLength(x){ if (typeof x === 'string') return x.length; if (Array.isArray(x)) return x.length; return 0; }
function frameRuntimeGetMapSize(m){ return m ? Object.keys(m).length : 0; }
function frameRuntimeMapSet(m,k,v){ m[k]=v; }
function frameRuntimeMapGet(m,k){ return m[k]; }
function frameRuntimeMapHasKey(m,k){ return Object.prototype.hasOwnProperty.call(m,k); }
function frameRuntimeMapKeys(m){ return Object.keys(m||{}); }
function frameRuntimeStringToNumber(s){ return Number(s); }
function frameRuntimeWait(ms){ const end=Date.now()+ms; while (Date.now()<end) {} }
function frameRuntimeCloseServer(){ return true; }
function frameRuntimeKillProcess(){ return true; }
function frameRuntimeSpawnPython(){ return { success:true, process:{}, pid:12345 }; }
function frameRuntimeSendEvent(event, body){ /* simulate DAP event */ }
function frameRuntimeSendResponse(command, body){ /* simulate DAP response */ }
module.exports = {
  FrameEvent, FrameCompartment,
  frameRuntimeSetDebugAdapter, frameRuntimeCreateServer, frameRuntimeSendCommand,
  frameRuntimeSetEnv, frameRuntimeToString, frameRuntimeGetTimestamp, frameRuntimeFileExists,
  frameRuntimeTranspileFrame, frameRuntimeInjectFrameDebugRuntime, frameRuntimeGetLength,
  frameRuntimeGetMapSize, frameRuntimeMapSet, frameRuntimeMapGet, frameRuntimeMapHasKey,
  frameRuntimeMapKeys, frameRuntimeStringToNumber, frameRuntimeWait, frameRuntimeCloseServer,
  frameRuntimeKillProcess, frameRuntimeSpawnPython, frameRuntimeSendEvent, frameRuntimeSendResponse
};
JS

OUT_JS="$OUT_DIR/out/$(basename "$FRM_PATH" .frm).js"
NODE_HARNESS="$ROOT/scripts/node_fda_harness.js"
NODE_PATH="$OUT_DIR/out/node_modules" OUT_JS="$OUT_JS" node "$NODE_HARNESS"

echo "FDA_SMOKE_OK"
