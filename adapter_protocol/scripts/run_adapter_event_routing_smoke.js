#!/usr/bin/env node
/**
 * Event routing smoke without sockets/framec.
 * Verifies onPythonExecutionPaused/resumed/terminated are forwarded in
 * WaitingForConnection and Connected states.
 */
const path = require('path');

const support = require(path.join(process.cwd(), 'dist/fda_adapter/out/src/debug/state_machines/FrameRuntimeSupport.js'));
let sentEvents = [];

// Stub runtime helpers
support.frameRuntimeFileExists = () => true;
global.frameRuntimeFileExists = support.frameRuntimeFileExists;
support.frameRuntimeCreateServer = () => ({ server: {}, port: 12345 });
support.frameRuntimeTranspileFrame = () => ({ success: true, code: 'print("stub")', sourceMap: {} });
support.frameRuntimeInjectFrameDebugRuntime = code => code;
support.frameRuntimeSpawnPython = () => ({ success: true, process: null, pid: 0 });
support.frameRuntimeSendCommand = () => true;
support.frameRuntimeSetEnv = () => {};
support.frameRuntimeMapSet = (obj, key, val) => { if (obj && typeof obj === 'object') obj[key] = val; };
global.frameRuntimeMapSet = support.frameRuntimeMapSet;
support.frameRuntimeSendEvent = (event, body) => sentEvents.push({ event, body });
global.frameRuntimeSendEvent = support.frameRuntimeSendEvent;
support.frameRuntimeSendResponse = () => {};
global.frameRuntimeSendResponse = support.frameRuntimeSendResponse;
support.frameRuntimeGetMapSize = obj => (obj && typeof obj === 'object' ? Object.keys(obj).length : 0);
support.frameRuntimeMapHasKey = (obj, key) => !!(obj && Object.prototype.hasOwnProperty.call(obj, key));
support.frameRuntimeMapKeys = obj => (obj && typeof obj === 'object' ? Object.keys(obj) : []);
support.frameRuntimeMapGet = (obj, key) => (obj && typeof obj === 'object' ? obj[key] : undefined);

const { FrameDebugAdapter } = require(path.join(process.cwd(), 'dist/fda_adapter/adapter.js'));
if (!FrameDebugAdapter) {
  console.error('EVENT_ROUTING_SMOKE_FAIL: FrameDebugAdapter export not found');
  process.exit(1);
}

function newAdapter() {
  const a = new FrameDebugAdapter();
  a.createTcpServer = function stubCreateServer() { this.debugPort = 12345; this.debugServer = {}; return true; };
  a.transpileFrameFile = function stubTranspileFile() { this.frameSourceMap = {}; this.framePythonCode = "print('stub')"; this.debugRuntimeCode = "print('stub')"; return true; };
  a.spawnFramePython = function stubSpawnPython() { return true; };
  a.sendCommand = function stubSendCommand() { return true; };
  a['$']();
  return a;
}

function assert(condition, msg) {
  if (!condition) {
    console.error(msg);
    process.exit(1);
  }
}

// Scenario 1: WaitingForConnection event routing
sentEvents = [];
let adapter = newAdapter();
adapter.initialize({});
adapter.launch({ program: '/tmp/stub.frm', stopOnEntry: false });
adapter.onPythonExecutionPaused('breakpoint', 7);
adapter.onPythonExecutionResumed();
adapter.onPythonTerminated(99);

let stoppedEvt = sentEvents.find(e => e.event === 'stopped');
let continuedEvt = sentEvents.find(e => e.event === 'continued');
let terminatedEvt = sentEvents.find(e => e.event === 'terminated');

assert(stoppedEvt && stoppedEvt.body.reason === 'breakpoint' && stoppedEvt.body.threadId === 1, 'WaitingForConnection stopped event missing/incorrect');
assert(continuedEvt && continuedEvt.body.threadId === 1, 'WaitingForConnection continued event missing');
assert(terminatedEvt && terminatedEvt.body.exitCode === 99, 'WaitingForConnection terminated event missing/incorrect');

// Scenario 2: Connected event routing
sentEvents = [];
adapter = newAdapter();
adapter.initialize({});
adapter.launch({ program: '/tmp/stub.frm', stopOnEntry: false });
adapter.onPythonConnected();
adapter.onPythonExecutionPaused('step', 3);
adapter.onPythonExecutionResumed();
adapter.onPythonTerminated(0);

stoppedEvt = sentEvents.find(e => e.event === 'stopped');
continuedEvt = sentEvents.find(e => e.event === 'continued');
terminatedEvt = sentEvents.find(e => e.event === 'terminated');

assert(stoppedEvt && stoppedEvt.body.reason === 'step' && stoppedEvt.body.threadId === 1, 'Connected stopped event missing/incorrect');
assert(continuedEvt && continuedEvt.body.threadId === 1, 'Connected continued event missing');
assert(terminatedEvt && terminatedEvt.body.exitCode === 0, 'Connected terminated event missing/incorrect');

console.log('EVENT_ROUTING_SMOKE_OK');
process.exit(0);
