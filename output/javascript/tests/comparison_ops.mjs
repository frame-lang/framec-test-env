
// Test: Comparison operators in Frame handlers
// Tests: >, <, >=, <=, ==, !=

export class ComparisonTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class ComparisonTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class ComparisonTestCompartment {
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
        const c = new ComparisonTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class ComparisonTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    a = 5;
    b = 3;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new ComparisonTestCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new ComparisonTestFrameEvent("$>", null);
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
            const exit_event = new ComparisonTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ComparisonTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new ComparisonTestFrameEvent("$>", this.__compartment.enter_args);
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

    test_greater() {
        const __e = new ComparisonTestFrameEvent("test_greater", null);
        const __ctx = new ComparisonTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    test_less() {
        const __e = new ComparisonTestFrameEvent("test_less", null);
        const __ctx = new ComparisonTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    test_greater_equal() {
        const __e = new ComparisonTestFrameEvent("test_greater_equal", null);
        const __ctx = new ComparisonTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    test_less_equal() {
        const __e = new ComparisonTestFrameEvent("test_less_equal", null);
        const __ctx = new ComparisonTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    test_equal() {
        const __e = new ComparisonTestFrameEvent("test_equal", null);
        const __ctx = new ComparisonTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    test_not_equal() {
        const __e = new ComparisonTestFrameEvent("test_not_equal", null);
        const __ctx = new ComparisonTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    set_values(x, y) {
        const __e = new ComparisonTestFrameEvent("set_values", {"x": x, "y": y});
        const __ctx = new ComparisonTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Ready(__e) {
        if (__e._message === "set_values") {
            const x = __e._parameters?.["x"];
            const y = __e._parameters?.["y"];
            this.a = x;
            this.b = y;
        } else if (__e._message === "test_equal") {
            if (this.a == this.b) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        } else if (__e._message === "test_greater") {
            if (this.a > this.b) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        } else if (__e._message === "test_greater_equal") {
            if (this.a >= this.b) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        } else if (__e._message === "test_less") {
            if (this.a < this.b) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        } else if (__e._message === "test_less_equal") {
            if (this.a <= this.b) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        } else if (__e._message === "test_not_equal") {
            if (this.a != this.b) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        }
    }
}

function main() {
    console.log("TAP version 14");
    console.log("1..6");

    const s = new ComparisonTest();

    // a=5, b=3: 5 > 3 is true
    if (s.test_greater()) {
        console.log("ok 1 - 5 > 3 is true");
    } else {
        console.log("not ok 1 - 5 > 3 is true");
    }

    // a=5, b=3: 5 < 3 is false
    if (!s.test_less()) {
        console.log("ok 2 - 5 < 3 is false");
    } else {
        console.log("not ok 2 - 5 < 3 is false");
    }

    // a=5, b=3: 5 >= 3 is true
    if (s.test_greater_equal()) {
        console.log("ok 3 - 5 >= 3 is true");
    } else {
        console.log("not ok 3 - 5 >= 3 is true");
    }

    // a=5, b=3: 5 <= 3 is false
    if (!s.test_less_equal()) {
        console.log("ok 4 - 5 <= 3 is false");
    } else {
        console.log("not ok 4 - 5 <= 3 is false");
    }

    // a=5, b=3: 5 == 3 is false
    if (!s.test_equal()) {
        console.log("ok 5 - 5 == 3 is false");
    } else {
        console.log("not ok 5 - 5 == 3 is false");
    }

    // a=5, b=3: 5 != 3 is true
    if (s.test_not_equal()) {
        console.log("ok 6 - 5 != 3 is true");
    } else {
        console.log("not ok 6 - 5 != 3 is true");
    }
}

main();
