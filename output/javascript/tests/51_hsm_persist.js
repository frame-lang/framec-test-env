
// Test 51: HSM Persistence
//
// Tests that HSM parent compartment chain is properly saved and restored:
// - Child state vars preserved
// - Parent state vars preserved
// - Parent compartment chain intact after restore
// - Forwarding to parent still works after restore

export class HSMPersistFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMPersistFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMPersistCompartment {
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
        const c = new HSMPersistCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMPersist {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMPersistCompartment("Parent", null);
        __parent_comp_0.state_vars["parent_count"] = 100;
        this.__compartment = new HSMPersistCompartment("Child", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMPersistFrameEvent("$>", null);
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
            const exit_event = new HSMPersistFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMPersistFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMPersistFrameEvent("$>", this.__compartment.enter_args);
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

    increment_child() {
        const __e = new HSMPersistFrameEvent("increment_child", null);
        const __ctx = new HSMPersistFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    increment_parent() {
        const __e = new HSMPersistFrameEvent("increment_parent", null);
        const __ctx = new HSMPersistFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_child_count() {
        const __e = new HSMPersistFrameEvent("get_child_count", null);
        const __ctx = new HSMPersistFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_parent_count() {
        const __e = new HSMPersistFrameEvent("get_parent_count", null);
        const __ctx = new HSMPersistFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMPersistFrameEvent("get_state", null);
        const __ctx = new HSMPersistFrameContext(__e, null);
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
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
            return;
        } else if (__e._message === "increment_parent") {
            __sv_comp.state_vars["parent_count"] = __sv_comp.state_vars["parent_count"] + 1;
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
            // Forward to parent
            this._state_Parent(__e);
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Child";
            return;
        } else if (__e._message === "increment_child") {
            __sv_comp.state_vars["child_count"] = __sv_comp.state_vars["child_count"] + 1;
        } else if (__e._message === "increment_parent") {
            // Forward to parent
            this._state_Parent(__e);
        }
    }

    saveState() {
        const serializeComp = (c) => {
            if (!c) return null;
            return {
                state: c.state,
                state_args: {...c.state_args},
                state_vars: {...c.state_vars},
                enter_args: {...c.enter_args},
                exit_args: {...c.exit_args},
                forward_event: c.forward_event,
                parent_compartment: serializeComp(c.parent_compartment),
            };
        };
        return JSON.stringify({
            _compartment: serializeComp(this.__compartment),
            _state_stack: this._state_stack.map((c) => serializeComp(c)),
        });
    }

    static restoreState(json) {
        const deserializeComp = (data) => {
            if (!data) return null;
            const comp = new HSMPersistCompartment(data.state);
            comp.state_args = {...(data.state_args || {})};
            comp.state_vars = {...(data.state_vars || {})};
            comp.enter_args = {...(data.enter_args || {})};
            comp.exit_args = {...(data.exit_args || {})};
            comp.forward_event = data.forward_event;
            comp.parent_compartment = deserializeComp(data.parent_compartment);
            return comp;
        };
        const data = JSON.parse(json);
        const instance = Object.create(HSMPersist.prototype);
        instance.__compartment = deserializeComp(data._compartment);
        instance.__next_compartment = null;
        instance._state_stack = (data._state_stack || []).map((c) => deserializeComp(c));
        instance._context_stack = [];
        return instance;
    }
}

function main() {
    console.log("=== Test 51: HSM Persistence ===");

    // Create system and modify state vars at both levels
    const s1 = new HSMPersist();

    // Verify initial state
    console.assert(s1.get_state() === "Child", `Expected Child, got ${s1.get_state()}`);
    console.assert(s1.get_child_count() === 0, `Expected 0, got ${s1.get_child_count()}`);
    console.assert(s1.get_parent_count() === 100, `Expected 100, got ${s1.get_parent_count()}`);
    console.log("1. Initial state verified: Child with child_count=0, parent_count=100");

    // Modify state vars at both levels
    s1.increment_child();
    s1.increment_child();
    s1.increment_child();  // child_count = 3
    s1.increment_parent();
    s1.increment_parent();  // parent_count = 102

    console.assert(s1.get_child_count() === 3, `Expected 3, got ${s1.get_child_count()}`);
    console.assert(s1.get_parent_count() === 102, `Expected 102, got ${s1.get_parent_count()}`);
    console.log(`2. After increments: child_count=${s1.get_child_count()}, parent_count=${s1.get_parent_count()}`);

    // Save state
    const data = s1.saveState();
    console.assert(typeof data === "string", `Expected string, got ${typeof data}`);
    console.log(`3. Saved state: ${data.length} chars`);

    // Restore to new instance
    const s2 = HSMPersist.restoreState(data);

    // Verify restored state
    console.assert(s2.get_state() === "Child", `Expected Child after restore, got ${s2.get_state()}`);
    console.log(`4. Restored state: ${s2.get_state()}`);

    // Verify child state var preserved
    console.assert(s2.get_child_count() === 3, `Expected child_count=3, got ${s2.get_child_count()}`);
    console.log(`5. Child state var preserved: child_count=${s2.get_child_count()}`);

    // Verify parent state var preserved (requires parent compartment chain)
    console.assert(s2.get_parent_count() === 102, `Expected parent_count=102, got ${s2.get_parent_count()}`);
    console.log(`6. Parent state var preserved: parent_count=${s2.get_parent_count()}`);

    // Verify state machine still works after restore
    s2.increment_child();
    s2.increment_parent();
    console.assert(s2.get_child_count() === 4, `Expected 4, got ${s2.get_child_count()}`);
    console.assert(s2.get_parent_count() === 103, `Expected 103, got ${s2.get_parent_count()}`);
    console.log(`7. After post-restore increments: child_count=${s2.get_child_count()}, parent_count=${s2.get_parent_count()}`);

    console.log("PASS: HSM persistence works correctly");
}

main();
