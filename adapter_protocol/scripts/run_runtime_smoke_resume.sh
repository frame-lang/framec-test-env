#!/usr/bin/env bash
set -euo pipefail

# Resume smoke: entry stop then continued; asserts paused clears and executionState returns to running.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

if [[ -x "${ROOT}/scripts/build_adapter_js.sh" ]]; then
  "${ROOT}/scripts/build_adapter_js.sh"
fi

TMP_FRM="$(mktemp /tmp/resume_smoke.XXXXXX.frm)"
trap 'rm -f "$TMP_FRM"' EXIT
cat > "$TMP_FRM" <<'EOF'
@target python_3
system ResumeSmoke {
    interface:
        start()
    machine:
        $Init {
            start() { -> $Init }
        }
}
EOF

TMP_FRM_PATH="$TMP_FRM" node <<'NODE'
const path = require('path');
const { spawn } = require('child_process');

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
send({"type":"event","event":"stopped","data":{"reason":"entry","frameLine":2,"threadId":1}})
time.sleep(0.1)
send({"type":"event","event":"continued","data":{"threadId":1}})
time.sleep(0.05)
s.close()
`;

global.frameRuntimeTranspileFrame = function(filePath, target, debug) {
  return { success: true, code: stubPython, sourceMap: { "2": 4 } };
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
adapter.launch({ program: process.env.TMP_FRM_PATH || '', stopOnEntry: true });

setTimeout(() => {
  const state = { isPaused: adapter.isPaused, lastStoppedReason: adapter.lastStoppedReason, currentFrameLine: adapter.currentFrameLine, executionState: adapter.executionState };
  console.log('STATE', state);
  if (adapter.isPaused || adapter.lastStoppedReason !== "" || adapter.executionState !== "running") {
    console.error('RESUME_SMOKE_FAIL');
    process.exit(1);
  }
  console.log('RESUME_SMOKE_OK');
  process.exit(0);
}, 1000);
NODE
