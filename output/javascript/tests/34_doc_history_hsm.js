
// Documentation Example: HSM with History (History203)
// Refactored common gotoC behavior into parent state $AB

export class HistoryHSMFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HistoryHSMFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HistoryHSMCompartment {
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
        const c = new HistoryHSMCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HistoryHSM {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new HistoryHSMCompartment("Waiting");
        this.__next_compartment = null;
        const __frame_event = new HistoryHSMFrameEvent("$>", null);
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
            const exit_event = new HistoryHSMFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HistoryHSMFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HistoryHSMFrameEvent("$>", this.__compartment.enter_args);
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

    gotoA() {
        const __e = new HistoryHSMFrameEvent("gotoA", null);
        const __ctx = new HistoryHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    gotoB() {
        const __e = new HistoryHSMFrameEvent("gotoB", null);
        const __ctx = new HistoryHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    gotoC() {
        const __e = new HistoryHSMFrameEvent("gotoC", null);
        const __ctx = new HistoryHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    goBack() {
        const __e = new HistoryHSMFrameEvent("goBack", null);
        const __ctx = new HistoryHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_state() {
        const __e = new HistoryHSMFrameEvent("get_state", null);
        const __ctx = new HistoryHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_log() {
        const __e = new HistoryHSMFrameEvent("get_log", null);
        const __ctx = new HistoryHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Waiting(__e) {
        if (__e._message === "$>") {
            this.log_msg("In $Waiting")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Waiting";
            return;
        } else if (__e._message === "gotoA") {
            this.log_msg("gotoA")
            const __compartment = new HistoryHSMCompartment("A", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "gotoB") {
            this.log_msg("gotoB")
            const __compartment = new HistoryHSMCompartment("B", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_AB(__e) {
        if (__e._message === "gotoC") {
            this.log_msg("gotoC in $AB")
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new HistoryHSMCompartment("C", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_A(__e) {
        if (__e._message === "$>") {
            this.log_msg("In $A")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "A";
            return;
        } else if (__e._message === "gotoB") {
            this.log_msg("gotoB")
            const __compartment = new HistoryHSMCompartment("B", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else {
            this._state_AB(__e);
        }
    }

    _state_B(__e) {
        if (__e._message === "$>") {
            this.log_msg("In $B")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "B";
            return;
        } else if (__e._message === "gotoA") {
            this.log_msg("gotoA")
            const __compartment = new HistoryHSMCompartment("A", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else {
            this._state_AB(__e);
        }
    }

    _state_C(__e) {
        if (__e._message === "$>") {
            this.log_msg("In $C")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "C";
            return;
        } else if (__e._message === "goBack") {
            this.log_msg("goBack")
            this.__transition(this._state_stack.pop());
            return;
        }
    }

    log_msg(msg) {
                    this.log.push(msg)
    }
}

function main() {
    console.log("=== Test 34: Doc History HSM ===");
    const h = new HistoryHSM();

    // Start in Waiting
    if (h.get_state() !== "Waiting") {
        throw new Error(`Expected 'Waiting', got '${h.get_state()}'`);
    }

    // Go to A
    h.gotoA();
    if (h.get_state() !== "A") {
        throw new Error(`Expected 'A', got '${h.get_state()}'`);
    }

    // Go to C (using inherited gotoC from $AB)
    h.gotoC();
    if (h.get_state() !== "C") {
        throw new Error(`Expected 'C', got '${h.get_state()}'`);
    }

    // Go back (should pop to A)
    h.goBack();
    if (h.get_state() !== "A") {
        throw new Error(`Expected 'A' after goBack, got '${h.get_state()}'`);
    }

    // Go to B
    h.gotoB();
    if (h.get_state() !== "B") {
        throw new Error(`Expected 'B', got '${h.get_state()}'`);
    }

    // Go to C (again using inherited gotoC)
    h.gotoC();
    if (h.get_state() !== "C") {
        throw new Error(`Expected 'C', got '${h.get_state()}'`);
    }

    // Go back (should pop to B)
    h.goBack();
    if (h.get_state() !== "B") {
        throw new Error(`Expected 'B' after goBack, got '${h.get_state()}'`);
    }

    console.log("Log:", h.get_log());
    console.log("PASS: HSM with history works correctly");
}

main();
