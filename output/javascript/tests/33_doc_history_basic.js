
// Documentation Example: History with push$/pop$ (History201)

export class HistoryBasicFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HistoryBasicFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HistoryBasicCompartment {
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
        const c = new HistoryBasicCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HistoryBasic {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new HistoryBasicCompartment("A");
        this.__next_compartment = null;
        const __frame_event = new HistoryBasicFrameEvent("$>", null);
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
            const exit_event = new HistoryBasicFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HistoryBasicFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HistoryBasicFrameEvent("$>", this.__compartment.enter_args);
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

    gotoC_from_A() {
        const __e = new HistoryBasicFrameEvent("gotoC_from_A", null);
        const __ctx = new HistoryBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    gotoC_from_B() {
        const __e = new HistoryBasicFrameEvent("gotoC_from_B", null);
        const __ctx = new HistoryBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    gotoB() {
        const __e = new HistoryBasicFrameEvent("gotoB", null);
        const __ctx = new HistoryBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    return_back() {
        const __e = new HistoryBasicFrameEvent("return_back", null);
        const __ctx = new HistoryBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_state() {
        const __e = new HistoryBasicFrameEvent("get_state", null);
        const __ctx = new HistoryBasicFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_A(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "A";
            return;
        } else if (__e._message === "gotoB") {
            const __compartment = new HistoryBasicCompartment("B", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "gotoC_from_A") {
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new HistoryBasicCompartment("C", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_B(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "B";
            return;
        } else if (__e._message === "gotoC_from_B") {
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new HistoryBasicCompartment("C", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_C(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "C";
            return;
        } else if (__e._message === "return_back") {
            this.__transition(this._state_stack.pop());
            return;
        }
    }
}

function main() {
    console.log("=== Test 33: Doc History Basic ===");
    const h = new HistoryBasic();

    // Start in A
    if (h.get_state() !== "A") {
        throw new Error(`Expected 'A', got '${h.get_state()}'`);
    }

    // Go to C from A (push A)
    h.gotoC_from_A();
    if (h.get_state() !== "C") {
        throw new Error(`Expected 'C', got '${h.get_state()}'`);
    }

    // Return back (pop to A)
    h.return_back();
    if (h.get_state() !== "A") {
        throw new Error(`Expected 'A' after pop, got '${h.get_state()}'`);
    }

    // Now go to B
    h.gotoB();
    if (h.get_state() !== "B") {
        throw new Error(`Expected 'B', got '${h.get_state()}'`);
    }

    // Go to C from B (push B)
    h.gotoC_from_B();
    if (h.get_state() !== "C") {
        throw new Error(`Expected 'C', got '${h.get_state()}'`);
    }

    // Return back (pop to B)
    h.return_back();
    if (h.get_state() !== "B") {
        throw new Error(`Expected 'B' after pop, got '${h.get_state()}'`);
    }

    console.log("PASS: History push/pop works correctly");
}

main();
