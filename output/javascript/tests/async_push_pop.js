
// Test 5: Stack operations across async boundaries
// Validates: push$/pop$ preserve compartment across async handlers

async function mockCompute() {
    await Promise.resolve();
    return 42;
}

async function mockCleanup() {
    await Promise.resolve();
}

export class AsyncPushPopFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncPushPopFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncPushPopCompartment {
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
        const c = new AsyncPushPopCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncPushPop {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncPushPopCompartment("Main");
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
            const exit_event = new AsyncPushPopFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncPushPopFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new AsyncPushPopFrameEvent("$>", this.__compartment.enter_args);
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

    async save_and_go() {
        const __e = new AsyncPushPopFrameEvent("save_and_go", null);
        const __ctx = new AsyncPushPopFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }

    async restore() {
        const __e = new AsyncPushPopFrameEvent("restore", null);
        const __ctx = new AsyncPushPopFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }

    async get_state() {
        const __e = new AsyncPushPopFrameEvent("get_state", null);
        const __ctx = new AsyncPushPopFrameContext(__e, null);
        __ctx._return = "Unknown";
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async get_counter() {
        const __e = new AsyncPushPopFrameEvent("get_counter", null);
        const __ctx = new AsyncPushPopFrameContext(__e, null);
        __ctx._return = 0;
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Temp(__e) {
        if (__e._message === "get_counter") {
            this._context_stack[this._context_stack.length - 1]._return = 0;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Temp";
            return;
        } else if (__e._message === "restore") {
            await mockCleanup()
            this.__transition(this._state_stack.pop());
            return;
        }
    }

    async _state_Main(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Main") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("counter" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["counter"] = 0;
            }
        } else if (__e._message === "get_counter") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["counter"];
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Main";
            return;
        } else if (__e._message === "save_and_go") {
            __sv_comp.state_vars["counter"] = await mockCompute();
            await this._state_stack.push(this.__compartment.copy());
            const __compartment = new AsyncPushPopCompartment("Temp", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    async init() {
        const __e = new AsyncPushPopFrameEvent("$>", null);
        const __ctx = new AsyncPushPopFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let s = new AsyncPushPop();
    await s.init();

    let state = await s.get_state();
    if (state !== "Main") {
        throw new Error(`Expected 'Main', got '${state}'`);
    }
    let counter = await s.get_counter();
    if (counter !== 0) {
        throw new Error(`Expected 0, got ${counter}`);
    }

    // Save state and go to Temp
    await s.save_and_go();
    state = await s.get_state();
    if (state !== "Temp") {
        throw new Error(`Expected 'Temp', got '${state}'`);
    }

    // Restore â pop back to Main with preserved counter
    await s.restore();
    state = await s.get_state();
    if (state !== "Main") {
        throw new Error(`Expected 'Main', got '${state}'`);
    }
    counter = await s.get_counter();
    if (counter !== 42) {
        throw new Error(`Expected 42, got ${counter}`);
    }

    console.log("PASS: async push/pop â state vars preserved across async boundaries");
}

main();
