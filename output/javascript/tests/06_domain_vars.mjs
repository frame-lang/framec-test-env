
export class DomainVarsFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class DomainVarsFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class DomainVarsCompartment {
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
        const c = new DomainVarsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class DomainVars {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    count = 0;
    name = "counter";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new DomainVarsCompartment("Counting");
        this.__next_compartment = null;
        const __frame_event = new DomainVarsFrameEvent("$>", null);
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
            const exit_event = new DomainVarsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new DomainVarsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new DomainVarsFrameEvent("$>", this.__compartment.enter_args);
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

    increment() {
        const __e = new DomainVarsFrameEvent("increment", null);
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    decrement() {
        const __e = new DomainVarsFrameEvent("decrement", null);
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_count() {
        const __e = new DomainVarsFrameEvent("get_count", null);
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    set_count(value) {
        const __e = new DomainVarsFrameEvent("set_count", {"value": value});
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Counting(__e) {
        if (__e._message === "decrement") {
            this.count -= 1;
            console.log(`${this.name}: decremented to ${this.count}`);
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = this.count;
            return;;
        } else if (__e._message === "increment") {
            this.count += 1;
            console.log(`${this.name}: incremented to ${this.count}`);
        } else if (__e._message === "set_count") {
            const value = __e._parameters?.["value"];
            this.count = value;
            console.log(`${this.name}: set to ${this.count}`);
        }
    }
}

function main() {
    console.log("=== Test 06: Domain Variables ===");
    const s = new DomainVars();

    // Initial value should be 0
    let count = s.get_count();
    if (count !== 0) {
        throw new Error(`Expected initial count=0, got ${count}`);
    }
    console.log(`Initial count: ${count}`);

    // Increment
    s.increment();
    count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }

    s.increment();
    count = s.get_count();
    if (count !== 2) {
        throw new Error(`Expected count=2, got ${count}`);
    }

    // Decrement
    s.decrement();
    count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }

    // Set directly
    s.set_count(100);
    count = s.get_count();
    if (count !== 100) {
        throw new Error(`Expected count=100, got ${count}`);
    }

    console.log(`Final count: ${count}`);
    console.log("PASS: Domain variables work correctly");
}

main();
