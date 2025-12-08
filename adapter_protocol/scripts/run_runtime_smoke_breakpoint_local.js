#!/usr/bin/env node
/**
 * Breakpoint smoke without sockets/framec.
 * Stubs runtime helpers and asserts adapter paused state/line on breakpoint.
 */
const path = require('path');
const fs = require('fs');
const os = require('os');

const tmpFrmPath = path.join(os.tmpdir(), 'stub_bp.frm');
fs.writeFileSync(tmpFrmPath, '// stub breakpoint smoke\n');

const support = require(path.join(process.cwd(), 'dist/fda_adapter/out/src/debug/state_machines/FrameRuntimeSupport.js'));
const { FrameDebugAdapter } = require(path.join(process.cwd(), 'dist/fda_adapter/adapter.js'));
if (!FrameDebugAdapter) {
  console.error('BREAKPOINT_LOCAL_SMOKE_FAIL: FrameDebugAdapter export not found');
  process.exit(1);
}

// Stub runtime helpers
support.frameRuntimeTranspileFrame = () => ({ success: true, code: 'print("stub")', sourceMap: { '5': 10 } });
support.frameRuntimeInjectFrameDebugRuntime = code => code;
support.frameRuntimeSpawnPython = () => ({ success: true, process: null, pid: 0 });
support.frameRuntimeCreateServer = () => ({ server: {}, port: 12345 });
support.frameRuntimeSendCommand = () => true;
support.frameRuntimeFileExists = () => true;
support.frameRuntimeMapSet = (obj, key, val) => { if (obj && typeof obj === 'object') obj[key] = val; };
global.frameRuntimeMapSet = support.frameRuntimeMapSet;

const adapter = new FrameDebugAdapter();
adapter['$']();
adapter.createTcpServer = function stubCreateServer() { this.debugPort = 12345; this.debugServer = {}; return true; };
adapter.transpileFrameFile = function stubTranspileFile() { this.frameSourceMap = { "5": 10 }; this.framePythonCode = ""; this.debugRuntimeCode = "print('stub')"; this.refreshPendingBreakpoints(); return true; };
adapter.spawnFramePython = function stubSpawnPython() { return true; };
adapter.sendCommand = function stubSendCommand() { return true; };

adapter.initialize({});
adapter.launch({ program: tmpFrmPath, stopOnEntry: false });
adapter.onPythonConnected();

adapter.onPythonExecutionPaused('breakpoint', 5);

const state = { isPaused: adapter.isPaused, lastStoppedReason: adapter.lastStoppedReason, currentFrameLine: adapter.currentFrameLine };
console.log('STATE', state);

if (!state.isPaused || state.lastStoppedReason !== 'breakpoint' || state.currentFrameLine !== 5) {
  console.error('BREAKPOINT_LOCAL_SMOKE_FAIL');
  process.exit(1);
}

console.log('BREAKPOINT_LOCAL_SMOKE_OK');
process.exit(0);
