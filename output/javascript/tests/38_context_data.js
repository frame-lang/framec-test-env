
// Test: Context Data (@@:data)
// Validates call-scoped data that persists across handler -> <$ -> $> chain

export class ContextDataTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class ContextDataTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class ContextDataTestCompartment {
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
        const c = new ContextDataTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class ContextDataTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new ContextDataTestCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new ContextDataTestFrameEvent("$>", null);
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
            const exit_event = new ContextDataTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ContextDataTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new ContextDataTestFrameEvent("$>", this.__compartment.enter_args);
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

    process_with_data(value) {
        const __e = new ContextDataTestFrameEvent("process_with_data", {"value": value});
        const __ctx = new ContextDataTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    check_data_isolation() {
        const __e = new ContextDataTestFrameEvent("check_data_isolation", null);
        const __ctx = new ContextDataTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    transition_preserves_data(x) {
        const __e = new ContextDataTestFrameEvent("transition_preserves_data", {"x": x});
        const __ctx = new ContextDataTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Start(__e) {
        if (__e._message === "<$") {
            // Exit handler can access data set by event handler
            this._context_stack[this._context_stack.length - 1]._data["trace"].push("exit");
        } else if (__e._message === "check_data_isolation") {
            // Set data, call another method, verify our data preserved
            this._context_stack[this._context_stack.length - 1]._data["outer"] = "outer_value";

            // This creates its own context with its own data
            const inner_result = this.process_with_data(99);

            // Our data should still be here
            this._context_stack[this._context_stack.length - 1]._return = "outer_data=" + this._context_stack[this._context_stack.length - 1]._data["outer"] + ",inner=" + inner_result;
        } else if (__e._message === "process_with_data") {
            const value = __e._parameters?.["value"];
            // Set data in handler
            this._context_stack[this._context_stack.length - 1]._data["input"] = this._context_stack[this._context_stack.length - 1].event._parameters["value"];
            this._context_stack[this._context_stack.length - 1]._data["trace"] = ["handler"];

            this._context_stack[this._context_stack.length - 1]._return = "processed:" + this._context_stack[this._context_stack.length - 1]._data["input"];
        } else if (__e._message === "transition_preserves_data") {
            const x = __e._parameters?.["x"];
            // Set data, transition, verify data available in lifecycle handlers
            this._context_stack[this._context_stack.length - 1]._data["started_in"] = "Start";
            this._context_stack[this._context_stack.length - 1]._data["value"] = this._context_stack[this._context_stack.length - 1].event._parameters["x"];
            this._context_stack[this._context_stack.length - 1]._data["trace"] = ["handler"];
            const __compartment = new ContextDataTestCompartment("End", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_End(__e) {
        if (__e._message === "$>") {
            // Enter handler can access data set by previous handlers
            this._context_stack[this._context_stack.length - 1]._data["trace"].push("enter");
            this._context_stack[this._context_stack.length - 1]._data["ended_in"] = "End";

            // Build final result from accumulated data
            const trace = this._context_stack[this._context_stack.length - 1]._data["trace"];
            const trace_str = trace ? trace.join(",") : "no_trace";
            this._context_stack[this._context_stack.length - 1]._return = `from=${this._context_stack[this._context_stack.length - 1]._data["started_in"]},to=${this._context_stack[this._context_stack.length - 1]._data["ended_in"]},value=${this._context_stack[this._context_stack.length - 1]._data["value"]},trace=${trace_str}`;
        }
    }
}

function main() {
    console.log("=== Test 38: Context Data ===");

    // Test 1: Basic data set/get
    const s1 = new ContextDataTest();
    let result = s1.process_with_data(42);
    if (result !== "processed:42") throw new Error(`Expected 'processed:42', got '${result}'`);
    console.log(`1. process_with_data(42) = '${result}'`);

    // Test 2: Data isolation between nested calls
    const s2 = new ContextDataTest();
    result = s2.check_data_isolation();
    const expected = "outer_data=outer_value,inner=processed:99";
    if (result !== expected) throw new Error(`Expected '${expected}', got '${result}'`);
    console.log(`2. check_data_isolation() = '${result}'`);

    // Test 3: Data preserved across transition (handler -> <$ -> $>)
    const s3 = new ContextDataTest();
    result = s3.transition_preserves_data(100);
    // Data should flow: handler sets -> exit accesses -> enter accesses and returns
    if (!result.includes("from=Start")) throw new Error(`Expected 'from=Start' in '${result}'`);
    if (!result.includes("to=End")) throw new Error(`Expected 'to=End' in '${result}'`);
    if (!result.includes("value=100")) throw new Error(`Expected 'value=100' in '${result}'`);
    console.log(`3. transition_preserves_data(100) = '${result}'`);

    console.log("PASS: Context data works correctly");
}

main();
