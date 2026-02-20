class TransitionEnterArgsFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class TransitionEnterArgsCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: TransitionEnterArgsCompartment | null;

    constructor(state: string, parent_compartment: TransitionEnterArgsCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): TransitionEnterArgsCompartment {
        const c = new TransitionEnterArgsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class TransitionEnterArgs {
    private _state_stack: Array<any>;
    private __compartment: TransitionEnterArgsCompartment;
    private __next_compartment: TransitionEnterArgsCompartment | null;
    private _return_value: any;
    private log: string[] =     [];

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.log =         [];
        this.__compartment = new TransitionEnterArgsCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new TransitionEnterArgsFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: TransitionEnterArgsFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new TransitionEnterArgsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new TransitionEnterArgsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new TransitionEnterArgsFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: TransitionEnterArgsFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: TransitionEnterArgsCompartment) {
        this.__next_compartment = next_compartment;
    }

    public start() {
        const __e = new TransitionEnterArgsFrameEvent("start", null);
        this.__kernel(__e);
    }

    public get_log(): string[] {
        this._return_value = null;
        const __e = new TransitionEnterArgsFrameEvent("get_log", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Active(__e: TransitionEnterArgsFrameEvent) {
        if (__e._message === "$>") {
            const source = __e._parameters?.["0"];
            const value = __e._parameters?.["1"];
            this.log.push(`active:enter:${source}:${value}`);
        } else if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "start") {
            this.log.push("active:start");
        }
    }

    private _state_Idle(__e: TransitionEnterArgsFrameEvent) {
        if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "start") {
            this.log.push("idle:start");
            const __compartment = new TransitionEnterArgsCompartment("Active");
            __compartment.enter_args = Object.fromEntries(["from_idle", 42].map((v, i) => [String(i), v]));
            this.__transition(__compartment);
        }
    }
}


function main() {
    console.log("=== Test 17: Transition Enter Args ===");
    const s = new TransitionEnterArgs();

    // Initial state is Idle
    let log = s.get_log();
    if (log.length !== 0) {
        throw new Error(`Expected empty log, got ${JSON.stringify(log)}`);
    }

    // Transition to Active with args
    s.start();
    log = s.get_log();
    if (!log.includes("idle:start")) {
        throw new Error(`Expected 'idle:start' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("active:enter:from_idle:42")) {
        throw new Error(`Expected 'active:enter:from_idle:42' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`Log after transition: ${JSON.stringify(log)}`);

    console.log("PASS: Transition enter args work correctly");
}

main();
