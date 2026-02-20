class HSMDefaultForwardFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class HSMDefaultForwardCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: HSMDefaultForwardCompartment | null;

    constructor(state: string, parent_compartment: HSMDefaultForwardCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): HSMDefaultForwardCompartment {
        const c = new HSMDefaultForwardCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class HSMDefaultForward {
    private _state_stack: Array<any>;
    private __compartment: HSMDefaultForwardCompartment;
    private __next_compartment: HSMDefaultForwardCompartment | null;
    private _return_value: any;
    private log: string[] =     [];

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.log =         [];
        this.__compartment = new HSMDefaultForwardCompartment("Child");
        this.__next_compartment = null;
        const __frame_event = new HSMDefaultForwardFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: HSMDefaultForwardFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new HSMDefaultForwardFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMDefaultForwardFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMDefaultForwardFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: HSMDefaultForwardFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: HSMDefaultForwardCompartment) {
        this.__next_compartment = next_compartment;
    }

    public handled_event() {
        const __e = new HSMDefaultForwardFrameEvent("handled_event", null);
        this.__kernel(__e);
    }

    public unhandled_event() {
        const __e = new HSMDefaultForwardFrameEvent("unhandled_event", null);
        this.__kernel(__e);
    }

    public get_log(): string[] {
        this._return_value = null;
        const __e = new HSMDefaultForwardFrameEvent("get_log", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Parent(__e: HSMDefaultForwardFrameEvent) {
        if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "handled_event") {
            this.log.push("Parent:handled_event")
        } else if (__e._message === "unhandled_event") {
            this.log.push("Parent:unhandled_event")
        }
    }

    private _state_Child(__e: HSMDefaultForwardFrameEvent) {
        if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "handled_event") {
            this.log.push("Child:handled_event")
        } else {
            this._state_Parent(__e);
        }
    }
}


function main(): void {
    console.log("=== Test: HSM State-Level Default Forward ===");
    const s = new HSMDefaultForward();

    s.handled_event();
    let log = s.get_log();
    if (!log.includes("Child:handled_event")) {
        throw new Error(`Expected 'Child:handled_event' in log, got ${log}`);
    }
    console.log(`After handled_event: ${JSON.stringify(log)}`);

    s.unhandled_event();
    log = s.get_log();
    if (!log.includes("Parent:unhandled_event")) {
        throw new Error(`Expected 'Parent:unhandled_event' in log (forwarded), got ${log}`);
    }
    console.log(`After unhandled_event (forwarded): ${JSON.stringify(log)}`);

    console.log("PASS: HSM state-level default forward works correctly");
}

main();
