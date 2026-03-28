
// Test: Basic System Context Access
// Validates @@.param, @@:return, @@:event syntax

export class ContextBasicTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class ContextBasicTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class ContextBasicTestCompartment {
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
        const c = new ContextBasicTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class ContextBasicTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new ContextBasicTestCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new ContextBasicTestFrameEvent("$>", null);
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
            const exit_event = new ContextBasicTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ContextBasicTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new ContextBasicTestFrameEvent("$>", this.__compartment.enter_args);
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
        const __e = new ContextBasicTestFrameEvent("add", {"a": a, "b": b});
        const __ctx = new ContextBasicTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_event_name() {
        const __e = new ContextBasicTestFrameEvent("get_event_name", null);
        const __ctx = new ContextBasicTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    greet(name) {
        const __e = new ContextBasicTestFrameEvent("greet", {"name": name});
        const __ctx = new ContextBasicTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Ready(__e) {
        if (__e._message === "add") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            // Access params via @@ shorthand
            this._context_stack[this._context_stack.length - 1]._return = this._context_stack[this._context_stack.length - 1].event._parameters["a"] + this._context_stack[this._context_stack.length - 1].event._parameters["b"];
        } else if (__e._message === "get_event_name") {
            // Access event name
            this._context_stack[this._context_stack.length - 1]._return = this._context_stack[this._context_stack.length - 1].event._message;
        } else if (__e._message === "greet") {
            const name = __e._parameters?.["name"];
            // Mix param access and return
            const result = "Hello, " + this._context_stack[this._context_stack.length - 1].event._parameters["name"] + "!";
            this._context_stack[this._context_stack.length - 1]._return = result;
        }
    }
}

function main() {
    console.log("=== Test 36: Context Basic ===");
    const s = new ContextBasicTest();

    // Test 1: @@.a and @@.b param access, @@:return
    const result1 = s.add(3, 5);
    if (result1 !== 8) throw new Error(`Expected 8, got ${result1}`);
    console.log(`1. add(3, 5) = ${result1}`);

    // Test 2: @@:event access
    const eventName = s.get_event_name();
    if (eventName !== "get_event_name") throw new Error(`Expected 'get_event_name', got '${eventName}'`);
    console.log(`2. @@:event = '${eventName}'`);

    // Test 3: @@.name param access with string
    const greeting = s.greet("World");
    if (greeting !== "Hello, World!") throw new Error(`Expected 'Hello, World!', got '${greeting}'`);
    console.log(`3. greet('World') = '${greeting}'`);

    console.log("PASS: Context basic access works correctly");
}

main();
