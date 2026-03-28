
// Test 49: HSM Enter/Exit with Parameters
//
// Tests enter and exit handlers with parameters in HSM context:
// - Exit params passed correctly
// - Enter params passed to target state
// - Transition syntax: (exit_args) -> (enter_args) $Target

export class HSMEnterExitParamsFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMEnterExitParamsFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMEnterExitParamsCompartment {
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
        const c = new HSMEnterExitParamsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMEnterExitParams {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new HSMEnterExitParamsCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new HSMEnterExitParamsFrameEvent("$>", null);
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
            const exit_event = new HSMEnterExitParamsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMEnterExitParamsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMEnterExitParamsFrameEvent("$>", this.__compartment.enter_args);
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

    go_to_a() {
        const __e = new HSMEnterExitParamsFrameEvent("go_to_a", null);
        const __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    go_to_sibling() {
        const __e = new HSMEnterExitParamsFrameEvent("go_to_sibling", null);
        const __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    go_back() {
        const __e = new HSMEnterExitParamsFrameEvent("go_back", null);
        const __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMEnterExitParamsFrameEvent("get_log", null);
        const __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMEnterExitParamsFrameEvent("get_state", null);
        const __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Parent(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
            return;
        }
    }

    _state_ChildA(__e) {
        if (__e._message === "<$") {
            const reason = __e._parameters?.["0"];
            this.log.push(`ChildA:exit(${reason})`)
        } else if (__e._message === "$>") {
            const msg = __e._parameters?.["0"];
            this.log.push(`ChildA:enter(${msg})`)
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "ChildA";
            return;
        } else if (__e._message === "go_to_sibling") {
            this.__compartment.exit_args = Object.fromEntries(["leaving_A"].map((v, i) => [String(i), v]));
            const __compartment = new HSMEnterExitParamsCompartment("ChildB", this.__compartment.copy());
            __compartment.enter_args = Object.fromEntries(["arriving_B"].map((v, i) => [String(i), v]));
            this.__transition(__compartment);
            return;
        }
    }

    _state_Start(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Start";
            return;
        } else if (__e._message === "go_to_a") {
            const __compartment = new HSMEnterExitParamsCompartment("ChildA", this.__compartment.copy());
            __compartment.enter_args = Object.fromEntries(["starting"].map((v, i) => [String(i), v]));
            this.__transition(__compartment);
            return;
        }
    }

    _state_ChildB(__e) {
        if (__e._message === "<$") {
            const reason = __e._parameters?.["0"];
            this.log.push(`ChildB:exit(${reason})`)
        } else if (__e._message === "$>") {
            const msg = __e._parameters?.["0"];
            this.log.push(`ChildB:enter(${msg})`)
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "ChildB";
            return;
        } else if (__e._message === "go_back") {
            this.__compartment.exit_args = Object.fromEntries(["leaving_B"].map((v, i) => [String(i), v]));
            const __compartment = new HSMEnterExitParamsCompartment("ChildA", this.__compartment.copy());
            __compartment.enter_args = Object.fromEntries(["returning_A"].map((v, i) => [String(i), v]));
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("=== Test 49: HSM Enter/Exit with Params ===");
    const s = new HSMEnterExitParams();

    // First go to ChildA with enter params
    s.go_to_a();
    let log = s.get_log();
    if (!log.includes("ChildA:enter(starting)")) throw new Error(`Expected ChildA:enter(starting), got ${JSON.stringify(log)}`);
    console.log("TC2.5.0: Initial transition with enter params - PASS");

    // TC2.5.1: Exit params passed correctly
    s.go_to_sibling();
    log = s.get_log();
    if (!log.includes("ChildA:exit(leaving_A)")) throw new Error(`Expected exit with param, got ${JSON.stringify(log)}`);
    console.log("TC2.5.1: Exit params passed correctly - PASS");

    // TC2.5.2: Enter params passed to target state
    if (!log.includes("ChildB:enter(arriving_B)")) throw new Error(`Expected enter with param, got ${JSON.stringify(log)}`);
    if (s.get_state() !== "ChildB") throw new Error(`Expected ChildB, got ${s.get_state()}`);
    console.log("TC2.5.2: Enter params passed to target - PASS");

    // TC2.5.3: Return transition with different params
    s.go_back();
    log = s.get_log();
    if (!log.includes("ChildB:exit(leaving_B)")) throw new Error(`Expected ChildB exit, got ${JSON.stringify(log)}`);
    if (!log.includes("ChildA:enter(returning_A)")) throw new Error(`Expected ChildA enter, got ${JSON.stringify(log)}`);
    console.log("TC2.5.3: Return transition with params - PASS");

    console.log("PASS: HSM enter/exit with params works correctly");
}

main();
