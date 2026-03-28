
export class StateVarPushPopFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class StateVarPushPopFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class StateVarPushPopCompartment {
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
        const c = new StateVarPushPopCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class StateVarPushPop {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new StateVarPushPopCompartment("Counter");
        this.__next_compartment = null;
        const __frame_event = new StateVarPushPopFrameEvent("$>", null);
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
        const __e = new StateVarPushPopFrameEvent("increment", null);
        const __ctx = new StateVarPushPopFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_count() {
        const __e = new StateVarPushPopFrameEvent("get_count", null);
        const __ctx = new StateVarPushPopFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    save_and_go() {
        const __e = new StateVarPushPopFrameEvent("save_and_go", null);
        const __ctx = new StateVarPushPopFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    restore() {
        const __e = new StateVarPushPopFrameEvent("restore", null);
        const __ctx = new StateVarPushPopFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Other(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Other") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("other_count" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["other_count"] = 100;
            }
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["other_count"];
            return;;
        } else if (__e._message === "increment") {
            __sv_comp.state_vars["other_count"] = __sv_comp.state_vars["other_count"] + 1;
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["other_count"];
            return;;
        } else if (__e._message === "restore") {
            this.__transition(this._state_stack.pop());
            return;
        }
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
        } else if (__e._message === "save_and_go") {
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new StateVarPushPopCompartment("Other", this.__compartment.copy());
            this.__transition(__compartment);
            return;
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
