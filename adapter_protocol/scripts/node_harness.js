/* eslint-disable */
const assert = (c,m)=>{ if(!c) throw new Error(m); };
const path = require('path');
const OUT_JS = process.env.OUT_JS;
if (!OUT_JS) throw new Error('OUT_JS not set');
const { AdapterProtocol } = require(OUT_JS);

const fsm = new AdapterProtocol();
// start → drain empty
fsm.start();
let cmds = fsm.drainCommands();
assert(Array.isArray(cmds) && cmds.length === 0, 'queue should be empty before connection');
// runtimeConnected → initialize + ping
fsm.runtimeConnected();
cmds = fsm.drainCommands();
const acts = cmds.map(c=>c&&c.action);
assert(acts.includes('initialize') && acts.includes('ping'), 'expected initialize+ping');
// guarded before ready → deferred
fsm.enqueueCommand('continue', {});
cmds = fsm.drainCommands();
assert(Array.isArray(cmds) && cmds.length === 0, 'guarded should defer before ready');
// hello + ready → single continue after enqueue
fsm.runtimeMessage({ event: 'hello', type:'event', data: { message:'ready' } });
fsm.runtimeMessage({ event: 'ready', type:'event', data: {} });
fsm.enqueueCommand('continue', {});
cmds = fsm.drainCommands();
assert(cmds.filter(c=>c&&c.action==='continue').length === 1, 'single continue after ready');
// while pendingAction, guard subsequent step/continue
fsm.enqueueCommand('next', {});
fsm.enqueueCommand('stepIn', {});
fsm.enqueueCommand('pause', {});
cmds = fsm.drainCommands();
assert(Array.isArray(cmds) && cmds.length === 0, 'no guarded commands while pendingAction');
// stop event clears pending; next should be accepted
fsm.runtimeMessage({ event: 'stopped', type:'event', data: { reason:'breakpoint', threadId: 1 } });
fsm.enqueueCommand('next', {});
cmds = fsm.drainCommands();
assert(cmds.filter(c=>c&&c.action==='next').length === 1, 'next accepted after pending cleared');
// stopped sets isPaused
fsm.runtimeMessage({ event: 'stopped', type:'event', data: { reason:'pause', threadId:1 } });
assert(fsm.isPaused === true, 'isPaused should be true on stopped');
console.log('ADAPTER_SMOKE_OK');
