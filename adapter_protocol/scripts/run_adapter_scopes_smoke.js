#!/usr/bin/env node
/**
 * Adapter scopes/variables/evaluate/stackTrace smoke without sockets.
 * Ensures handlers return plausible shapes when paused.
 */
const path = require('path');

// Load support to register globals
process.env.NODE_PATH = [
  path.join(process.cwd(), 'dist/node_modules'),
  process.env.NODE_PATH || ''
].filter(Boolean).join(path.delimiter);
require('module').Module._initPaths();

const support = require(path.join(process.cwd(), 'dist/out/src/debug/state_machines/FrameRuntimeSupport.js'));
support.frameRuntimeMapSet = (obj, key, val) => { if (obj && typeof obj === 'object') obj[key] = val; };
global.frameRuntimeMapSet = support.frameRuntimeMapSet;

const { FrameDebugAdapter } = require(path.join(process.cwd(), 'dist/adapter.js'));
const { FrameCompartment } = require('frame_runtime_ts');

if (!FrameDebugAdapter || !FrameCompartment) {
  console.error('ADAPTER_SCOPES_SMOKE_FAIL: adapter/frame_runtime_ts not found');
  process.exit(1);
}

const adapter = new FrameDebugAdapter();
adapter['$']();

// Move directly to Connected with stub state
adapter.frameFile = '/tmp/scopes_smoke.frm';
adapter._frame_transition(new FrameCompartment("__FrameDebugAdapter_state_Connected"));

// Simulate paused state
adapter.onPythonExecutionPaused('entry', 3);

// Scopes
const scopesResp = adapter.scopes(1);
const scopes = scopesResp.scopes || scopesResp?.scopes || [];
if (!Array.isArray(scopes) || scopes.length === 0) {
  console.error('ADAPTER_SCOPES_SMOKE_FAIL: scopes empty');
  process.exit(1);
}

// Variables for first scope
const varRef = scopes[0].variablesReference;
const varsResp = adapter.variables(varRef);
const vars = varsResp.variables || varsResp?.variables || [];
if (!Array.isArray(vars)) {
  console.error('ADAPTER_SCOPES_SMOKE_FAIL: variables not array');
  process.exit(1);
}

// Evaluate
const evalResp = adapter.evaluate('1+2', 1, 'repl');
if (!evalResp || typeof evalResp.result !== 'string') {
  console.error('ADAPTER_SCOPES_SMOKE_FAIL: evaluate missing result');
  process.exit(1);
}

// Stack trace (may be empty, but should return object)
const trace = adapter.stackTrace(1, 0, 20);
if (!trace || !Array.isArray(trace.stackFrames)) {
  console.error('ADAPTER_SCOPES_SMOKE_FAIL: stackTrace missing stackFrames');
  process.exit(1);
}

console.log('ADAPTER_SCOPES_SMOKE_OK');
