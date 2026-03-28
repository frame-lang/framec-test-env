
// Test 7: Nested async interface calls (reentrancy)
// Validates: context stack handles nested async calls correctly

async function mockFetch() {
    await Promise.resolve();
    return "fetched";
}

export class AsyncReentrantFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncReentrantFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncReentrantCompartment {
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
        const c = new AsyncReentrantCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncReentrant {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncReentrantCompartment("Ready");
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
            const exit_event = new AsyncReentrantFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncReentrantFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new AsyncReentrantFrameEvent("$>", this.__compartment.enter_args);
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

    async outer() {
        const __e = new AsyncReentrantFrameEvent("outer", null);
        const __ctx = new AsyncReentrantFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async inner() {
        const __e = new AsyncReentrantFrameEvent("inner", null);
        const __ctx = new AsyncReentrantFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Ready(__e) {
        if (__e._message === "inner") {
            const data = await mockFetch()
            this._context_stack[this._context_stack.length - 1]._return = "inner:" + data;
            return;
        } else if (__e._message === "outer") {
            const inner_result = await this.inner()
            this._context_stack[this._context_stack.length - 1]._return = "outer:" + inner_result;
            return;
        }
    }

    async init() {
        const __e = new AsyncReentrantFrameEvent("$>", null);
        const __ctx = new AsyncReentrantFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let s = new AsyncReentrant();
    await s.init();

    // Direct inner call
    let result = await s.inner();
    if (result !== "inner:fetched") {
        throw new Error(`inner: expected 'inner:fetched', got '${result}'`);
    }

    // Outer calls inner â nested async dispatch
    result = await s.outer();
    if (result !== "outer:inner:fetched") {
        throw new Error(`outer: expected 'outer:inner:fetched', got '${result}'`);
    }

    console.log("PASS: async reentrant â nested calls work, context stack isolates returns");
}

main();
