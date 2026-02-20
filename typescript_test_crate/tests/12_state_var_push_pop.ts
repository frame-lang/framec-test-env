class StateVarPushPopFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class StateVarPushPopCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: StateVarPushPopCompartment | null;

    constructor(state: string, parent_compartment: StateVarPushPopCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): StateVarPushPopCompartment {
        const c = new StateVarPushPopCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class StateVarPushPop {
    private _state_stack: Array<any>;
    private __compartment: StateVarPushPopCompartment;
    private __next_compartment: StateVarPushPopCompartment | null;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.__compartment = new StateVarPushPopCompartment("Counter");
        this.__next_compartment = null;
        const __frame_event = new StateVarPushPopFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: StateVarPushPopFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new StateVarPushPopFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new StateVarPushPopFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new StateVarPushPopFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: StateVarPushPopFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: StateVarPushPopCompartment) {
        this.__next_compartment = next_compartment;
    }

    public increment(): number {
        this._return_value = null;
        const __e = new StateVarPushPopFrameEvent("increment", null);
        this.__kernel(__e);
        return this._return_value;
    }

    public get_count(): number {
        this._return_value = null;
        const __e = new StateVarPushPopFrameEvent("get_count", null);
        this.__kernel(__e);
        return this._return_value;
    }

    public save_and_go() {
        const __e = new StateVarPushPopFrameEvent("save_and_go", null);
        this.__kernel(__e);
    }

    public restore() {
        const __e = new StateVarPushPopFrameEvent("restore", null);
        this.__kernel(__e);
    }

    private _state_Other(__e: StateVarPushPopFrameEvent) {
        if (__e._message === "$>") {
            this.__compartment.state_vars["other_count"] = 100;
        } else if (__e._message === "get_count") {
            this._return_value = this.__compartment.state_vars["other_count"];
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "increment") {
            this.__compartment.state_vars["other_count"] = this.__compartment.state_vars["other_count"] + 1;
            this._return_value = this.__compartment.state_vars["other_count"];
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "restore") {
            this.__compartment = this._state_stack.pop()!;
            return;
        }
    }

    private _state_Counter(__e: StateVarPushPopFrameEvent) {
        if (__e._message === "$>") {
            this.__compartment.state_vars["count"] = 0;
        } else if (__e._message === "get_count") {
            this._return_value = this.__compartment.state_vars["count"];
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "increment") {
            this.__compartment.state_vars["count"] = this.__compartment.state_vars["count"] + 1;
            this._return_value = this.__compartment.state_vars["count"];
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "save_and_go") {
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new StateVarPushPopCompartment("Other");
            this.__transition(__compartment);
        }
    }
}


function main() {
    console.log("=== Test 12: State Variable Push/Pop ===");
    const s = new StateVarPushPop();

    // Increment counter to 3
    s.increment();
    s.increment();
    s.increment();
    let count = s.get_count();
    if (count !== 3) {
        throw new Error(`Expected 3, got ${count}`);
    }
    console.log(`Counter before push: ${count}`);

    // Push and go to Other state
    s.save_and_go();
    console.log("Pushed and transitioned to Other");

    // In Other state, count should be 100 (Other's state var)
    count = s.get_count();
    if (count !== 100) {
        throw new Error(`Expected 100 in Other state, got ${count}`);
    }
    console.log(`Other state count: ${count}`);

    // Increment in Other
    s.increment();
    count = s.get_count();
    if (count !== 101) {
        throw new Error(`Expected 101 after increment, got ${count}`);
    }
    console.log(`Other state after increment: ${count}`);

    // Pop back - should restore Counter with count=3
    s.restore();
    console.log("Popped back to Counter");

    count = s.get_count();
    if (count !== 3) {
        throw new Error(`Expected 3 after pop (preserved), got ${count}`);
    }
    console.log(`Counter after pop: ${count}`);

    // Increment to verify it works
    s.increment();
    count = s.get_count();
    if (count !== 4) {
        throw new Error(`Expected 4, got ${count}`);
    }
    console.log(`Counter after increment: ${count}`);

    console.log("PASS: State variables preserved across push/pop");
}

main();
