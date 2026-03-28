
// Test: Deeply nested braces and braces-in-strings should not confuse the body closer.

export class NestedBracesFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class NestedBracesFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class NestedBracesCompartment {
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
        const c = new NestedBracesCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class NestedBraces {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new NestedBracesCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new NestedBracesFrameEvent("$>", null);
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
            const exit_event = new NestedBracesFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new NestedBracesFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new NestedBracesFrameEvent("$>", this.__compartment.enter_args);
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

    run_test() {
        const __e = new NestedBracesFrameEvent("run_test", null);
        const __ctx = new NestedBracesFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Start(__e) {
        if (__e._message === "run_test") {
            // Object with nested braces
            const d = {outer: {inner: {deep: 1}}};

            // String containing braces
            const s1 = "string with { braces }";
            const s2 = "nested { { { braces } } }";
            const s3 = '{"json": "in string"}';

            // Template literal with braces
            const name = "world";
            const s4 = `hello ${name} with { braces }`;
            const s5 = `${{key: "value"}}`;

            // Multi-level nesting
            const result = {};
            for (let i = 0; i < 3; i++) {
                result[String(i)] = {level: i, data: {items: [1, 2, 3]}};
            }

            if (Object.keys(result).length === 3) {
                console.log("PASS: Nested braces handled correctly");
            } else {
                console.log("FAIL: Wrong result count");
                throw new Error("test failed");
            }
        }
    }
}

const s = new NestedBraces();
s.run_test();
