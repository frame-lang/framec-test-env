class StateVarReentryFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class StateVarReentryFrameContext {
    public event: StateVarReentryFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: StateVarReentryFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class StateVarReentryCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: StateVarReentryCompartment | null;

    constructor(state: string, parent_compartment: StateVarReentryCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): StateVarReentryCompartment {
        const c = new StateVarReentryCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class StateVarReentry {
    private _state_stack: Array<any>;
    private __compartment: StateVarReentryCompartment;
    private __next_compartment: StateVarReentryCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new StateVarReentryCompartment("Counter");
        this.__next_compartment = null;
        const __frame_event = new StateVarReentryFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: StateVarReentryFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new StateVarReentryFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new StateVarReentryFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new StateVarReentryFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: StateVarReentryFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: StateVarReentryCompartment) {
        this.__next_compartment = next_compartment;
    }

    public increment(): number {
        const __e = new StateVarReentryFrameEvent("increment", null);
        const __ctx = new StateVarReentryFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_count(): number {
        const __e = new StateVarReentryFrameEvent("get_count", null);
        const __ctx = new StateVarReentryFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public go_other() {
        const __e = new StateVarReentryFrameEvent("go_other", null);
        const __ctx = new StateVarReentryFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public come_back() {
        const __e = new StateVarReentryFrameEvent("come_back", null);
        const __ctx = new StateVarReentryFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    private _state_Counter(__e: StateVarReentryFrameEvent) {
        if (__e._message === "$>") {
            if (!("count" in this.__compartment.state_vars)) {
                this.__compartment.state_vars["count"] = 0;
            }
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = this.__compartment.state_vars["count"];
            return;;
        } else if (__e._message === "go_other") {
            const __compartment = new StateVarReentryCompartment("Other", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "increment") {
            this.__compartment.state_vars["count"] = this.__compartment.state_vars["count"] + 1;
            this._context_stack[this._context_stack.length - 1]._return = this.__compartment.state_vars["count"];
            return;;
        }
    }

    private _state_Other(__e: StateVarReentryFrameEvent) {
        if (__e._message === "come_back") {
            const __compartment = new StateVarReentryCompartment("Counter", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = -1;
            return;;
        } else if (__e._message === "increment") {
            this._context_stack[this._context_stack.length - 1]._return = -1;
            return;;
        }
    }
}


function main() {
    console.log("=== Test 11: State Variable Reentry ===");
    const s = new StateVarReentry();

    // Increment a few times
    s.increment();
    s.increment();
    let count = s.get_count();
    if (count !== 2) {
        throw new Error(`Expected 2 after two increments, got ${count}`);
    }
    console.log(`Count before leaving: ${count}`);

    // Leave the state
    s.go_other();
    console.log("Transitioned to Other state");

    // Come back - state var should be reinitialized to 0
    s.come_back();
    count = s.get_count();
    if (count !== 0) {
        throw new Error(`Expected 0 after re-entering Counter (state var reinit), got ${count}`);
    }
    console.log(`Count after re-entering Counter: ${count}`);

    // Increment again to verify it works
    const result = s.increment();
    if (result !== 1) {
        throw new Error(`Expected 1 after increment, got ${result}`);
    }
    console.log(`After increment: ${result}`);

    console.log("PASS: State variables reinitialize on state reentry");
}

main();
