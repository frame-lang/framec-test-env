
// Test 40: HSM Parent State Variables
//
// This test validates that parent and child states in an HSM hierarchy
// maintain SEPARATE compartments with independent state variables.
//
// EXPECTED ARCHITECTURE:
// - Child has its own compartment: {state: "Child", stateVars: {child_count: 0}}
// - Parent has its own compartment: {state: "Parent", stateVars: {parent_count: 100}}
// - Child's compartment.parentCompartment -> Parent's compartment
// - When child forwards to parent, parent accesses ITS OWN compartment

export class HSMParentStateVarsFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMParentStateVarsFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMParentStateVarsCompartment {
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
        const c = new HSMParentStateVarsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMParentStateVars {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMParentStateVarsCompartment("Parent", null);
        __parent_comp_0.state_vars["parent_count"] = 100;
        this.__compartment = new HSMParentStateVarsCompartment("Child", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMParentStateVarsFrameEvent("$>", null);
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
            const exit_event = new HSMParentStateVarsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMParentStateVarsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMParentStateVarsFrameEvent("$>", this.__compartment.enter_args);
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

    get_child_count() {
        const __e = new HSMParentStateVarsFrameEvent("get_child_count", null);
        const __ctx = new HSMParentStateVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_parent_count() {
        const __e = new HSMParentStateVarsFrameEvent("get_parent_count", null);
        const __ctx = new HSMParentStateVarsFrameContext(__e, null);
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
            if (!("parent_count" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["parent_count"] = 100;
            }
        } else if (__e._message === "get_parent_count") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["parent_count"];
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
            if (!("child_count" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["child_count"] = 0;
            }
        } else if (__e._message === "get_child_count") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["child_count"];
            return;
        } else if (__e._message === "get_parent_count") {
            this._state_Parent(__e);
        }
    }
}

function main() {
    console.log("=== Test 40: HSM Parent State Variables ===");
    const s = new HSMParentStateVars();

    const childCount = s.get_child_count();
    if (childCount !== 0) {
        throw new Error(`Expected child_count=0, got ${childCount}`);
    }
    console.log(`Child count: ${childCount}`);

    const parentCount = s.get_parent_count();
    if (parentCount !== 100) {
        throw new Error(`Expected parent_count=100, got ${parentCount}`);
    }
    console.log(`Parent count: ${parentCount}`);

    console.log("PASS: HSM parent state variables work correctly");
}

main();
