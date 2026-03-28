
export class HSMForwardFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMForwardFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMForwardCompartment {
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
        const c = new HSMForwardCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMForward {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMForwardCompartment("Parent", null);
        this.__compartment = new HSMForwardCompartment("Child", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMForwardFrameEvent("$>", null);
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
            const exit_event = new HSMForwardFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMForwardFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMForwardFrameEvent("$>", this.__compartment.enter_args);
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

    event_a() {
        const __e = new HSMForwardFrameEvent("event_a", null);
        const __ctx = new HSMForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    event_b() {
        const __e = new HSMForwardFrameEvent("event_b", null);
        const __ctx = new HSMForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMForwardFrameEvent("get_log", null);
        const __ctx = new HSMForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Child(__e) {
        if (__e._message === "event_a") {
            this.log.push("Child:event_a");
        } else if (__e._message === "event_b") {
            this.log.push("Child:event_b_forward");
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        }
    }

    _state_Parent(__e) {
        if (__e._message === "event_a") {
            this.log.push("Parent:event_a");
        } else if (__e._message === "event_b") {
            this.log.push("Parent:event_b");
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        }
    }
}

function main() {
    console.log("=== Test 08: HSM Forward ===");
    const s = new HSMForward();

    // event_a should be handled by Child (no forward)
    s.event_a();
    let log = s.get_log();
    if (!log.includes("Child:event_a")) {
        throw new Error(`Expected 'Child:event_a' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After event_a: ${JSON.stringify(log)}`);

    // event_b should forward to Parent
    s.event_b();
    log = s.get_log();
    if (!log.includes("Child:event_b_forward")) {
        throw new Error(`Expected 'Child:event_b_forward' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("Parent:event_b")) {
        throw new Error(`Expected 'Parent:event_b' in log (forwarded), got ${JSON.stringify(log)}`);
    }
    console.log(`After event_b (forwarded): ${JSON.stringify(log)}`);

    console.log("PASS: HSM forward works correctly");
}

main();
