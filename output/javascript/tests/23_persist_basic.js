
export class PersistTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class PersistTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class PersistTestCompartment {
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
        const c = new PersistTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class PersistTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    value = 0;
    name = "default";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new PersistTestCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new PersistTestFrameEvent("$>", null);
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
            const exit_event = new PersistTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new PersistTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new PersistTestFrameEvent("$>", this.__compartment.enter_args);
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

    set_value(v) {
        const __e = new PersistTestFrameEvent("set_value", {"v": v});
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_value() {
        const __e = new PersistTestFrameEvent("get_value", null);
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    go_active() {
        const __e = new PersistTestFrameEvent("go_active", null);
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    go_idle() {
        const __e = new PersistTestFrameEvent("go_idle", null);
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Idle(__e) {
        if (__e._message === "get_value") {
            this._context_stack[this._context_stack.length - 1]._return = this.value;
            return;;
        } else if (__e._message === "go_active") {
            const __compartment = new PersistTestCompartment("Active", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "go_idle") {
            // Already idle
        } else if (__e._message === "set_value") {
            const v = __e._parameters?.["v"];
            this.value = v;
        }
    }

    _state_Active(__e) {
        if (__e._message === "get_value") {
            this._context_stack[this._context_stack.length - 1]._return = this.value;
            return;;
        } else if (__e._message === "go_active") {
            // Already active
        } else if (__e._message === "go_idle") {
            const __compartment = new PersistTestCompartment("Idle", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "set_value") {
            const v = __e._parameters?.["v"];
            this.value = v * 2;
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
            value: this.value,
            name: this.name,
        });
    }

    static restoreState(json) {
        const deserializeComp = (data) => {
            if (!data) return null;
            const comp = new PersistTestCompartment(data.state);
            comp.state_args = {...(data.state_args || {})};
            comp.state_vars = {...(data.state_vars || {})};
            comp.enter_args = {...(data.enter_args || {})};
            comp.exit_args = {...(data.exit_args || {})};
            comp.forward_event = data.forward_event;
            comp.parent_compartment = deserializeComp(data.parent_compartment);
            return comp;
        };
        const data = JSON.parse(json);
        const instance = Object.create(PersistTest.prototype);
        instance.__compartment = deserializeComp(data._compartment);
        instance.__next_compartment = null;
        instance._state_stack = (data._state_stack || []).map((c) => deserializeComp(c));
        instance._context_stack = [];
        instance.value = data.value;
        instance.name = data.name;
        return instance;
    }
}

function main() {
    console.log("=== Test 23: Persist Basic (JavaScript) ===");

    // Test 1: Create and modify system
    const s1 = new PersistTest();
    s1.set_value(10);
    s1.go_active();
    s1.set_value(5);  // Should be doubled to 10 in Active state

    // Test 2: Save state
    const json = s1.saveState();
    const data = JSON.parse(json);
    if (data._compartment.state !== 'Active') {
        throw new Error(`Expected 'Active', got ${data._compartment.state}`);
    }
    if (data.value !== 10) {
        throw new Error(`Expected 10, got ${data.value}`);
    }
    console.log(`1. Saved state: ${json}`);

    // Test 3: Restore state
    const s2 = PersistTest.restoreState(json);
    if (s2.get_value() !== 10) {
        throw new Error(`Expected 10, got ${s2.get_value()}`);
    }
    console.log(`2. Restored value: ${s2.get_value()}`);

    // Test 4: Verify state is preserved (Active state doubles)
    s2.set_value(3);  // Should be doubled to 6 in Active state
    if (s2.get_value() !== 6) {
        throw new Error(`Expected 6, got ${s2.get_value()}`);
    }
    console.log(`3. After set_value(3) in Active: ${s2.get_value()}`);

    // Test 5: Verify transitions work after restore
    s2.go_idle();
    s2.set_value(4);  // Should NOT be doubled in Idle state
    if (s2.get_value() !== 4) {
        throw new Error(`Expected 4, got ${s2.get_value()}`);
    }
    console.log(`4. After go_idle, set_value(4): ${s2.get_value()}`);

    console.log("PASS: Persist basic works correctly");
}

main();
