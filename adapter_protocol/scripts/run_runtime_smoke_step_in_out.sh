#!/usr/bin/env bash
set -euo pipefail

# Runtime stepIn/stepOut smokes: stub runtime emits continued + stopped(step) for each.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

if [[ -x "${ROOT}/scripts/build_adapter_js.sh" ]]; then
  "${ROOT}/scripts/build_adapter_js.sh"
fi

TMP_FRM="$(mktemp /tmp/step_io_smoke.XXXXXX.frm)"
cat > "$TMP_FRM" <<'EOF'
@target python_3
system StepIOSmoke {
    interface: start()
    machine:
        $Init { start() { -> $Init } }
}
EOF
cleanup() {
  rm -f "$TMP_FRM"
}
trap cleanup EXIT

run_case() {
  local action="$1"
  local frameLine="$2"

  TMP_FRM_PATH="$TMP_FRM" ACTION="$action" FRAME_LINE="$frameLine" node <<'NODE'
const path = require('path');
const { spawn } = require('child_process');

const action = process.env.ACTION;
const frameLine = parseInt(process.env.FRAME_LINE || '0', 10);

process.env.NODE_PATH = [
  path.join(process.cwd(), 'frame_runtime_ts'),
  path.join(process.cwd(), 'dist/node_modules'),
  process.env.NODE_PATH || ''
].filter(Boolean).join(path.delimiter);
require('module').Module._initPaths();

require(path.join(process.cwd(), 'dist/out/src/debug/state_machines/FrameRuntimeSupport.js'));
const { FrameDebugAdapter } = require(path.join(process.cwd(), 'dist/adapter.js'));
if (!FrameDebugAdapter) throw new Error('FrameDebugAdapter export not found');

const stubPython = `
import os, socket, json, time
port = int(os.environ["FRAME_DEBUG_PORT"])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", port))
def send(msg):
    s.send((json.dumps(msg)+"\\n").encode("utf-8"))
send({"type":"event","event":"connected","data":{}})
send({"type":"event","event":"ready","data":{}})
send({"type":"response","command":"` + action + `","success": True})
send({"type":"event","event":"continued","data":{"threadId":1}})
send({"type":"event","event":"stopped","data":{"reason":"step","frameLine":` + frameLine + `,"threadId":1}})
time.sleep(0.05)
s.close()
`;

global.frameRuntimeTranspileFrame = function(filePath, target, debug) {
  return { success: true, code: stubPython, sourceMap: { [String(frameLine)]: frameLine + 5 } };
};
global.frameRuntimeInjectFrameDebugRuntime = function(code, sourceMap, port) { return stubPython; };
global.frameRuntimeSpawnPython = function(code) {
  const proc = spawn('python3', ['-c', code], { env: { ...process.env } });
  proc.stderr.on('data', d => process.stderr.write(d));
  return { success: true, process: proc, pid: proc.pid };
};

const adapter = new FrameDebugAdapter();
adapter['$']();
adapter.initialize({});
adapter.launch({ program: process.env.TMP_FRM_PATH || '', stopOnEntry: false });
if (action === 'stepIn') adapter.stepInto(1); else adapter.stepOutOf(1);

setTimeout(() => {
  const state = { isPaused: adapter.isPaused, lastStoppedReason: adapter.lastStoppedReason, currentFrameLine: adapter.currentFrameLine };
  console.log('STATE', action, state);
  if (!state.isPaused || state.lastStoppedReason !== 'step' || state.currentFrameLine !== frameLine) {
    console.error(action.toUpperCase() + '_SMOKE_FAIL');
    process.exit(1);
  }
  console.log(action.toUpperCase() + '_SMOKE_OK');
  process.exit(0);
}, 800);
NODE
}

run_case stepIn 9
run_case stepOut 11

echo "STEP_IN_OUT_SMOKES_OK"
