
// Test: Ternary/conditional expressions in Frame handlers
// JavaScript uses: cond ? a : b

export class TernaryTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class TernaryTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class TernaryTestCompartment {
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
        const c = new TernaryTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class TernaryTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    cond = true;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new TernaryTestCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new TernaryTestFrameEvent("$>", null);
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
            const exit_event = new TernaryTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new TernaryTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new TernaryTestFrameEvent("$>", this.__compartment.enter_args);
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

    get_value() {
        const __e = new TernaryTestFrameEvent("get_value", null);
        const __ctx = new TernaryTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    set_condition(c) {
        const __e = new TernaryTestFrameEvent("set_condition", {"c": c});
        const __ctx = new TernaryTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Ready(__e) {
        if (__e._message === "get_value") {
            const result = this.cond ? 100 : 200;
            this._context_stack[this._context_stack.length - 1]._return = result;
        } else if (__e._message === "set_condition") {
            const c = __e._parameters?.["c"];
            this.cond = c;
        }
    }
}

function main() {
    console.log("TAP version 14");
    console.log("1..2");

    const s = new TernaryTest();

    // cond=true: should return 100
    const v1 = s.get_value();
    if (v1 === 100) {
        console.log("ok 1 - cond=true returns 100");
    } else {
        console.log(`not ok 1 - cond=true returns 100 # got ${v1}`);
    }

    // cond=false: should return 200
    s.set_condition(false);
    const v2 = s.get_value();
    if (v2 === 200) {
        console.log("ok 2 - cond=false returns 200");
    } else {
        console.log(`not ok 2 - cond=false returns 200 # got ${v2}`);
    }
}

main();
