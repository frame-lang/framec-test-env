@target typescript

system AdapterProtocol {
    
    interface:
        start()
        runtimeConnected()
        runtimeMessage(payload)
        runtimeDisconnected()
        requestTerminate()
        drainCommands()
    
    machine:
        $Idle {
            start() {
                this.commandQueue = []
                this.pingCounter = 0
                this.handshakeComplete = false
                this.isReady = false
                this.pendingAction = false
                this.deferredQueue = []
                this.isPaused = false
                this.lastStoppedReason = ""
                this.lastThreadId = 0
                this.lastOutput = ""
                this.lifecycle = "waiting"
                this.debuggerId = "rebuild-harness"
                -> $WaitingForConnection
            }

            runtimeConnected() {
                // Ignore until started
            }

            runtimeMessage(payload) {
                // Ignore until started
            }

            runtimeDisconnected() {
                this.lifecycle = "terminated"
                -> $Terminated
            }

            requestTerminate() {
                // Nothing to terminate yet
            }

            drainCommands() {
                return this.flushCommands()
            }
        }

        $WaitingForConnection {
            runtimeConnected() {
                this.lifecycle = "connected"
                this.handshakeComplete = false
                this.pingCounter = this.pingCounter + 1
                this.enqueueCommand("initialize", {"debugger": this.debuggerId})
                this.enqueueCommand("ping", {"sequence": this.pingCounter})
                -> $Connected
            }

            runtimeMessage(payload) {
                // Ignore stray messages until connection confirmed
            }

            runtimeDisconnected() {
                this.lifecycle = "terminated"
                -> $Terminated
            }

            requestTerminate() {
                this.lifecycle = "terminated"
                -> $Terminated
            }

            drainCommands() {
                return this.flushCommands()
            }
        }

        $Connected {
            runtimeMessage(payload) {
                this.handleConnectedMessage(payload)
                if (this.lifecycle === "terminated") {
                    -> $Terminated
                }
            }

            runtimeDisconnected() {
                this.lifecycle = "terminated"
                -> $Terminated
            }

            requestTerminate() {
                this.enqueueCommand("terminate", {"reason": "requested"})
                this.lifecycle = "terminating"
                -> $Terminating
            }

            drainCommands() {
                return this.flushCommands()
            }
        }

        $Terminating {
            runtimeMessage(payload) {
                this.handleTerminatingMessage(payload)
                if (this.lifecycle === "terminated") {
                    -> $Terminated
                }
            }

            runtimeDisconnected() {
                this.lifecycle = "terminated"
                -> $Terminated
            }

            requestTerminate() {
                // Already terminating
            }

            drainCommands() {
                return this.flushCommands()
            }
        }

        $Terminated {
            start() {
                // Ignore attempts to restart
            }

            runtimeConnected() {
                // Ignore new runtime connections
            }

            runtimeMessage(payload) {
                // Ignore messages once terminated
            }

            runtimeDisconnected() {
                // Already terminated
            }

            requestTerminate() {
                // Already terminated
            }

            drainCommands() {
                return this.flushCommands()
            }
        }
    
    actions:
        enqueueCommand(action, data) {
            const guarded: Record<string, boolean> = { continue: true, next: true, stepIn: true, stepOut: true, pause: true };
            const entry = { type: "command", action, data } as any;
            if (guarded[action]) {
                if (this.isReady !== true || this.handshakeComplete !== true) {
                    if (Array.isArray(this.deferredQueue) && this.deferredQueue.some((e: any) => e && e.action === action)) {
                        return;
                    }
                    this.deferredQueue.push(entry);
                    return;
                }
                if (this.pendingAction === true) {
                    return;
                }
                this.pendingAction = true;
            } else if (action === "setBreakpoints") {
                if (this.isReady !== true || this.handshakeComplete !== true) {
                    if (Array.isArray(this.deferredQueue) && this.deferredQueue.some((e: any) => e && e.action === action)) {
                        return;
                    }
                    this.deferredQueue.push(entry);
                    return;
                }
            }
            this.commandQueue.push(entry);
        }

        flushCommands() {
            const queued = this.commandQueue;
            this.commandQueue = [];
            return queued;
        }

        handleConnectedMessage(payload) {
            const eventType = payload["event"];
            if (eventType === "hello") {
                this.handshakeComplete = true;
                this.lastOutput = "runtime ready";
            } else if (eventType === "output") {
                this.lastOutput = payload["data"]["output"];
            } else if (eventType === "ready") {
                this.isReady = true;
                if (this.deferredQueue && this.deferredQueue.length > 0) {
                    for (const e of this.deferredQueue) {
                        this.commandQueue.push(e);
                    }
                    this.deferredQueue = [];
                }
            } else if (eventType === "continued") {
                this.pendingAction = false;
                this.isPaused = false;
            } else if (eventType === "stopped") {
                this.pendingAction = false;
                this.isPaused = true;
                try {
                    this.lastStoppedReason = payload["data"]["reason"];
                    this.lastThreadId = payload["data"]["threadId"];
                } catch (_e) {
                    // ignore
                }
            } else if (eventType === "terminated") {
                this.lifecycle = "terminated";
                this.isPaused = false;
                this.commandQueue = [];
                this.deferredQueue = [];
            }
        }

        handleTerminatingMessage(payload) {
            const eventType = payload["event"];
            if (eventType === "terminated") {
                this.lifecycle = "terminated";
            }
        }

    domain:
        commandQueue = []
        pingCounter = 0
        handshakeComplete = false
        isReady = false
        pendingAction = false
        deferredQueue = []
        isPaused = false
        lastStoppedReason = ""
        lastThreadId = 0
        lastOutput = ""
        lifecycle = "waiting"
        debuggerId = "rebuild-harness"
}

