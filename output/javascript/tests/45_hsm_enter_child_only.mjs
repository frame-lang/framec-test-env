
// Test 45: HSM Enter in Child Only
//
// Tests enter handler in child only:
// - Child has $>(), parent does not
// - Child enter handler fires on entry
// - No error when parent lacks enter handler
// - Forward to parent works without parent having enter

export class HSMEnterChildOnlyFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMEnterChildOnlyFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMEnterChildOnlyCompartment {
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
        const c = new HSMEnterChildOnlyCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMEnterChildOnly {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new HSMEnterChildOnlyCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new HSMEnterChildOnlyFrameEvent("$>", null);
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
            const exit_event = new HSMEnterChildOnlyFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMEnterChildOnlyFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMEnterChildOnlyFrameEvent("$>", this.__compartment.enter_args);
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

    go_to_child() {
        const __e = new HSMEnterChildOnlyFrameEvent("go_to_child", null);
        const __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forward_action() {
        const __e = new HSMEnterChildOnlyFrameEvent("forward_action", null);
        const __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMEnterChildOnlyFrameEvent("get_log", null);
        const __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMEnterChildOnlyFrameEvent("get_state", null);
        const __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Parent(__e) {
        if (__e._message === "forward_action") {
            this.log.push("Parent:forward_action")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
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
        } else if (__e._message === "go_to_child") {
            const __compartment = new HSMEnterChildOnlyCompartment("Child", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Child(__e) {
        if (__e._message === "$>") {
            this.log.push("Child:enter")
        } else if (__e._message === "forward_action") {
            this.log.push("Child:forward")
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Child";
            return;
        }
    }
}

function main() {
    console.log("=== Test 45: HSM Enter in Child Only ===");
    const s = new HSMEnterChildOnly();

    // Start state has no enter
    if (s.get_state() !== "Start") throw new Error(`Expected Start, got ${s.get_state()}`);
    console.log("TC2.1.0: Initial state is Start - PASS");

    // TC2.1.1: Child enter handler fires on entry
    s.go_to_child();
    let log = s.get_log();
    if (!log.includes("Child:enter")) throw new Error(`Expected Child:enter, got ${JSON.stringify(log)}`);
    if (s.get_state() !== "Child") throw new Error(`Expected Child, got ${s.get_state()}`);
    console.log("TC2.1.1: Child enter handler fires - PASS");

    // TC2.1.2: No error when parent lacks enter (verified by compilation/execution)
    console.log("TC2.1.2: No error when parent lacks enter - PASS");

    // TC2.1.3: Forward to parent works without parent having enter
    s.forward_action();
    log = s.get_log();
    if (!log.includes("Child:forward")) throw new Error(`Expected Child:forward, got ${JSON.stringify(log)}`);
    if (!log.includes("Parent:forward_action")) throw new Error(`Expected Parent handler, got ${JSON.stringify(log)}`);
    console.log("TC2.1.3: Forward works without parent enter - PASS");

    console.log("PASS: HSM enter in child only works correctly");
}

main();
