
// Test 50: HSM Omitted Handlers - Forwarding Behavior
//
// Tests behavior when handlers are omitted at various levels:
// - Event not handled in child, not forwarded = silent ignore
// - Event not handled in child, forwarded with `=> $^` = parent handles
// - State-level `=> $^` forwards all unhandled events

export class HSMOmittedHandlersFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMOmittedHandlersFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMOmittedHandlersCompartment {
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
        const c = new HSMOmittedHandlersCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMOmittedHandlers {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMOmittedHandlersCompartment("Parent", null);
        this.__compartment = new HSMOmittedHandlersCompartment("Child", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMOmittedHandlersFrameEvent("$>", null);
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
            const exit_event = new HSMOmittedHandlersFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMOmittedHandlersFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMOmittedHandlersFrameEvent("$>", this.__compartment.enter_args);
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

    handled_by_child() {
        const __e = new HSMOmittedHandlersFrameEvent("handled_by_child", null);
        const __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forwarded_explicitly() {
        const __e = new HSMOmittedHandlersFrameEvent("forwarded_explicitly", null);
        const __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    unhandled_no_forward() {
        const __e = new HSMOmittedHandlersFrameEvent("unhandled_no_forward", null);
        const __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMOmittedHandlersFrameEvent("get_log", null);
        const __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMOmittedHandlersFrameEvent("get_state", null);
        const __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Parent(__e) {
        if (__e._message === "forwarded_explicitly") {
            this.log.push("Parent:forwarded_explicitly")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
            return;
        } else if (__e._message === "handled_by_child") {
            this.log.push("Parent:handled_by_child")
        } else if (__e._message === "unhandled_no_forward") {
            this.log.push("Parent:unhandled_no_forward")
        }
    }

    _state_Child(__e) {
        if (__e._message === "forwarded_explicitly") {
            this.log.push("Child:before_forward")
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Child";
            return;
        } else if (__e._message === "handled_by_child") {
            this.log.push("Child:handled_by_child")
        }
    }
}

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

    child_handled() {
        const __e = new HSMDefaultForwardFrameEvent("child_handled", null);
        const __ctx = new HSMDefaultForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    parent_handled() {
        const __e = new HSMDefaultForwardFrameEvent("parent_handled", null);
        const __ctx = new HSMDefaultForwardFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    both_respond() {
        const __e = new HSMDefaultForwardFrameEvent("both_respond", null);
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
        if (__e._message === "child_handled") {
            this.log.push("Child:child_handled")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else {
            this._state_Parent(__e);
        }
    }

    _state_Parent(__e) {
        if (__e._message === "both_respond") {
            this.log.push("Parent:both_respond")
        } else if (__e._message === "child_handled") {
            this.log.push("Parent:child_handled")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "parent_handled") {
            this.log.push("Parent:parent_handled")
        }
    }
}

function main() {
    console.log("=== Test 50: HSM Omitted Handlers ===");

    // Part 1: Explicit forwarding vs no forwarding
    const s1 = new HSMOmittedHandlers();

    // TC2.6.1: Event handled by child only
    s1.handled_by_child();
    let log = s1.get_log();
    if (!log.includes("Child:handled_by_child")) throw new Error(`Expected Child handler, got ${JSON.stringify(log)}`);
    if (log.includes("Parent:handled_by_child")) throw new Error(`Parent should NOT be called, got ${JSON.stringify(log)}`);
    console.log("TC2.6.1: Handled by child, not forwarded - PASS");

    // TC2.6.2: Event explicitly forwarded to parent
    s1.forwarded_explicitly();
    log = s1.get_log();
    if (!log.includes("Child:before_forward")) throw new Error(`Expected Child forward, got ${JSON.stringify(log)}`);
    if (!log.includes("Parent:forwarded_explicitly")) throw new Error(`Expected Parent handler, got ${JSON.stringify(log)}`);
    console.log("TC2.6.2: Explicitly forwarded to parent - PASS");

    // TC2.6.3: Unhandled event with no forward - silently ignored
    // This should NOT crash and should NOT call parent
    s1.unhandled_no_forward();
    log = s1.get_log();
    if (log.includes("Parent:unhandled_no_forward")) throw new Error(`Unhandled should be ignored, got ${JSON.stringify(log)}`);
    console.log("TC2.6.3: Unhandled (no forward) is silently ignored - PASS");

    // Part 2: State-level default forward
    const s2 = new HSMDefaultForward();

    // TC2.6.4: Event handled by child (no forward despite => $^)
    s2.child_handled();
    log = s2.get_log();
    if (!log.includes("Child:child_handled")) throw new Error(`Expected Child handler, got ${JSON.stringify(log)}`);
    if (log.includes("Parent:child_handled")) throw new Error(`Handled by child, not forwarded, got ${JSON.stringify(log)}`);
    console.log("TC2.6.4: Child handles, not forwarded - PASS");

    // TC2.6.5: Unhandled event forwarded via => $^
    s2.parent_handled();
    log = s2.get_log();
    if (!log.includes("Parent:parent_handled")) throw new Error(`Expected Parent handler, got ${JSON.stringify(log)}`);
    console.log("TC2.6.5: Unhandled forwarded via state-level => $^ - PASS");

    // TC2.6.6: Another unhandled event forwarded
    s2.both_respond();
    log = s2.get_log();
    if (!log.includes("Parent:both_respond")) throw new Error(`Expected Parent handler, got ${JSON.stringify(log)}`);
    console.log("TC2.6.6: Default forward works for multiple events - PASS");

    console.log("PASS: HSM omitted handlers work correctly");
}

main();
