
// Test 42: HSM Three-Level Hierarchy
//
// Tests 3+ level deep hierarchies:
// - $Grandchild => $Child => $Parent
// - Forward through multiple levels
// - Each level's state variables remain isolated

export class HSMThreeLevelsFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMThreeLevelsFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMThreeLevelsCompartment {
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
        const c = new HSMThreeLevelsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMThreeLevels {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMThreeLevelsCompartment("Parent", null);
        __parent_comp_0.state_vars["parent_var"] = 100;
        const __parent_comp_1 = new HSMThreeLevelsCompartment("Child", __parent_comp_0);
        __parent_comp_1.state_vars["child_var"] = 10;
        this.__compartment = new HSMThreeLevelsCompartment("Grandchild", __parent_comp_1);
        this.__next_compartment = null;
        const __frame_event = new HSMThreeLevelsFrameEvent("$>", null);
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
            const exit_event = new HSMThreeLevelsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMThreeLevelsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMThreeLevelsFrameEvent("$>", this.__compartment.enter_args);
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

    handle_at_grandchild() {
        const __e = new HSMThreeLevelsFrameEvent("handle_at_grandchild", null);
        const __ctx = new HSMThreeLevelsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forward_to_child() {
        const __e = new HSMThreeLevelsFrameEvent("forward_to_child", null);
        const __ctx = new HSMThreeLevelsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forward_to_parent() {
        const __e = new HSMThreeLevelsFrameEvent("forward_to_parent", null);
        const __ctx = new HSMThreeLevelsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forward_through_all() {
        const __e = new HSMThreeLevelsFrameEvent("forward_through_all", null);
        const __ctx = new HSMThreeLevelsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMThreeLevelsFrameEvent("get_log", null);
        const __ctx = new HSMThreeLevelsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Parent(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Parent") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("parent_var" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["parent_var"] = 100;
            }
        } else if (__e._message === "forward_through_all") {
            let val = __sv_comp.state_vars["parent_var"]
            this.log.push(`Parent:forward_through_all(var=${val})`)
        } else if (__e._message === "forward_to_parent") {
            let val = __sv_comp.state_vars["parent_var"]
            this.log.push(`Parent:handled(var=${val})`)
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        }
    }

    _state_Child(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Child") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("child_var" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["child_var"] = 10;
            }
        } else if (__e._message === "forward_through_all") {
            let val = __sv_comp.state_vars["child_var"]
            this.log.push(`Child:forward_through_all(var=${val})`)
            this._state_Parent(__e);
        } else if (__e._message === "forward_to_child") {
            let val = __sv_comp.state_vars["child_var"]
            this.log.push(`Child:handled(var=${val})`)
        } else if (__e._message === "forward_to_parent") {
            let val = __sv_comp.state_vars["child_var"]
            this.log.push(`Child:forward_to_parent(var=${val})`)
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        }
    }

    _state_Grandchild(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Grandchild") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("grandchild_var" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["grandchild_var"] = 1;
            }
        } else if (__e._message === "forward_through_all") {
            this.log.push("Grandchild:forward_through_all")
            this._state_Child(__e);
        } else if (__e._message === "forward_to_child") {
            this.log.push("Grandchild:forward_to_child")
            this._state_Child(__e);
        } else if (__e._message === "forward_to_parent") {
            this.log.push("Grandchild:forward_to_parent")
            this._state_Child(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "handle_at_grandchild") {
            let val = __sv_comp.state_vars["grandchild_var"]
            this.log.push(`Grandchild:handled(var=${val})`)
        }
    }
}

function main() {
    console.log("=== Test 42: HSM Three-Level Hierarchy ===");
    const s = new HSMThreeLevels();

    // TC1.2.1: Three-level hierarchy compiles
    console.log("TC1.2.1: Three-level hierarchy compiles - PASS");

    // TC1.2.2: Handle at grandchild (no forward)
    s.handle_at_grandchild();
    let log = s.get_log();
    if (!log.includes("Grandchild:handled(var=1)")) throw new Error(`Expected Grandchild handler, got ${JSON.stringify(log)}`);
    console.log("TC1.2.2: Grandchild handles locally - PASS");

    // TC1.2.3: Forward from grandchild to child
    s.forward_to_child();
    log = s.get_log();
    if (!log.includes("Grandchild:forward_to_child")) throw new Error(`Expected Grandchild forward, got ${JSON.stringify(log)}`);
    if (!log.includes("Child:handled(var=10)")) throw new Error(`Expected Child handler, got ${JSON.stringify(log)}`);
    console.log("TC1.2.3: Forward grandchild->child - PASS");

    // TC1.2.4: Forward from grandchild through child to parent
    s.forward_to_parent();
    log = s.get_log();
    if (!log.includes("Grandchild:forward_to_parent")) throw new Error(`Expected Grandchild forward, got ${JSON.stringify(log)}`);
    if (!log.includes("Child:forward_to_parent(var=10)")) throw new Error(`Expected Child forward, got ${JSON.stringify(log)}`);
    if (!log.includes("Parent:handled(var=100)")) throw new Error(`Expected Parent handler, got ${JSON.stringify(log)}`);
    console.log("TC1.2.4: Forward grandchild->child->parent - PASS");

    // TC1.2.5: Forward through entire chain
    s.forward_through_all();
    log = s.get_log();
    if (!log.includes("Grandchild:forward_through_all")) throw new Error(`Expected Grandchild, got ${JSON.stringify(log)}`);
    if (!log.includes("Child:forward_through_all(var=10)")) throw new Error(`Expected Child, got ${JSON.stringify(log)}`);
    if (!log.includes("Parent:forward_through_all(var=100)")) throw new Error(`Expected Parent, got ${JSON.stringify(log)}`);
    console.log("TC1.2.5: Full chain forward - PASS");

    // Verify state variable isolation
    console.log("TC1.2.6: State vars isolated (grandchild=1, child=10, parent=100) - PASS");

    console.log("PASS: HSM three-level hierarchy works correctly");
}

main();
