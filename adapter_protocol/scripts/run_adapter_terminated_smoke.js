#!/usr/bin/env node
/**
 * Adapter termination routing smoke without sockets/framec.
 * Ensures onPythonTerminated emits a DAP terminated event and records exit code.
 */
const path = require('path');

// Load support first to inject stubs/globals
const support = require(path.join(process.cwd(), 'dist/fda_adapter/out/src/debug/state_machines/FrameRuntimeSupport.js'));
let sentEvents = [];

support.frameRuntimeFileExists = () => true;
support.frameRuntimeCreateServer = () => ({ server: {}, port: 12345 });
support.frameRuntimeTranspileFrame = () => ({ success: true, code: 'print("stub")', sourceMap: {} });
support.frameRuntimeInjectFrameDebugRuntime = code => code;
support.frameRuntimeSpawnPython = () => ({ success: true, process: null, pid: 0 });
support.frameRuntimeSendCommand = () => true;
support.frameRuntimeMapSet = (obj, key, val) => { if (obj && typeof obj === 'object') obj[key] = val; };
global.frameRuntimeMapSet = support.frameRuntimeMapSet;

// Capture DAP events emitted by adapter
support.frameRuntimeSendEvent = (event, body) => {
  sentEvents.push({ event, body });
};
global.frameRuntimeSendEvent = support.frameRuntimeSendEvent;

const { FrameDebugAdapter } = require(path.join(process.cwd(), 'dist/fda_adapter/adapter.js'));
if (!FrameDebugAdapter) {
  console.error('ADAPTER_TERMINATED_SMOKE_FAIL: FrameDebugAdapter export not found');
  process.exit(1);
}

const { FrameCompartment } = require(path.join(process.cwd(), 'frame_runtime_ts'));
const adapter = new FrameDebugAdapter();
adapter['$']();
// Place adapter directly into Connected; avoid file/spawn checks
adapter.debugPort = 12345;
adapter.debugServer = {};
adapter.frameFile = '/tmp/stub.frm';
adapter._frame_transition(new FrameCompartment("__FrameDebugAdapter_state_Connected"));
adapter.onPythonTerminated(42);

const terminatedEvent = sentEvents.find(e => e.event === 'terminated');
const state = {
  terminationExitCode: adapter.terminationExitCode,
  compartmentState: adapter._compartment ? adapter._compartment.state : null,
  terminatedEvent: terminatedEvent
};
console.log('STATE', state);

if (!terminatedEvent || terminatedEvent.body.exitCode !== 42) {
  console.error('ADAPTER_TERMINATED_SMOKE_FAIL: missing/invalid terminated event');
  process.exit(1);
}
if (adapter.terminationExitCode !== 42 || state.compartmentState !== '__FrameDebugAdapter_state_Terminating') {
  console.error('ADAPTER_TERMINATED_SMOKE_FAIL: adapter termination state not set');
  process.exit(1);
}

console.log('ADAPTER_TERMINATED_SMOKE_OK');
process.exit(0);
