
// =============================================================================
// Test 01: Interface Return
// =============================================================================
// Validates that event handler returns work correctly via the context stack.
// Tests both syntaxes:
//   - return value     (sugar - expands to @@:return = value)
//   - @@:return = value (explicit context assignment)
// =============================================================================

export class InterfaceReturnFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class InterfaceReturnFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class InterfaceReturnCompartment {
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
        const c = new InterfaceReturnCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class InterfaceReturn {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new InterfaceReturnCompartment("Active");
        this.__next_compartment = null;
        const __frame_event = new InterfaceReturnFrameEvent("$>", null);
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
            const exit_event = new InterfaceReturnFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new InterfaceReturnFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new InterfaceReturnFrameEvent("$>", this.__compartment.enter_args);
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

    bool_return() {
        const __e = new InterfaceReturnFrameEvent("bool_return", null);
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    int_return() {
        const __e = new InterfaceReturnFrameEvent("int_return", null);
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    string_return() {
        const __e = new InterfaceReturnFrameEvent("string_return", null);
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    conditional_return(x) {
        const __e = new InterfaceReturnFrameEvent("conditional_return", {"x": x});
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    computed_return(a, b) {
        const __e = new InterfaceReturnFrameEvent("computed_return", {"a": a, "b": b});
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    explicit_bool() {
        const __e = new InterfaceReturnFrameEvent("explicit_bool", null);
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    explicit_int() {
        const __e = new InterfaceReturnFrameEvent("explicit_int", null);
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    explicit_string() {
        const __e = new InterfaceReturnFrameEvent("explicit_string", null);
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    explicit_conditional(x) {
        const __e = new InterfaceReturnFrameEvent("explicit_conditional", {"x": x});
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    explicit_computed(a, b) {
        const __e = new InterfaceReturnFrameEvent("explicit_computed", {"a": a, "b": b});
        const __ctx = new InterfaceReturnFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Active(__e) {
        if (__e._message === "bool_return") {
            this._context_stack[this._context_stack.length - 1]._return = true;
            return;;
        } else if (__e._message === "computed_return") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            const result = a * b + 10;
            this._context_stack[this._context_stack.length - 1]._return = result;
            return;;
        } else if (__e._message === "conditional_return") {
            const x = __e._parameters?.["x"];
            if (x < 0) {
                this._context_stack[this._context_stack.length - 1]._return = "negative";
                return;;
            } else if (x === 0) {
                this._context_stack[this._context_stack.length - 1]._return = "zero";
                return;;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = "positive";
                return;;
            }
        } else if (__e._message === "explicit_bool") {
            this._context_stack[this._context_stack.length - 1]._return = true;
        } else if (__e._message === "explicit_computed") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            const result = a * b + 10;
            this._context_stack[this._context_stack.length - 1]._return = result;
        } else if (__e._message === "explicit_conditional") {
            const x = __e._parameters?.["x"];
            if (x < 0) {
                this._context_stack[this._context_stack.length - 1]._return = "negative";
                return;
            } else if (x === 0) {
                this._context_stack[this._context_stack.length - 1]._return = "zero";
                return;
            } else {
                this._context_stack[this._context_stack.length - 1]._return = "positive";
            }
        } else if (__e._message === "explicit_int") {
            this._context_stack[this._context_stack.length - 1]._return = 42;
        } else if (__e._message === "explicit_string") {
            this._context_stack[this._context_stack.length - 1]._return = "Frame";
        } else if (__e._message === "int_return") {
            this._context_stack[this._context_stack.length - 1]._return = 42;
            return;;
        } else if (__e._message === "string_return") {
            this._context_stack[this._context_stack.length - 1]._return = "Frame";
            return;;
        }
    }
}

function main() {
    console.log("=== Test 01: Interface Return (JavaScript) ===");
    const s = new InterfaceReturn();
    const errors = [];

    console.log("-- Testing 'return value' sugar --");

    let r = s.bool_return();
    if (r !== true) {
        errors.push(`bool_return: expected true, got ${r}`);
    } else {
        console.log(`1. bool_return() = ${r}`);
    }

    r = s.int_return();
    if (r !== 42) {
        errors.push(`int_return: expected 42, got ${r}`);
    } else {
        console.log(`2. int_return() = ${r}`);
    }

    r = s.string_return();
    if (r !== "Frame") {
        errors.push(`string_return: expected 'Frame', got '${r}'`);
    } else {
        console.log(`3. string_return() = '${r}'`);
    }

    r = s.conditional_return(-5);
    if (r !== "negative") {
        errors.push(`conditional_return(-5): expected 'negative', got '${r}'`);
    }
    r = s.conditional_return(0);
    if (r !== "zero") {
        errors.push(`conditional_return(0): expected 'zero', got '${r}'`);
    }
    r = s.conditional_return(10);
    if (r !== "positive") {
        errors.push(`conditional_return(10): expected 'positive', got '${r}'`);
    } else {
        console.log(`4. conditional_return(-5,0,10) = 'negative','zero','positive'`);
    }

    r = s.computed_return(3, 4);
    if (r !== 22) {
        errors.push(`computed_return(3,4): expected 22, got ${r}`);
    } else {
        console.log(`5. computed_return(3,4) = ${r}`);
    }

    console.log("-- Testing '@@:return = value' explicit --");

    r = s.explicit_bool();
    if (r !== true) {
        errors.push(`explicit_bool: expected true, got ${r}`);
    } else {
        console.log(`6. explicit_bool() = ${r}`);
    }

    r = s.explicit_int();
    if (r !== 42) {
        errors.push(`explicit_int: expected 42, got ${r}`);
    } else {
        console.log(`7. explicit_int() = ${r}`);
    }

    r = s.explicit_string();
    if (r !== "Frame") {
        errors.push(`explicit_string: expected 'Frame', got '${r}'`);
    } else {
        console.log(`8. explicit_string() = '${r}'`);
    }

    r = s.explicit_conditional(-5);
    if (r !== "negative") {
        errors.push(`explicit_conditional(-5): expected 'negative', got '${r}'`);
    }
    r = s.explicit_conditional(0);
    if (r !== "zero") {
        errors.push(`explicit_conditional(0): expected 'zero', got '${r}'`);
    }
    r = s.explicit_conditional(10);
    if (r !== "positive") {
        errors.push(`explicit_conditional(10): expected 'positive', got '${r}'`);
    } else {
        console.log(`9. explicit_conditional(-5,0,10) = 'negative','zero','positive'`);
    }

    r = s.explicit_computed(3, 4);
    if (r !== 22) {
        errors.push(`explicit_computed(3,4): expected 22, got ${r}`);
    } else {
        console.log(`10. explicit_computed(3,4) = ${r}`);
    }

    if (errors.length > 0) {
        for (const e of errors) {
            console.log(`FAIL: ${e}`);
        }
        throw new Error(`${errors.length} test(s) failed`);
    } else {
        console.log("PASS: All interface return tests passed");
    }
}

main();
