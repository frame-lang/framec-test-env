
// Test 6: Return values through async chain
// Validates: return sugar, @@:return, default return all work async

async function mockMultiply(x, y) {
    await Promise.resolve();
    return x * y;
}

async function mockFetch() {
    await Promise.resolve();
    return "fetched_data";
}

export class AsyncReturnFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncReturnFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncReturnCompartment {
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
        const c = new AsyncReturnCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncReturn {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncReturnCompartment("Ready");
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
            const exit_event = new AsyncReturnFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncReturnFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new AsyncReturnFrameEvent("$>", this.__compartment.enter_args);
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

    async compute(x) {
        const __e = new AsyncReturnFrameEvent("compute", {"x": x});
        const __ctx = new AsyncReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async with_default() {
        const __e = new AsyncReturnFrameEvent("with_default", null);
        const __ctx = new AsyncReturnFrameContext(__e, null);
        __ctx._return = "default_value";
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async get_data() {
        const __e = new AsyncReturnFrameEvent("get_data", null);
        const __ctx = new AsyncReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Ready(__e) {
        if (__e._message === "compute") {
            const x = __e._parameters?.["x"];
            const result = await mockMultiply(x, 2)
            this._context_stack[this._context_stack.length - 1]._return = result;
            return;
        } else if (__e._message === "get_data") {
            const data = await mockFetch()
            this._context_stack[this._context_stack.length - 1]._return = data;
        } else if (__e._message === "with_default") {
            // Do not set @@:return — default should be used
            // no-op
        }
    }

    async init() {
        const __e = new AsyncReturnFrameEvent("$>", null);
        const __ctx = new AsyncReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let s = new AsyncReturn();
    await s.init();

    // Test return sugar
    let result = await s.compute(5);
    if (result !== 10) {
        throw new Error(`compute: expected 10, got ${result}`);
    }

    // Test default return value
    let strResult = await s.with_default();
    if (strResult !== "default_value") {
        throw new Error(`default: expected 'default_value', got ${strResult}`);
    }

    // Test @@:return assignment
    strResult = await s.get_data();
    if (strResult !== "fetched_data") {
        throw new Error(`get_data: expected 'fetched_data', got ${strResult}`);
    }

    console.log("PASS: async return values â sugar, default, and @@:return all work");
}

main();
