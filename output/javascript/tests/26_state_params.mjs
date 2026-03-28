
export class StateParamsFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class StateParamsFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class StateParamsCompartment {
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
        const c = new StateParamsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class StateParams {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new StateParamsCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new StateParamsFrameEvent("$>", null);
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
            const exit_event = new StateParamsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new StateParamsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new StateParamsFrameEvent("$>", this.__compartment.enter_args);
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

    start(val) {
        const __e = new StateParamsFrameEvent("start", {"val": val});
        const __ctx = new StateParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_value() {
        const __e = new StateParamsFrameEvent("get_value", null);
        const __ctx = new StateParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
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
            // Access state param via compartment - using string key "0"
            __sv_comp.state_vars["count"] = this.__compartment.state_args["0"];
            const count_val = __sv_comp.state_vars["count"]
            console.log(`Counter entered with initial=${count_val}`)
        } else if (__e._message === "get_value") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["count"];
            return;
        }
    }

    _state_Idle(__e) {
        if (__e._message === "get_value") {
            this._context_stack[this._context_stack.length - 1]._return = 0;
            return;
        } else if (__e._message === "start") {
            const val = __e._parameters?.["val"];
            const __compartment = new StateParamsCompartment("Counter", this.__compartment.copy());
            __compartment.state_args = {"0": val};
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("=== Test 26: State Parameters ===")
    const s = new StateParams()

    let val = s.get_value()
    if (val !== 0) {
        throw new Error(`Expected 0 in Idle, got ${val}`)
    }
    console.log(`Initial value: ${val}`)

    s.start(42)
    val = s.get_value()
    if (val !== 42) {
        throw new Error(`Expected 42 in Counter from state param, got ${val}`)
    }
    console.log(`Value after transition: ${val}`)

    console.log("PASS: State parameters work correctly")
}

main()
