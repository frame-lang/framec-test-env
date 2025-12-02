/* Node harness for AdapterProtocolMinimal.
 *
 * This mirrors the Bug #081 validator flow in a hermetic, in-repo form:
 * - start() → drainCommands() → expect empty queue
 * - runtimeConnected() → drainCommands() → expect initialize+ping
 * - guarded command before ready → expect deferral (drain empty)
 * - hello/ready + continue → expect single continue
 * - stopped event → expect isPaused === true and stopped metadata populated
 */
/* eslint-disable @typescript-eslint/no-var-requires */
const assert = (cond, msg) => {
    if (!cond) {
        throw new Error(msg);
    }
};
// OUT_JS is injected by run_adapter_smoke.sh
const outJs = process.env.OUT_JS;
if (!outJs) {
    throw new Error("OUT_JS environment variable must point to adapter_protocol_minimal.js");
}
// eslint-disable-next-line @typescript-eslint/no-var-requires
const mod = require(outJs);
const AdapterProtocolCtor = mod.AdapterProtocol || mod.AdapterProtocolMinimal;
if (!AdapterProtocolCtor) {
    throw new Error("Expected AdapterProtocol export (or AdapterProtocolMinimal) from generated JS");
}
const fsm = new AdapterProtocolCtor();
// Helper: host-level drain that reads and clears the commandQueue domain field.
const drain = () => {
    const q = Array.isArray(fsm.commandQueue)
        ? fsm.commandQueue.slice()
        : [];
    fsm.commandQueue = [];
    return q;
};
// 1) start → drain: expect empty
fsm.start();
let cmds = drain();
assert(Array.isArray(cmds) && cmds.length === 0, "queue should be empty before connection");
// 2) runtimeConnected → drain: expect initialize + ping
fsm.runtimeConnected();
cmds = drain();
const acts = cmds.map((c) => c && c.action);
assert(acts.includes("initialize") && acts.includes("ping"), "expected initialize+ping after runtimeConnected");
// 3) guarded before ready/handshake → deferred (no commands drained)
fsm.enqueueCommand("continue", {});
cmds = drain();
assert(cmds.length === 0, "guarded action should defer before handshake/ready");
// 4) hello + ready → then enqueue continue once; should appear once
fsm.runtimeMessage({ event: "hello", type: "event", data: { message: "ready" } });
fsm.runtimeMessage({ event: "ready", type: "event", data: {} });
fsm.enqueueCommand("continue", {});
cmds = drain();
assert(cmds.filter((c) => c && c.action === "continue").length === 1, "expected single continue enqueued after ready");
// 5) stopped should set isPaused + metadata
fsm.runtimeMessage({ event: "stopped", type: "event", data: { reason: "pause", threadId: 1 } });
assert(fsm.isPaused === true, "isPaused should be true on stopped");
assert(typeof fsm.lastStoppedReason === "string", "lastStoppedReason should be a string");
assert(typeof fsm.lastThreadId === "number", "lastThreadId should be a number");
console.log("ADAPTER_SMOKE_OK");
//# sourceMappingURL=node_harness.js.map
