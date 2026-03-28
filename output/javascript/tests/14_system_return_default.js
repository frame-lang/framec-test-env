
// NOTE: Default return value syntax (method(): type = default) not yet implemented.
// This test validates behavior when handler does not set @@:return.

export class SystemReturnDefaultTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class SystemReturnDefaultTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class SystemReturnDefaultTestCompartment {
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
        const c = new SystemReturnDefaultTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class SystemReturnDefaultTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new SystemReturnDefaultTestCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new SystemReturnDefaultTestFrameEvent("$>", null);
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
            const exit_event = new SystemReturnDefaultTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new SystemReturnDefaultTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new SystemReturnDefaultTestFrameEvent("$>", this.__compartment.enter_args);
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

    handler_sets_value() {
        const __e = new SystemReturnDefaultTestFrameEvent("handler_sets_value", null);
        const __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    handler_no_return() {
        const __e = new SystemReturnDefaultTestFrameEvent("handler_no_return", null);
        const __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_count() {
        const __e = new SystemReturnDefaultTestFrameEvent("get_count", null);
        const __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Start(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Start") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("count" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["count"] = 0;
            }
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["count"];
            return;;
        } else if (__e._message === "handler_no_return") {
            // Does not set return - should return null/undefined
            __sv_comp.state_vars["count"] = __sv_comp.state_vars["count"] + 1;
        } else if (__e._message === "handler_sets_value") {
            this._context_stack[this._context_stack.length - 1]._return = "set_by_handler";
            return;;
        }
    }
}

function main() {
    console.log("=== Test 14: System Return Default Behavior ===");
    const s = new SystemReturnDefaultTest();

    // Test 1: Handler explicitly sets return value
    const result1 = s.handler_sets_value();
    if (result1 !== "set_by_handler") {
        throw new Error(`Expected 'set_by_handler', got '${result1}'`);
    }
    console.log(`1. handler_sets_value() = '${result1}'`);

    // Test 2: Handler does NOT set return - should return null/undefined
    const result2 = s.handler_no_return();
    if (result2 !== null && result2 !== undefined) {
        throw new Error(`Expected null/undefined, got '${result2}'`);
    }
    console.log(`2. handler_no_return() = ${result2}`);

    // Test 3: Verify handler was called (side effect check)
    let count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }
    console.log(`3. Handler was called, count = ${count}`);

    // Test 4: Call again to verify idempotence
    const result4 = s.handler_no_return();
    if (result4 !== null && result4 !== undefined) {
        throw new Error(`Expected null/undefined again, got '${result4}'`);
    }
    count = s.get_count();
    if (count !== 2) {
        throw new Error(`Expected count=2, got ${count}`);
    }
    console.log(`4. Second call: result=${result4}, count=${count}`);

    console.log("PASS: System return default behavior works correctly");
}

main();
