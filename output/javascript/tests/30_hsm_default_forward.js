
export class HSMDefaultForwardFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMDefaultForwardFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMDefaultForwardCompartment {
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
        const c = new HSMDefaultForwardCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMDefaultForward {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMDefaultForwardCompartment("Parent", null);
        this.__compartment = new HSMDefaultForwardCompartment("Child", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMDefaultForwardFrameEvent("$>", null);
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
            const exit_event = new HSMDefaultForwardFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMDefaultForwardFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMDefaultForwardFrameEvent("$>", this.__compartment.enter_args);
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

    handled_event() {
        const __e = new HSMDefaultForwardFrameEvent("handled_event", null);
        const __ctx = new HSMDefaultForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    unhandled_event() {
        const __e = new HSMDefaultForwardFrameEvent("unhandled_event", null);
        const __ctx = new HSMDefaultForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMDefaultForwardFrameEvent("get_log", null);
        const __ctx = new HSMDefaultForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Child(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "handled_event") {
            this.log.push("Child:handled_event")
        } else {
            this._state_Parent(__e);
        }
    }

    _state_Parent(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "handled_event") {
            this.log.push("Parent:handled_event")
        } else if (__e._message === "unhandled_event") {
            this.log.push("Parent:unhandled_event")
        }
    }
}

function main() {
    console.log("=== Test 30: HSM State-Level Default Forward ===");
    const s = new HSMDefaultForward();

    s.handled_event();
    let log = s.get_log();
    if (!log.includes("Child:handled_event")) {
        throw new Error(`Expected 'Child:handled_event' in log, got ${log}`);
    }
    console.log(`After handled_event: ${JSON.stringify(log)}`);

    s.unhandled_event();
    log = s.get_log();
    if (!log.includes("Parent:unhandled_event")) {
        throw new Error(`Expected 'Parent:unhandled_event' in log (forwarded), got ${log}`);
    }
    console.log(`After unhandled_event (forwarded): ${JSON.stringify(log)}`);

    console.log("PASS: HSM state-level default forward works correctly");
}

main();
