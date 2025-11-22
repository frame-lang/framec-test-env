import { FrameEvent, FrameCompartment } from 'frame_runtime_ts'

export class AdapterProtocol {
  public commandQueue: any =  [];
  public pingCounter: any =  0;
  public handshakeComplete: any =  false;
  public isReady: any =  false;
  public pendingAction: any =  false;
  public deferredQueue: any =  [];
  public isPaused: any =  false;
  public lastStoppedReason: any =  "";
  public lastThreadId: any =  0;
  public lastOutput: any =  "";
  public lifecycle: any =  "waiting";
  public debuggerId: any =  "rebuild-harness";
  public _compartment: FrameCompartment = new FrameCompartment('__AdapterProtocol_state_Idle');
  private _stack: FrameCompartment[] = [];
  constructor(...sysParams: any[]) {
    const startCount = 0;
    const enterCount = 0;
    const startArgs = sysParams.slice(0, startCount);
    const enterArgs = sysParams.slice(startCount, startCount + enterCount);
    const domainArgs = sysParams.slice(startCount + enterCount);
    const stateArgs: any = {};
    this._compartment = new FrameCompartment('__AdapterProtocol_state_Idle', enterArgs, undefined, stateArgs);
    const enterEvent = new FrameEvent("$enter", enterArgs);
    this._frame_router(enterEvent, this._compartment);
  }
  _frame_transition(n: FrameCompartment){ this._compartment = n; const enterEvent = new FrameEvent("$enter", n.enterArgs); this._frame_router(enterEvent, n); }
  _frame_router(__e: FrameEvent, c?: FrameCompartment){ const _c = c || this._compartment; const _m = __e.message; void _c; void _m; }
  _frame_stack_push(){ this._stack.push(this._compartment); }
  _frame_stack_pop(){ const prev = this._stack.pop(); if (prev) this._frame_transition(prev); }
  public drainCommands(__e: FrameEvent, compartment: FrameCompartment): void {
    const c = compartment || this._compartment;
    switch (c.state) {
      case '__AdapterProtocol_state_Idle':
        
                        return this.flushCommands();
        
        break;
      case '__AdapterProtocol_state_WaitingForConnection':
        
                        return this.flushCommands();
        
        break;
      case '__AdapterProtocol_state_Connected':
        
                        return this.flushCommands();
        
        break;
      case '__AdapterProtocol_state_Terminating':
        
                        return this.flushCommands();
        
        break;
      case '__AdapterProtocol_state_Terminated':
        
                        return this.flushCommands();
        
        break;
    }
  }
  public requestTerminate(__e: FrameEvent, compartment: FrameCompartment): void {
    const c = compartment || this._compartment;
    switch (c.state) {
      case '__AdapterProtocol_state_Idle':
        
                        // Nothing to terminate yet;
        
        break;
      case '__AdapterProtocol_state_WaitingForConnection':
        
                        this.lifecycle = "terminated";
                                        {
                        const __frameNextCompartment_Terminated = new FrameCompartment("__AdapterProtocol_state_Terminated");
                        this._frame_transition(__frameNextCompartment_Terminated);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_Connected':
        
                        this.enqueueCommand("terminate", {"reason": "requested"});
                        this.lifecycle = "terminating";
                                        {
                        const __frameNextCompartment_Terminating = new FrameCompartment("__AdapterProtocol_state_Terminating");
                        this._frame_transition(__frameNextCompartment_Terminating);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_Terminating':
        
                        // Already terminating;
        
        break;
      case '__AdapterProtocol_state_Terminated':
        
                        // Already terminated;
        
        break;
    }
  }
  public runtimeConnected(__e: FrameEvent, compartment: FrameCompartment): void {
    const c = compartment || this._compartment;
    switch (c.state) {
      case '__AdapterProtocol_state_Idle':
        
                        // Ignore until started;
        
        break;
      case '__AdapterProtocol_state_WaitingForConnection':
        
                        this.lifecycle = "connected";
                        this.handshakeComplete = false;
                        this.pingCounter = this.pingCounter + 1;
                        this.enqueueCommand("initialize", {"debugger": this.debuggerId});
                        this.enqueueCommand("ping", {"sequence": this.pingCounter});
                                        {
                        const __frameNextCompartment_Connected = new FrameCompartment("__AdapterProtocol_state_Connected");
                        this._frame_transition(__frameNextCompartment_Connected);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_Terminated':
        
                        // Ignore new runtime connections;
        
        break;
    }
  }
  public runtimeDisconnected(__e: FrameEvent, compartment: FrameCompartment): void {
    const c = compartment || this._compartment;
    switch (c.state) {
      case '__AdapterProtocol_state_Idle':
        
                        this.lifecycle = "terminated";
                                        {
                        const __frameNextCompartment_Terminated = new FrameCompartment("__AdapterProtocol_state_Terminated");
                        this._frame_transition(__frameNextCompartment_Terminated);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_WaitingForConnection':
        
                        this.lifecycle = "terminated";
                                        {
                        const __frameNextCompartment_Terminated = new FrameCompartment("__AdapterProtocol_state_Terminated");
                        this._frame_transition(__frameNextCompartment_Terminated);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_Connected':
        
                        this.lifecycle = "terminated";
                                        {
                        const __frameNextCompartment_Terminated = new FrameCompartment("__AdapterProtocol_state_Terminated");
                        this._frame_transition(__frameNextCompartment_Terminated);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_Terminating':
        
                        this.lifecycle = "terminated";
                                        {
                        const __frameNextCompartment_Terminated = new FrameCompartment("__AdapterProtocol_state_Terminated");
                        this._frame_transition(__frameNextCompartment_Terminated);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_Terminated':
        
                        // Already terminated;
        
        break;
    }
  }
  public runtimeMessage(__e: FrameEvent, compartment: FrameCompartment, payload): void {
    const c = compartment || this._compartment;
    switch (c.state) {
      case '__AdapterProtocol_state_Idle':
        
                        // Ignore until started;
        
        break;
      case '__AdapterProtocol_state_WaitingForConnection':
        
                        // Ignore stray messages until connection confirmed;
        
        break;
      case '__AdapterProtocol_state_Connected':
        
                        this.handleConnectedMessage(payload);
                        if (this.lifecycle === "terminated") {
                                                {
                            const __frameNextCompartment_Terminated = new FrameCompartment("__AdapterProtocol_state_Terminated");
                            this._frame_transition(__frameNextCompartment_Terminated);
                            return;
                            }
        
                        }
        
        break;
      case '__AdapterProtocol_state_Terminating':
        
                        this.handleTerminatingMessage(payload);
                        if (this.lifecycle === "terminated") {
                                                {
                            const __frameNextCompartment_Terminated = new FrameCompartment("__AdapterProtocol_state_Terminated");
                            this._frame_transition(__frameNextCompartment_Terminated);
                            return;
                            }
        
                        }
        
        break;
      case '__AdapterProtocol_state_Terminated':
        
                        // Ignore messages once terminated;
        
        break;
    }
  }
  public start(__e: FrameEvent, compartment: FrameCompartment): void {
    const c = compartment || this._compartment;
    switch (c.state) {
      case '__AdapterProtocol_state_Idle':
        
                        this.commandQueue = [];
                        this.pingCounter = 0;
                        this.handshakeComplete = false;
                        this.isReady = false;
                        this.pendingAction = false;
                        this.deferredQueue = [];
                        this.isPaused = false;
                        this.lastStoppedReason = "";
                        this.lastThreadId = 0;
                        this.lastOutput = "";
                        this.lifecycle = "waiting";
                        this.debuggerId = "rebuild-harness";
                                        {
                        const __frameNextCompartment_WaitingForConnection = new FrameCompartment("__AdapterProtocol_state_WaitingForConnection");
                        this._frame_transition(__frameNextCompartment_WaitingForConnection);
                        return;
                        }
        
        
        break;
      case '__AdapterProtocol_state_Terminated':
        
                        // Ignore attempts to restart;
        
        break;
    }
  }
  public enqueueCommand(action, data): void {
    
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
  public flushCommands(): void {
    
                const queued = this.commandQueue;
                this.commandQueue = [];
                return queued;
    
  }
  public handleConnectedMessage(payload): void {
    
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
                        // ignore;
                    }
                } else if (eventType === "terminated") {
                    this.lifecycle = "terminated";
                    this.isPaused = false;
                    this.commandQueue = [];
                    this.deferredQueue = [];
                }
    
  }
  public handleTerminatingMessage(payload): void {
    
                const eventType = payload["event"];
                if (eventType === "terminated") {
                    this.lifecycle = "terminated";
                }
    
  }
}
