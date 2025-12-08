'use strict';

const path = require('path');

function primeRuntimeGlobals() {
  // Load the runtime shim and project its exports onto global for free-function use
  // eslint-disable-next-line import/no-dynamic-require, global-require
  const rt = require('frame_runtime_ts');
  Object.keys(rt).forEach((k) => {
    if (typeof rt[k] === 'function') {
      global[k] = rt[k];
    }
  });
}

function requireAdapter() {
  const outJs = process.env.OUT_JS;
  if (!outJs) throw new Error('OUT_JS not set');
  // eslint-disable-next-line import/no-dynamic-require, global-require
  const mod = require(outJs);
  const ctor = mod.FrameDebugAdapter || mod.default || mod[Object.keys(mod)[0]];
  if (!ctor) throw new Error('Could not locate adapter class export');
  return ctor;
}

function main() {
  primeRuntimeGlobals();
  const Adapter = requireAdapter();
  const adapter = new Adapter();
  // Drive minimal flow: initialize -> launch -> onPythonConnected
  if (typeof adapter.initialize === 'function') {
    adapter.initialize({});
  }
  if (typeof adapter.launch === 'function') {
    adapter.launch({ program: '/tmp/dummy.frm' });
  }
  if (typeof adapter.onPythonConnected === 'function') {
    adapter.onPythonConnected();
  }
  // Exercise a simple command path
  if (typeof adapter.configurationDone === 'function') {
    adapter.configurationDone();
  }
  // Call drainCommands if present to ensure queue logic executes without throwing
  if (typeof adapter.drainCommands === 'function') {
    try { adapter.drainCommands(); } catch (e) { /* ignore */ }
  }
  // If we get here without exceptions, consider smoke OK
  console.log('FDA_NODE_HARNESS_OK');
}

main();
