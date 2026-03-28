
// Test 1: Basic async dispatch chain
// Validates: async interface method, await in handler, return value propagation

async function mockLookup(key) {
    await Promise.resolve();
    return `value_for_${key}`;
}

export class AsyncBasicFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncBasicFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncBasicCompartment {
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
        const c = new AsyncBasicCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncBasic {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncBasicCompartment("Ready");
        this.__next_compartment = null;
    }

    async __kernel(__e) {
        // Route event to current state
        await this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new AsyncBasicFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncBasicFrameEvent("$>", this.__compartment.enter_args);
                await this.__router(enter_event);
            } else {
                // Forward event to new state
                const forward_event = next_compartment.forward_event;
                next_compartment.forward_event = null;
                if (forward_event._message === "$>") {
                    // Forwarding enter event - just send it
                    await this.__router(forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    const enter_event = new AsyncBasicFrameEvent("$>", this.__compartment.enter_args);
                    await this.__router(enter_event);
                    await this.__router(forward_event);
                }
            }
        }
    }

    async __router(__e) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = this[handler_name];
        if (handler) {
            await handler.call(this, __e);
        }
    }

    __transition(next_compartment) {
        this.__next_compartment = next_compartment;
    }

    async fetch(key) {
        const __e = new AsyncBasicFrameEvent("fetch", {"key": key});
        const __ctx = new AsyncBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async get_state() {
        const __e = new AsyncBasicFrameEvent("get_state", null);
        const __ctx = new AsyncBasicFrameContext(__e, null);
        __ctx._return = "Unknown";
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Ready(__e) {
        if (__e._message === "fetch") {
            const key = __e._parameters?.["key"];
            const result = await mockLookup(key)
            this._context_stack[this._context_stack.length - 1]._return = result;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Ready";
            return;
        }
    }

    async init() {
        const __e = new AsyncBasicFrameEvent("$>", null);
        const __ctx = new AsyncBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let s = new AsyncBasic();
    await s.init();

    // Test async fetch
    let result = await s.fetch("test_key");
    if (result !== "value_for_test_key") {
        throw new Error(`Expected 'value_for_test_key', got '${result}'`);
    }

    // Test sync method works through async kernel
    let state = await s.get_state();
    if (state !== "Ready") {
        throw new Error(`Expected 'Ready', got '${state}'`);
    }

    console.log("PASS: async basic â dispatch chain and return values work");
}

main();
