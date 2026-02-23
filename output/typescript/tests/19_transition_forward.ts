class EventForwardTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class EventForwardTestFrameContext {
    public event: EventForwardTestFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: EventForwardTestFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class EventForwardTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: EventForwardTestCompartment | null;

    constructor(state: string, parent_compartment: EventForwardTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): EventForwardTestCompartment {
        const c = new EventForwardTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class EventForwardTest {
    private _state_stack: Array<any>;
    private __compartment: EventForwardTestCompartment;
    private __next_compartment: EventForwardTestCompartment | null;
    private _context_stack: Array<any>;
    private log: string[] =     [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.log =         [];
        this.__compartment = new EventForwardTestCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new EventForwardTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: EventForwardTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new EventForwardTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new EventForwardTestFrameEvent("$>", this.__compartment.enter_args);
                this.__router(enter_event);
            } else {
                // Forward event to new state
                const forward_event = next_compartment.forward_event;
                next_compartment.forward_event = null;
                if (forward_event._message === "$>") {
                    // Forwarding enter event - just send it
                    this.__router(forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    const enter_event = new EventForwardTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: EventForwardTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: EventForwardTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public process() {
        const __e = new EventForwardTestFrameEvent("process", null);
        const __ctx = new EventForwardTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_log(): string[] {
        const __e = new EventForwardTestFrameEvent("get_log", null);
        const __ctx = new EventForwardTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Working(__e: EventForwardTestFrameEvent) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "process") {
            this.log.push("working:process");
        }
    }

    private _state_Idle(__e: EventForwardTestFrameEvent) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "process") {
            this.log.push("idle:process:before");
            const __compartment = new EventForwardTestCompartment("Working", this.__compartment.copy());
            __compartment.forward_event = __e;
            this.__transition(__compartment);
            return;
            // This should NOT execute because -> => returns after dispatch
            this.log.push("idle:process:after");
        }
    }
}


function main(): void {
    console.log("=== Test 19: Transition Forward (TypeScript) ===");
    const s = new EventForwardTest();
    s.process();
    const log = s.get_log();
    console.log(`Log: ${JSON.stringify(log)}`);

    // After transition-forward:
    // - Idle logs "idle:process:before"
    // - Transition to Working
    // - Working handles process(), logs "working:process"
    // - Return prevents "idle:process:after"
    if (!log.includes("idle:process:before")) {
        throw new Error(`Expected 'idle:process:before' in log: ${log}`);
    }
    if (!log.includes("working:process")) {
        throw new Error(`Expected 'working:process' in log: ${log}`);
    }
    if (log.includes("idle:process:after")) {
        throw new Error(`Should NOT have 'idle:process:after' in log: ${log}`);
    }

    console.log("PASS: Transition forward works correctly");
}

main();
