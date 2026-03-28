
// Test 41: HSM Single Parent Relationship
//
// Tests basic child-parent HSM relationship:
// - Child declares parent with `=> $Parent` syntax
// - Child can forward events to parent
// - Child remains current state after forward
// - Parent handler executes and returns control

export class HSMSingleParentFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMSingleParentFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMSingleParentCompartment {
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
        const c = new HSMSingleParentCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMSingleParent {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMSingleParentCompartment("Parent", null);
        this.__compartment = new HSMSingleParentCompartment("Child", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMSingleParentFrameEvent("$>", null);
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
            const exit_event = new HSMSingleParentFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMSingleParentFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMSingleParentFrameEvent("$>", this.__compartment.enter_args);
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

    child_only() {
        const __e = new HSMSingleParentFrameEvent("child_only", null);
        const __ctx = new HSMSingleParentFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forward_to_parent() {
        const __e = new HSMSingleParentFrameEvent("forward_to_parent", null);
        const __ctx = new HSMSingleParentFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMSingleParentFrameEvent("get_log", null);
        const __ctx = new HSMSingleParentFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMSingleParentFrameEvent("get_state", null);
        const __ctx = new HSMSingleParentFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Child(__e) {
        if (__e._message === "child_only") {
            this.log.push("Child:child_only")
        } else if (__e._message === "forward_to_parent") {
            this.log.push("Child:before_forward")
            this._state_Parent(__e);
            this.log.push("Child:after_forward")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Child";
            return;
        }
    }

    _state_Parent(__e) {
        if (__e._message === "forward_to_parent") {
            this.log.push("Parent:forward_to_parent")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
            return;
        }
    }
}

function main() {
    console.log("=== Test 41: HSM Single Parent ===");
    const s = new HSMSingleParent();

    // TC1.1.1: Child declares parent with `=> $Parent` syntax (verified by compilation)
    console.log("TC1.1.1: Child-Parent relationship compiles - PASS");

    // TC1.1.2: Child can forward events to parent
    s.forward_to_parent();
    let log = s.get_log();
    if (!log.includes("Child:before_forward")) throw new Error(`Expected Child:before_forward in log, got ${JSON.stringify(log)}`);
    if (!log.includes("Parent:forward_to_parent")) throw new Error(`Expected Parent:forward_to_parent in log, got ${JSON.stringify(log)}`);
    console.log(`TC1.1.2: Child forwards to parent - PASS (log: ${JSON.stringify(log)})`);

    // TC1.1.3: Child remains the current state (no transition occurs on forward)
    const state = s.get_state();
    if (state !== "Child") throw new Error(`Expected state 'Child', got '${state}'`);
    console.log("TC1.1.3: Child remains current state after forward - PASS");

    // TC1.1.4: Parent handler executes and returns control
    // Verified by "Child:after_forward" appearing after parent execution
    if (!log.includes("Child:after_forward")) throw new Error(`Expected Child:after_forward in log (after parent), got ${JSON.stringify(log)}`);
    const idx_parent = log.indexOf("Parent:forward_to_parent");
    const idx_after = log.indexOf("Child:after_forward");
    if (idx_after <= idx_parent) throw new Error("Expected Child:after_forward after Parent handler");
    console.log("TC1.1.4: Parent executes and returns control - PASS");

    // TC1.1.5: Child-only event not forwarded
    s.child_only();
    log = s.get_log();
    const count = log.filter(x => x === "Child:child_only").length;
    if (count !== 1) throw new Error(`Expected exactly 1 Child:child_only, got ${JSON.stringify(log)}`);
    console.log("TC1.1.5: Child-only event handled locally - PASS");

    console.log("PASS: HSM single parent relationship works correctly");
}

main();
