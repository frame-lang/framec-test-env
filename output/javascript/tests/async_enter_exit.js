
// Test 3: Async enter/exit lifecycle handlers
// Validates: await works in $>() and <$() handlers

async function mockSetup() {
    await Promise.resolve();
    return "setup_done";
}

async function mockTeardown() {
    await Promise.resolve();
    return "teardown_done";
}

export class AsyncEnterExitFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncEnterExitFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncEnterExitCompartment {
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
        const c = new AsyncEnterExitCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncEnterExit {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = "";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncEnterExitCompartment("Idle");
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
            const exit_event = new AsyncEnterExitFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncEnterExitFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new AsyncEnterExitFrameEvent("$>", this.__compartment.enter_args);
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

    async start() {
        const __e = new AsyncEnterExitFrameEvent("start", null);
        const __ctx = new AsyncEnterExitFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }

    async stop() {
        const __e = new AsyncEnterExitFrameEvent("stop", null);
        const __ctx = new AsyncEnterExitFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }

    async get_log() {
        const __e = new AsyncEnterExitFrameEvent("get_log", null);
        const __ctx = new AsyncEnterExitFrameContext(__e, null);
        __ctx._return = "";
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Idle(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "start") {
            const __compartment = new AsyncEnterExitCompartment("Active", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    async _state_Active(__e) {
        if (__e._message === "<$") {
            const result = await mockTeardown()
            this.log = this.log + "exit:" + result + ","
        } else if (__e._message === "$>") {
            const result = await mockSetup()
            this.log = this.log + "enter:" + result + ","
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "stop") {
            const __compartment = new AsyncEnterExitCompartment("Idle", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    async init() {
        const __e = new AsyncEnterExitFrameEvent("$>", null);
        const __ctx = new AsyncEnterExitFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let s = new AsyncEnterExit();
    await s.init();

    // Start â triggers $Active.$>()
    await s.start();
    let log = await s.get_log();
    if (!log.includes("enter:setup_done")) {
        throw new Error(`Expected enter in log, got '${log}'`);
    }

    // Stop â triggers $Active.<$() then transition
    await s.stop();
    log = await s.get_log();
    if (!log.includes("exit:teardown_done")) {
        throw new Error(`Expected exit in log, got '${log}'`);
    }

    console.log("PASS: async enter/exit â lifecycle handlers with await work");
}

main();
