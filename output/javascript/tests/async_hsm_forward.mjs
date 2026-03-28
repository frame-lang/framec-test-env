
// Test 4: Async HSM parent forward
// Validates: => $^ dispatch is awaited in async mode

async function mockTransform(data) {
    await Promise.resolve();
    return data.toUpperCase();
}

export class AsyncHsmFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncHsmFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncHsmCompartment {
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
        const c = new AsyncHsmCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncHsm {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new AsyncHsmCompartment("Parent", null);
        this.__compartment = new AsyncHsmCompartment("Child", __parent_comp_0);
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
            const exit_event = new AsyncHsmFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncHsmFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new AsyncHsmFrameEvent("$>", this.__compartment.enter_args);
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

    async process(data) {
        const __e = new AsyncHsmFrameEvent("process", {"data": data});
        const __ctx = new AsyncHsmFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async other(data) {
        const __e = new AsyncHsmFrameEvent("other", {"data": data});
        const __ctx = new AsyncHsmFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Child(__e) {
        if (__e._message === "process") {
            const data = __e._parameters?.["data"];
            const result = await mockTransform(data)
            this._context_stack[this._context_stack.length - 1]._return = "child:" + result;
            return;
        } else {
            await this._state_Parent(__e);
        }
    }

    async _state_Parent(__e) {
        if (__e._message === "other") {
            const data = __e._parameters?.["data"];
            const result = await mockTransform(data)
            this._context_stack[this._context_stack.length - 1]._return = "parent_other:" + result;
            return;
        } else if (__e._message === "process") {
            const data = __e._parameters?.["data"];
            const result = await mockTransform(data)
            this._context_stack[this._context_stack.length - 1]._return = "parent:" + result;
            return;
        }
    }

    async init() {
        const __e = new AsyncHsmFrameEvent("$>", null);
        const __ctx = new AsyncHsmFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let s = new AsyncHsm();
    await s.init();

    // Child handles process directly
    let result = await s.process("hello");
    if (result !== "child:HELLO") {
        throw new Error(`Expected 'child:HELLO', got '${result}'`);
    }

    // Child does not handle 'other' â default forward to parent
    result = await s.other("test");
    if (result !== "parent_other:TEST") {
        throw new Error(`Expected 'parent_other:TEST', got '${result}'`);
    }

    console.log("PASS: async HSM forward â default forward dispatches to parent");
}

main();
