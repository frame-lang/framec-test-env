
export class OperationsTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class OperationsTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class OperationsTestCompartment {
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
        const c = new OperationsTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class OperationsTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    last_result = 0;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new OperationsTestCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new OperationsTestFrameEvent("$>", null);
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
            const exit_event = new OperationsTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new OperationsTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new OperationsTestFrameEvent("$>", this.__compartment.enter_args);
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

    compute(a, b) {
        const __e = new OperationsTestFrameEvent("compute", {"a": a, "b": b});
        const __ctx = new OperationsTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_last_result() {
        const __e = new OperationsTestFrameEvent("get_last_result", null);
        const __ctx = new OperationsTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Ready(__e) {
        if (__e._message === "compute") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            // Use instance operations
            const sum_val = this.add(a, b);
            const prod_val = this.multiply(a, b);
            const last_result = sum_val + prod_val;
            this._context_stack[this._context_stack.length - 1]._return = last_result;
            return;;
        } else if (__e._message === "get_last_result") {
            this._context_stack[this._context_stack.length - 1]._return = this.last_result;
            return;;
        }
    }

    add(x, y) {
                    return x + y;
    }

    multiply(x, y) {
                    return x * y;
    }

    static factorial(n) {
                    if (n <= 1) {
                        return 1;
                    }
                    return n * OperationsTest.factorial(n - 1);
    }

    static is_even(n) {
                    return n % 2 === 0;
    }
}

function main() {
    console.log("=== Test 22: Operations Basic (JavaScript) ===");
    const s = new OperationsTest();

    // Test 1: Instance operations
    let result = s.add(3, 4);
    if (result !== 7) {
        throw new Error(`Expected 7, got ${result}`);
    }
    console.log(`1. add(3, 4) = ${result}`);

    result = s.multiply(3, 4);
    if (result !== 12) {
        throw new Error(`Expected 12, got ${result}`);
    }
    console.log(`2. multiply(3, 4) = ${result}`);

    // Test 2: Operations used in handler
    result = s.compute(3, 4);
    // compute returns add(3,4) + multiply(3,4) = 7 + 12 = 19
    if (result !== 19) {
        throw new Error(`Expected 19, got ${result}`);
    }
    console.log(`3. compute(3, 4) = ${result}`);

    // Test 3: Static operations
    result = OperationsTest.factorial(5);
    if (result !== 120) {
        throw new Error(`Expected 120, got ${result}`);
    }
    console.log(`4. factorial(5) = ${result}`);

    let is_even = OperationsTest.is_even(4);
    if (is_even !== true) {
        throw new Error(`Expected true, got ${is_even}`);
    }
    console.log(`5. is_even(4) = ${is_even}`);

    is_even = OperationsTest.is_even(7);
    if (is_even !== false) {
        throw new Error(`Expected false, got ${is_even}`);
    }
    console.log(`6. is_even(7) = ${is_even}`);

    // Test 4: Static via class
    result = OperationsTest.factorial(4);
    if (result !== 24) {
        throw new Error(`Expected 24, got ${result}`);
    }
    console.log(`7. OperationsTest.factorial(4) = ${result}`);

    console.log("PASS: Operations basic works correctly");
}

main();
