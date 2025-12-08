#!/usr/bin/env bash
set -euo pipefail

# Minimal real-runtime smoke using adapter interface (initialize + launch).
# Stubs transpilation to emit a tiny Python runtime that connects and sends stopped(entry).

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

# Build adapter bundle if available; otherwise expect dist/fda_adapter present
if [[ -x "${ROOT}/scripts/build_adapter_js.sh" ]]; then
  "${ROOT}/scripts/build_adapter_js.sh"
fi

TMP_FRM="$(mktemp /tmp/entry_smoke.XXXXXX.frm)"
trap 'rm -f "$TMP_FRM"' EXIT
cat > "$TMP_FRM" <<'EOF'
@target python_3
system EntrySmoke {
    interface:
        start()
    machine:
        $Init {
            start() { -> $Init }
        }
}
EOF

TMP_FRM_PATH="$TMP_FRM" node <<'NODE'
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ADAPTER_JS = path.join(process.cwd(), 'dist/adapter.js');
// Make frame_runtime_ts resolvable
process.env.NODE_PATH = [
  path.join(process.cwd(), 'frame_runtime_ts'),
  path.join(process.cwd(), 'dist/node_modules'),
  process.env.NODE_PATH || ''
].filter(Boolean).join(path.delimiter);
require('module').Module._initPaths();

// Load runtime support and adapter
require(path.join(process.cwd(), 'dist/out/src/debug/state_machines/FrameRuntimeSupport.js'));
const { FrameDebugAdapter } = require(ADAPTER_JS);
if (!FrameDebugAdapter) throw new Error('FrameDebugAdapter export not found');

const useStub = process.env.USE_STUB !== '0';
const useHandcrafted = process.env.USE_HANDCRAFT === '1';

// Stub transpile to return minimal Python that connects and sends entry stop
const stubPython = `
import os, socket, json, time
port = int(os.environ["FRAME_DEBUG_PORT"])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", port))
def send(msg):
    s.send((json.dumps(msg)+"\\n").encode("utf-8"))
send({"type":"event","event":"connected","data":{}})
send({"type":"event","event":"ready","data":{}})
send({"type":"event","event":"stopped","data":{"reason":"entry","frameLine":1,"threadId":1}})
time.sleep(0.05)
s.close()
`;
if (useHandcrafted) {
  const handcrafted = fs.readFileSync(path.join(process.cwd(), 'scripts/python_runtime_handcrafted.py'), 'utf8');
  global.frameRuntimeTranspileFrame = function(filePath, target, debug) {
    return { success: true, code: handcrafted, sourceMap: { "1": 1 } };
  };
  global.frameRuntimeInjectFrameDebugRuntime = function(code, sourceMap, port) { return handcrafted; };
  global.frameRuntimeSpawnPython = function(code) {
    const proc = spawn('python3', ['-c', code], { env: { ...process.env } });
    proc.stderr.on('data', d => process.stderr.write(d));
    return { success: true, process: proc, pid: proc.pid };
  };
} else if (useStub) {
  global.frameRuntimeTranspileFrame = function(filePath, target, debug) {
    return { success: true, code: stubPython, sourceMap: { "1": 1 } };
  };
  global.frameRuntimeInjectFrameDebugRuntime = function(code, sourceMap, port) { return stubPython; };
  global.frameRuntimeSpawnPython = function(code) {
    const proc = spawn('python3', ['-c', code], { env: { ...process.env } });
    proc.stderr.on('data', d => process.stderr.write(d));
    return { success: true, process: proc, pid: proc.pid };
  };
}

async function main() {
  const adapter = new FrameDebugAdapter();
  adapter['$'](); // enter initial state
  adapter.initialize({});
  adapter.launch({ program: process.env.TMP_FRM_PATH || '' , stopOnEntry: true });

  setTimeout(() => {
    console.log('STATE', { isPaused: adapter.isPaused, lastStoppedReason: adapter.lastStoppedReason, currentFrameLine: adapter.currentFrameLine });
    if (!adapter.isPaused || adapter.lastStoppedReason !== 'entry') {
      console.error('ENTRY_SMOKE_FAIL');
      process.exit(1);
    }
    console.log('ENTRY_SMOKE_OK');
    process.exit(0);
  }, 800);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
NODE
