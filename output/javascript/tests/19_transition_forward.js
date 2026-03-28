
export class EventForwardTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class EventForwardTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class EventForwardTestCompartment {
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
        const c = new EventForwardTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class EventForwardTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new EventForwardTestCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new EventForwardTestFrameEvent("$>", null);
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
            const exit_event = new EventForwardTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new EventForwardTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new EventForwardTestFrameEvent("$>", this.__compartment.enter_args);
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

    process() {
        const __e = new EventForwardTestFrameEvent("process", null);
        const __ctx = new EventForwardTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new EventForwardTestFrameEvent("get_log", null);
        const __ctx = new EventForwardTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Working(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "process") {
            this.log.push("working:process");
        }
    }

    _state_Idle(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "process") {
            this.log.push("idle:process:before");
            const __compartment = new EventForwardTestCompartment("Working", this.__compartment.copy());
            __compartment.forward_event = __e;
            this.__transition(__compartment);
            return;
            // This should NOT execute because -> => returns after dispatch
            this.log.push("idle:process:after");
        }
    }
}

function main() {
    console.log("=== Test 19: Transition Forward (JavaScript) ===");
    const s = new EventForwardTest();
    s.process();
    const log = s.get_log();
    console.log(`Log: ${JSON.stringify(log)}`);

    // After transition-forward:
    // - Idle logs "idle:process:before"
    // - Transition to Working
    // - Working handles process(), logs "working:process"
    // - Return prevents "idle:process:after"
    if (!log.includes("idle:process:before")) {
        throw new Error(`Expected 'idle:process:before' in log: ${log}`);
    }
    if (!log.includes("working:process")) {
        throw new Error(`Expected 'working:process' in log: ${log}`);
    }
    if (log.includes("idle:process:after")) {
        throw new Error(`Should NOT have 'idle:process:after' in log: ${log}`);
    }

    console.log("PASS: Transition forward works correctly");
}

main();
