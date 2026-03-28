
// Test 46: HSM Enter in Parent Only
//
// Tests enter handler in parent only:
// - Parent has $>(), child does not
// - Child enters without error (no enter handler)
// - Parent's enter does NOT auto-fire when child is entered
// - Parent enter only fires when transitioning directly TO parent

export class HSMEnterParentOnlyFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMEnterParentOnlyFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMEnterParentOnlyCompartment {
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
        const c = new HSMEnterParentOnlyCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMEnterParentOnly {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new HSMEnterParentOnlyCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new HSMEnterParentOnlyFrameEvent("$>", null);
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
            const exit_event = new HSMEnterParentOnlyFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMEnterParentOnlyFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMEnterParentOnlyFrameEvent("$>", this.__compartment.enter_args);
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
        const __e = new HSMEnterParentOnlyFrameEvent("go_to_child", null);
        const __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    go_to_parent() {
        const __e = new HSMEnterParentOnlyFrameEvent("go_to_parent", null);
        const __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMEnterParentOnlyFrameEvent("get_log", null);
        const __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMEnterParentOnlyFrameEvent("get_state", null);
        const __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Parent(__e) {
        if (__e._message === "$>") {
            this.log.push("Parent:enter")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
            return;
        } else if (__e._message === "go_to_child") {
            const __compartment = new HSMEnterParentOnlyCompartment("Child", this.__compartment.copy());
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
        } else if (__e._message === "go_to_child") {
            const __compartment = new HSMEnterParentOnlyCompartment("Child", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "go_to_parent") {
            const __compartment = new HSMEnterParentOnlyCompartment("Parent", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Child(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Child";
            return;
        } else if (__e._message === "go_to_parent") {
            const __compartment = new HSMEnterParentOnlyCompartment("Parent", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("=== Test 46: HSM Enter in Parent Only ===");
    const s = new HSMEnterParentOnly();

    // TC2.2.1: Child enters without error (no enter handler)
    s.go_to_child();
    if (s.get_state() !== "Child") throw new Error(`Expected Child, got ${s.get_state()}`);
    let log = s.get_log();
    console.log(`TC2.2.1: Child enters without error (log: ${JSON.stringify(log)}) - PASS`);

    // TC2.2.2: Parent's enter does NOT auto-fire when child is entered
    if (log.includes("Parent:enter")) throw new Error(`Parent:enter should NOT fire for child entry, got ${JSON.stringify(log)}`);
    console.log("TC2.2.2: Parent enter NOT auto-fired for child - PASS");

    // TC2.2.3: Parent enter only fires when transitioning directly TO parent
    s.go_to_parent();
    if (s.get_state() !== "Parent") throw new Error(`Expected Parent, got ${s.get_state()}`);
    log = s.get_log();
    if (!log.includes("Parent:enter")) throw new Error(`Expected Parent:enter when transitioning to Parent, got ${JSON.stringify(log)}`);
    console.log("TC2.2.3: Parent enter fires when transitioning to Parent - PASS");

    // TC2.2.4: Going back to child from parent
    s.go_to_child();
    if (s.get_state() !== "Child") throw new Error(`Expected Child, got ${s.get_state()}`);
    log = s.get_log();
    // Parent enter should have fired only once (when we went to Parent)
    const count = log.filter(x => x === "Parent:enter").length;
    if (count !== 1) throw new Error(`Expected exactly 1 Parent:enter, got ${JSON.stringify(log)}`);
    console.log("TC2.2.4: Return to child, parent enter count unchanged - PASS");

    console.log("PASS: HSM enter in parent only works correctly");
}

main();
