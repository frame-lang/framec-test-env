
// Test: Logical operators in Frame handlers
// Tests: &&, ||, !

export class LogicalTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class LogicalTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class LogicalTestCompartment {
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
        const c = new LogicalTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class LogicalTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    a = true;
    b = false;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new LogicalTestCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new LogicalTestFrameEvent("$>", null);
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
            const exit_event = new LogicalTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new LogicalTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new LogicalTestFrameEvent("$>", this.__compartment.enter_args);
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

    test_and() {
        const __e = new LogicalTestFrameEvent("test_and", null);
        const __ctx = new LogicalTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    test_or() {
        const __e = new LogicalTestFrameEvent("test_or", null);
        const __ctx = new LogicalTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    test_not() {
        const __e = new LogicalTestFrameEvent("test_not", null);
        const __ctx = new LogicalTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    set_values(x, y) {
        const __e = new LogicalTestFrameEvent("set_values", {"x": x, "y": y});
        const __ctx = new LogicalTestFrameContext(__e, null);
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
        } else if (__e._message === "test_and") {
            if (this.a && this.b) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        } else if (__e._message === "test_not") {
            if (!this.a) {
                this._context_stack[this._context_stack.length - 1]._return = true;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = false;
            }
        } else if (__e._message === "test_or") {
            if (this.a || this.b) {
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

    const s = new LogicalTest();

    // a=true, b=false: true && false = false
    if (!s.test_and()) {
        console.log("ok 1 - true && false is false");
    } else {
        console.log("not ok 1 - true && false is false");
    }

    // a=true, b=false: true || false = true
    if (s.test_or()) {
        console.log("ok 2 - true || false is true");
    } else {
        console.log("not ok 2 - true || false is true");
    }

    // a=true: !true = false
    if (!s.test_not()) {
        console.log("ok 3 - !true is false");
    } else {
        console.log("not ok 3 - !true is false");
    }

    // Change values: a=true, b=true
    s.set_values(true, true);

    // true && true = true
    if (s.test_and()) {
        console.log("ok 4 - true && true is true");
    } else {
        console.log("not ok 4 - true && true is true");
    }

    // Change values: a=false, b=false
    s.set_values(false, false);

    // false || false = false
    if (!s.test_or()) {
        console.log("ok 5 - false || false is false");
    } else {
        console.log("not ok 5 - false || false is false");
    }

    // !false = true
    if (s.test_not()) {
        console.log("ok 6 - !false is true");
    } else {
        console.log("not ok 6 - !false is true");
    }
}

main();
