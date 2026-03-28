
// Test 48: HSM Exit Handlers
//
// Tests exit handlers in HSM context:
// - Child exit fires when transitioning out of child
// - Parent exit does NOT fire when transitioning out of child
// - Exit handler can access child's state variables

export class HSMExitHandlersFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMExitHandlersFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMExitHandlersCompartment {
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
        const c = new HSMExitHandlersCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMExitHandlers {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMExitHandlersCompartment("Parent", null);
        this.__compartment = new HSMExitHandlersCompartment("Child", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMExitHandlersFrameEvent("$>", null);
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
            const exit_event = new HSMExitHandlersFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMExitHandlersFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMExitHandlersFrameEvent("$>", this.__compartment.enter_args);
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

    go_to_other() {
        const __e = new HSMExitHandlersFrameEvent("go_to_other", null);
        const __ctx = new HSMExitHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    go_to_parent() {
        const __e = new HSMExitHandlersFrameEvent("go_to_parent", null);
        const __ctx = new HSMExitHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    go_to_child() {
        const __e = new HSMExitHandlersFrameEvent("go_to_child", null);
        const __ctx = new HSMExitHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMExitHandlersFrameEvent("get_log", null);
        const __ctx = new HSMExitHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMExitHandlersFrameEvent("get_state", null);
        const __ctx = new HSMExitHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_child_var() {
        const __e = new HSMExitHandlersFrameEvent("get_child_var", null);
        const __ctx = new HSMExitHandlersFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Child(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Child") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "<$") {
            let val = __sv_comp.state_vars["child_var"]
            this.log.push(`Child:exit(var=${val})`)
        } else if (__e._message === "$>") {
            if (!("child_var" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["child_var"] = 42;
            }
            this.log.push("Child:enter")
        } else if (__e._message === "get_child_var") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["child_var"];
            return;
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Child";
            return;
        } else if (__e._message === "go_to_other") {
            const __compartment = new HSMExitHandlersCompartment("Other", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "go_to_parent") {
            const __compartment = new HSMExitHandlersCompartment("Parent", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Parent(__e) {
        if (__e._message === "<$") {
            this.log.push("Parent:exit")
        } else if (__e._message === "$>") {
            this.log.push("Parent:enter")
        } else if (__e._message === "get_child_var") {
            this._context_stack[this._context_stack.length - 1]._return = -1;
            return;
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
            return;
        } else if (__e._message === "go_to_child") {
            const __compartment = new HSMExitHandlersCompartment("Child", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "go_to_other") {
            const __compartment = new HSMExitHandlersCompartment("Other", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Other(__e) {
        if (__e._message === "$>") {
            this.log.push("Other:enter")
        } else if (__e._message === "get_child_var") {
            this._context_stack[this._context_stack.length - 1]._return = -1;
            return;
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Other";
            return;
        } else if (__e._message === "go_to_child") {
            const __compartment = new HSMExitHandlersCompartment("Child", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "go_to_parent") {
            const __compartment = new HSMExitHandlersCompartment("Parent", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("=== Test 48: HSM Exit Handlers ===");
    const s = new HSMExitHandlers();

    // Initial state is Child
    let log = s.get_log();
    if (!log.includes("Child:enter")) throw new Error(`Expected Child:enter on init, got ${JSON.stringify(log)}`);
    if (s.get_state() !== "Child") throw new Error(`Expected Child, got ${s.get_state()}`);
    console.log("TC2.4.0: Initial state is Child with enter - PASS");

    // TC2.4.1: Child exit fires when transitioning out of child
    s.go_to_other();
    log = s.get_log();
    if (!log.includes("Child:exit(var=42)")) throw new Error(`Expected Child:exit, got ${JSON.stringify(log)}`);
    if (!log.includes("Other:enter")) throw new Error(`Expected Other:enter, got ${JSON.stringify(log)}`);
    console.log("TC2.4.1: Child exit fires when transitioning out - PASS");

    // TC2.4.2: Parent exit does NOT fire when transitioning out of child
    if (log.includes("Parent:exit")) throw new Error(`Parent:exit should NOT fire for child exit, got ${JSON.stringify(log)}`);
    console.log("TC2.4.2: Parent exit NOT fired for child exit - PASS");

    // TC2.4.3: Exit handler can access child's state variables (verified by var=42 in log)
    console.log("TC2.4.3: Exit handler accesses state var (var=42) - PASS");

    // TC2.4.4: Parent exit fires when transitioning out of Parent
    s.go_to_parent();
    log = s.get_log();
    if (!log.includes("Parent:enter")) throw new Error(`Expected Parent:enter, got ${JSON.stringify(log)}`);

    s.go_to_other();
    log = s.get_log();
    if (!log.includes("Parent:exit")) throw new Error(`Expected Parent:exit, got ${JSON.stringify(log)}`);
    console.log("TC2.4.4: Parent exit fires when leaving parent - PASS");

    console.log("PASS: HSM exit handlers work correctly");
}

main();
