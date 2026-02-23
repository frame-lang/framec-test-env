class StateVarBasicFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class StateVarBasicFrameContext {
    public event: StateVarBasicFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: StateVarBasicFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class StateVarBasicCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: StateVarBasicCompartment | null;

    constructor(state: string, parent_compartment: StateVarBasicCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): StateVarBasicCompartment {
        const c = new StateVarBasicCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class StateVarBasic {
    private _state_stack: Array<any>;
    private __compartment: StateVarBasicCompartment;
    private __next_compartment: StateVarBasicCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new StateVarBasicCompartment("Counter");
        this.__next_compartment = null;
        const __frame_event = new StateVarBasicFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: StateVarBasicFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new StateVarBasicFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new StateVarBasicFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new StateVarBasicFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: StateVarBasicFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: StateVarBasicCompartment) {
        this.__next_compartment = next_compartment;
    }

    public increment(): number {
        const __e = new StateVarBasicFrameEvent("increment", null);
        const __ctx = new StateVarBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_count(): number {
        const __e = new StateVarBasicFrameEvent("get_count", null);
        const __ctx = new StateVarBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public reset() {
        const __e = new StateVarBasicFrameEvent("reset", null);
        const __ctx = new StateVarBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    private _state_Counter(__e: StateVarBasicFrameEvent) {
        if (__e._message === "$>") {
            this.__compartment.state_vars["count"] = 0;
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = this.__compartment.state_vars["count"];
            return;;
        } else if (__e._message === "increment") {
            this.__compartment.state_vars["count"] = this.__compartment.state_vars["count"] + 1;
            this._context_stack[this._context_stack.length - 1]._return = this.__compartment.state_vars["count"];
            return;;
        } else if (__e._message === "reset") {
            this.__compartment.state_vars["count"] = 0;
        }
    }
}


function main() {
    console.log("=== Test 10: State Variable Basic ===");
    const s = new StateVarBasic();

    // Initial value should be 0
    if (s.get_count() !== 0) {
        throw new Error(`Expected 0, got ${s.get_count()}`);
    }
    console.log(`Initial count: ${s.get_count()}`);

    // Increment should return new value
    let result = s.increment();
    if (result !== 1) {
        throw new Error(`Expected 1 after first increment, got ${result}`);
    }
    console.log(`After first increment: ${result}`);

    // Second increment
    result = s.increment();
    if (result !== 2) {
        throw new Error(`Expected 2 after second increment, got ${result}`);
    }
    console.log(`After second increment: ${result}`);

    // Reset should set back to 0
    s.reset();
    if (s.get_count() !== 0) {
        throw new Error(`Expected 0 after reset, got ${s.get_count()}`);
    }
    console.log(`After reset: ${s.get_count()}`);

    console.log("PASS: State variable basic operations work correctly");
}

main();
