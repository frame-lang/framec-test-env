
// Test: Interface method return_init
// Validates that interface methods can have default return values
// Syntax: method(): type = "default_value"

export class ReturnInitTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class ReturnInitTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class ReturnInitTestCompartment {
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
        const c = new ReturnInitTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class ReturnInitTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new ReturnInitTestCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new ReturnInitTestFrameEvent("$>", null);
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
            const exit_event = new ReturnInitTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ReturnInitTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new ReturnInitTestFrameEvent("$>", this.__compartment.enter_args);
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

    get_status() {
        const __e = new ReturnInitTestFrameEvent("get_status", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        __ctx._return = "unknown";
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_count() {
        const __e = new ReturnInitTestFrameEvent("get_count", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        __ctx._return = 0;
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_flag() {
        const __e = new ReturnInitTestFrameEvent("get_flag", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        __ctx._return = false;
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    trigger() {
        const __e = new ReturnInitTestFrameEvent("trigger", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Start(__e) {
        if (__e._message === "$>") {
            // Start state enter (no-op)
        } else if (__e._message === "get_count") {
            // Do not set return - should use default 0
        } else if (__e._message === "get_flag") {
            // Do not set return - should use default false
        } else if (__e._message === "get_status") {
            // Do not set return - should use default "unknown"
        } else if (__e._message === "trigger") {
            const __compartment = new ReturnInitTestCompartment("Active", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Active(__e) {
        if (__e._message === "$>") {
            // Active state enter (no-op)
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = 42;
        } else if (__e._message === "get_flag") {
            this._context_stack[this._context_stack.length - 1]._return = true;
        } else if (__e._message === "get_status") {
            this._context_stack[this._context_stack.length - 1]._return = "active";
        } else if (__e._message === "trigger") {
            const __compartment = new ReturnInitTestCompartment("Start", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("TAP version 14");
    console.log("1..6");

    const s = new ReturnInitTest();

    // Test 1: Default string return
    if (s.get_status() === "unknown") {
        console.log("ok 1 - default string return is 'unknown'");
    } else {
        console.log(`not ok 1 - default string return is 'unknown' # got ${s.get_status()}`);
    }

    // Test 2: Default int return
    if (s.get_count() === 0) {
        console.log("ok 2 - default int return is 0");
    } else {
        console.log(`not ok 2 - default int return is 0 # got ${s.get_count()}`);
    }

    // Test 3: Default bool return
    if (s.get_flag() === false) {
        console.log("ok 3 - default bool return is false");
    } else {
        console.log(`not ok 3 - default bool return is false # got ${s.get_flag()}`);
    }

    // Transition to Active state
    s.trigger();

    // Test 4: Explicit string return overrides default
    if (s.get_status() === "active") {
        console.log("ok 4 - explicit return overrides default string");
    } else {
        console.log(`not ok 4 - explicit return overrides default string # got ${s.get_status()}`);
    }

    // Test 5: Explicit int return overrides default
    if (s.get_count() === 42) {
        console.log("ok 5 - explicit return overrides default int");
    } else {
        console.log(`not ok 5 - explicit return overrides default int # got ${s.get_count()}`);
    }

    // Test 6: Explicit bool return overrides default
    if (s.get_flag() === true) {
        console.log("ok 6 - explicit return overrides default bool");
    } else {
        console.log(`not ok 6 - explicit return overrides default bool # got ${s.get_flag()}`);
    }

    console.log("# PASS - return_init provides default return values");
}

main();
