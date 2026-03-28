
export class TransitionEnterArgsFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class TransitionEnterArgsFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class TransitionEnterArgsCompartment {
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
        const c = new TransitionEnterArgsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class TransitionEnterArgs {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new TransitionEnterArgsCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new TransitionEnterArgsFrameEvent("$>", null);
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
            const exit_event = new TransitionEnterArgsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new TransitionEnterArgsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new TransitionEnterArgsFrameEvent("$>", this.__compartment.enter_args);
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

    start() {
        const __e = new TransitionEnterArgsFrameEvent("start", null);
        const __ctx = new TransitionEnterArgsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new TransitionEnterArgsFrameEvent("get_log", null);
        const __ctx = new TransitionEnterArgsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Idle(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "start") {
            this.log.push("idle:start");
            const __compartment = new TransitionEnterArgsCompartment("Active", this.__compartment.copy());
            __compartment.enter_args = Object.fromEntries(["from_idle", 42].map((v, i) => [String(i), v]));
            this.__transition(__compartment);
            return;
        }
    }

    _state_Active(__e) {
        if (__e._message === "$>") {
            const source = __e._parameters?.["0"];
            const value = __e._parameters?.["1"];
            this.log.push(`active:enter:${source}:${value}`);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "start") {
            this.log.push("active:start");
        }
    }
}

function main() {
    console.log("=== Test 17: Transition Enter Args ===");
    const s = new TransitionEnterArgs();

    // Initial state is Idle
    let log = s.get_log();
    if (log.length !== 0) {
        throw new Error(`Expected empty log, got ${JSON.stringify(log)}`);
    }

    // Transition to Active with args
    s.start();
    log = s.get_log();
    if (!log.includes("idle:start")) {
        throw new Error(`Expected 'idle:start' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("active:enter:from_idle:42")) {
        throw new Error(`Expected 'active:enter:from_idle:42' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`Log after transition: ${JSON.stringify(log)}`);

    console.log("PASS: Transition enter args work correctly");
}

main();
