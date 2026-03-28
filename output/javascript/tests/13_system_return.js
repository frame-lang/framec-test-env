
export class SystemReturnTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class SystemReturnTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class SystemReturnTestCompartment {
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
        const c = new SystemReturnTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class SystemReturnTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new SystemReturnTestCompartment("Calculator");
        this.__next_compartment = null;
        const __frame_event = new SystemReturnTestFrameEvent("$>", null);
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
            const exit_event = new SystemReturnTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new SystemReturnTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new SystemReturnTestFrameEvent("$>", this.__compartment.enter_args);
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
        const __e = new SystemReturnTestFrameEvent("add", {"a": a, "b": b});
        const __ctx = new SystemReturnTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    multiply(a, b) {
        const __e = new SystemReturnTestFrameEvent("multiply", {"a": a, "b": b});
        const __ctx = new SystemReturnTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    greet(name) {
        const __e = new SystemReturnTestFrameEvent("greet", {"name": name});
        const __ctx = new SystemReturnTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_value() {
        const __e = new SystemReturnTestFrameEvent("get_value", null);
        const __ctx = new SystemReturnTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Calculator(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Calculator") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("value" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["value"] = 0;
            }
        } else if (__e._message === "add") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            this._context_stack[this._context_stack.length - 1]._return = a + b;
            return;;
        } else if (__e._message === "get_value") {
            __sv_comp.state_vars["value"] = 42;
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["value"];
            return;;
        } else if (__e._message === "greet") {
            const name = __e._parameters?.["name"];
            this._context_stack[this._context_stack.length - 1]._return = "Hello, " + name + "!";
            return;;
        } else if (__e._message === "multiply") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            this._context_stack[this._context_stack.length - 1]._return = a * b;
        }
    }
}

function main() {
    console.log("=== Test 13: System Return ===");
    const calc = new SystemReturnTest();

    // Test return sugar
    let result = calc.add(3, 5);
    if (result !== 8) {
        throw new Error(`Expected 8, got ${result}`);
    }
    console.log(`add(3, 5) = ${result}`);

    // Test @@:return = expr
    result = calc.multiply(4, 7);
    if (result !== 28) {
        throw new Error(`Expected 28, got ${result}`);
    }
    console.log(`multiply(4, 7) = ${result}`);

    // Test string return
    const greeting = calc.greet("World");
    if (greeting !== "Hello, World!") {
        throw new Error(`Expected 'Hello, World!', got '${greeting}'`);
    }
    console.log(`greet('World') = ${greeting}`);

    // Test return with state variable
    const value = calc.get_value();
    if (value !== 42) {
        throw new Error(`Expected 42, got ${value}`);
    }
    console.log(`get_value() = ${value}`);

    console.log("PASS: System return works correctly");
}

main();
