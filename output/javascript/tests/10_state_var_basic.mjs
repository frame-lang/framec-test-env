
export class StateVarBasicFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class StateVarBasicFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class StateVarBasicCompartment {
    state;
    state_args;
    state_vars;
    enter_args;
    exit_args;
    forward_event;
    parent_compartment;

    constructor(state, parent_compartment = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    copy() {
        const c = new StateVarBasicCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class StateVarBasic {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new StateVarBasicCompartment("Counter");
        this.__next_compartment = null;
        const __frame_event = new StateVarBasicFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    __kernel(__e) {
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

    __router(__e) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = this[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    __transition(next_compartment) {
        this.__next_compartment = next_compartment;
    }

    increment() {
        const __e = new StateVarBasicFrameEvent("increment", null);
        const __ctx = new StateVarBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_count() {
        const __e = new StateVarBasicFrameEvent("get_count", null);
        const __ctx = new StateVarBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    reset() {
        const __e = new StateVarBasicFrameEvent("reset", null);
        const __ctx = new StateVarBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Counter(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Counter") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("count" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["count"] = 0;
            }
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["count"];
            return;;
        } else if (__e._message === "increment") {
            __sv_comp.state_vars["count"] = __sv_comp.state_vars["count"] + 1;
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["count"];
            return;;
        } else if (__e._message === "reset") {
            __sv_comp.state_vars["count"] = 0;
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
