
// Test 2: Transition after await
// Validates: -> $State works correctly after async handler body

async function mockConnect(url) {
    await Promise.resolve();
    return {url: url, status: "connected"};
}

export class AsyncTransitionFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncTransitionFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncTransitionCompartment {
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
        const c = new AsyncTransitionCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncTransition {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    connection = null;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncTransitionCompartment("Disconnected");
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
            const exit_event = new AsyncTransitionFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncTransitionFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new AsyncTransitionFrameEvent("$>", this.__compartment.enter_args);
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

    async connect(url) {
        const __e = new AsyncTransitionFrameEvent("connect", {"url": url});
        const __ctx = new AsyncTransitionFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }

    async disconnect() {
        const __e = new AsyncTransitionFrameEvent("disconnect", null);
        const __ctx = new AsyncTransitionFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }

    async get_state() {
        const __e = new AsyncTransitionFrameEvent("get_state", null);
        const __ctx = new AsyncTransitionFrameContext(__e, null);
        __ctx._return = "Unknown";
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Disconnected(__e) {
        if (__e._message === "connect") {
            const url = __e._parameters?.["url"];
            const result = await mockConnect(url)
            this.connection = result
            const __compartment = new AsyncTransitionCompartment("Connected", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Disconnected";
            return;
        }
    }

    async _state_Connected(__e) {
        if (__e._message === "disconnect") {
            this.connection = null
            const __compartment = new AsyncTransitionCompartment("Disconnected", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Connected";
            return;
        }
    }

    async init() {
        const __e = new AsyncTransitionFrameEvent("$>", null);
        const __ctx = new AsyncTransitionFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let s = new AsyncTransition();
    await s.init();

    // Initial state
    let state = await s.get_state();
    if (state !== "Disconnected") {
        throw new Error(`Expected 'Disconnected', got '${state}'`);
    }

    // Connect â await then transition
    await s.connect("ws://example.com");
    state = await s.get_state();
    if (state !== "Connected") {
        throw new Error(`Expected 'Connected', got '${state}'`);
    }

    // Disconnect â transition back
    await s.disconnect();
    state = await s.get_state();
    if (state !== "Disconnected") {
        throw new Error(`Expected 'Disconnected', got '${state}'`);
    }

    console.log("PASS: async transition â state changes work after await");
}

main();
