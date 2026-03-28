
// Test 39: Tagged System Instantiation
// Validates the @@System() syntax for tracked instantiation

export class CalculatorFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class CalculatorFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class CalculatorCompartment {
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
        const c = new CalculatorCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class Calculator {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    result = 0;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new CalculatorCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new CalculatorFrameEvent("$>", null);
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
            const exit_event = new CalculatorFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new CalculatorFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new CalculatorFrameEvent("$>", this.__compartment.enter_args);
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

    add(a, b) {
        const __e = new CalculatorFrameEvent("add", {"a": a, "b": b});
        const __ctx = new CalculatorFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_result() {
        const __e = new CalculatorFrameEvent("get_result", null);
        const __ctx = new CalculatorFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Ready(__e) {
        if (__e._message === "add") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            this.result = a + b;
            this._context_stack[this._context_stack.length - 1]._return = this.result;
            return;
        } else if (__e._message === "get_result") {
            this._context_stack[this._context_stack.length - 1]._return = this.result;
            return;
        }
    }
}

export class CounterFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class CounterFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class CounterCompartment {
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
        const c = new CounterCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class Counter {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    count = 0;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new CounterCompartment("Active");
        this.__next_compartment = null;
        const __frame_event = new CounterFrameEvent("$>", null);
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
            const exit_event = new CounterFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new CounterFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new CounterFrameEvent("$>", this.__compartment.enter_args);
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
        const __e = new CounterFrameEvent("increment", null);
        const __ctx = new CounterFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_count() {
        const __e = new CounterFrameEvent("get_count", null);
        const __ctx = new CounterFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Active(__e) {
        if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = this.count;
            return;
        } else if (__e._message === "increment") {
            this.count = this.count + 1;
        }
    }
}

function main() {
    console.log("=== Test 39: Tagged System Instantiation ===");

    // Tagged instantiation - validated at transpile time
    const calc = new Calculator();
    const counter = new Counter();

    // Test Calculator
    let result = calc.add(3, 4);
    if (result !== 7) {
        console.log(`FAIL: Expected 7, got ${result}`);
        process.exit(1);
    }
    console.log(`Calculator.add(3, 4) = ${result}`);

    result = calc.get_result();
    if (result !== 7) {
        console.log(`FAIL: Expected 7, got ${result}`);
        process.exit(1);
    }
    console.log(`Calculator.get_result() = ${result}`);

    // Test Counter
    counter.increment();
    counter.increment();
    counter.increment();
    const count = counter.get_count();
    if (count !== 3) {
        console.log(`FAIL: Expected 3, got ${count}`);
        process.exit(1);
    }
    console.log(`Counter after 3 increments: ${count}`);

    console.log("PASS: Tagged instantiation works correctly");
}

main();
