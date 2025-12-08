#!/usr/bin/env node
/**
 * Stop-on-entry + terminated smoke without sockets.
 * Stubs runtime helpers to avoid TCP/framec and asserts paused state on entry
 * and termination exit code handling.
 */
const path = require('path');
const fs = require('fs');
const os = require('os');

// Prepare a stub FRM path to satisfy launch arguments
const tmpFrmPath = path.join(os.tmpdir(), 'stub_entry.frm');
fs.writeFileSync(tmpFrmPath, '// stub entry smoke\n');

// Load support and adapter from built bundle (run scripts/build_adapter_js.sh first)
const support = require(path.join(process.cwd(), 'dist/fda_adapter/out/src/debug/state_machines/FrameRuntimeSupport.js'));
const { FrameDebugAdapter } = require(path.join(process.cwd(), 'dist/fda_adapter/adapter.js'));
if (!FrameDebugAdapter) {
  console.error('ENTRY_LOCAL_SMOKE_FAIL: FrameDebugAdapter export not found');
  process.exit(1);
}

// Stub runtime helpers to avoid network and framec
support.frameRuntimeTranspileFrame = function stubTranspile(_filePath, _target, _debug) {
  return { success: true, code: 'print("stub")', sourceMap: { '1': 1 } };
};
support.frameRuntimeInjectFrameDebugRuntime = function stubInject(code, _map, _port) {
  return code;
};
support.frameRuntimeSpawnPython = function stubSpawn(_code) {
  return { success: true, process: null, pid: 0 };
};
support.frameRuntimeCreateServer = function stubServer() {
  return { server: {}, port: 12345 };
};
support.frameRuntimeSendCommand = function stubSend(_server, action, data) {
  console.log(`[StubSend] ${action}`, data || {});
};
support.frameRuntimeFileExists = function stubExists(_path) {
  return true;
};
support.frameRuntimeMapSet = function stubMapSet(obj, key, val) {
  if (obj && typeof obj === 'object') obj[key] = val;
};
global.frameRuntimeMapSet = support.frameRuntimeMapSet;

// Drive adapter through stop-on-entry and termination paths
const adapter = new FrameDebugAdapter();
adapter.createTcpServer = function stubCreateServer() {
  this.debugPort = 12345;
  this.debugServer = {};
  return true;
};
adapter.transpileFrameFile = function stubTranspileFile() {
  this.frameSourceMap = { "1": 1 };
  this.framePythonCode = "";
  this.debugRuntimeCode = "print('stub')";
  this.refreshPendingBreakpoints();
  return true;
};
adapter.spawnFramePython = function stubSpawnPython() {
  return true;
};
adapter.sendCommand = function stubSendCommand() {
  return true;
};

adapter['$'](); // enter initial compartment
adapter.initialize({});
adapter.launch({ program: tmpFrmPath, stopOnEntry: true });
adapter.onPythonConnected(); // transition to Connected

// Simulate runtime stop on entry
adapter.onPythonExecutionPaused('entry', 1);

// Simulate runtime termination
adapter.onPythonTerminated(0);

const state = {
  isPaused: adapter.isPaused,
  lastStoppedReason: adapter.lastStoppedReason,
  currentFrameLine: adapter.currentFrameLine,
  terminationExitCode: adapter.terminationExitCode,
  compartmentState: adapter._compartment ? adapter._compartment.state : null
};
console.log('STATE', state);

if (!state.isPaused || state.lastStoppedReason !== 'entry' || state.currentFrameLine !== 1) {
  console.error('ENTRY_LOCAL_SMOKE_FAIL: pause semantics');
  process.exit(1);
}
if (state.terminationExitCode !== 0 || state.compartmentState !== '__FrameDebugAdapter_state_Terminating') {
  console.error('ENTRY_LOCAL_SMOKE_FAIL: termination semantics');
  process.exit(1);
}

console.log('ENTRY_LOCAL_SMOKE_OK');
process.exit(0);
