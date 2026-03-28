
// Test: Heavy native prolog and epilog with edge-case JavaScript syntax.

class NativeHelper {
    // Mentions @@system and -> $State in comments
    // These should NOT be parsed as Frame

    static TEMPLATE = `
    {
        "@@target": "not_real",
        "-> $State": "just a string",
        "push$": true
    }
    `;

    process(data) {
        const result = JSON.stringify({"key": "value with { braces }"});
        // Comment with -> $Transition and => $^ and push$
        return result;
    }
}

// Global with @@ in string
const GLOBAL_CONFIG = {
    "description": "Config with @@system-like syntax",
    "pattern": "-> $Start",
};

export class HeavyNativePrologFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HeavyNativePrologFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HeavyNativePrologCompartment {
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
        const c = new HeavyNativePrologCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HeavyNativeProlog {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new HeavyNativePrologCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new HeavyNativePrologFrameEvent("$>", null);
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
            const exit_event = new HeavyNativePrologFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HeavyNativePrologFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HeavyNativePrologFrameEvent("$>", this.__compartment.enter_args);
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

    run_test() {
        const __e = new HeavyNativePrologFrameEvent("run_test", null);
        const __ctx = new HeavyNativePrologFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Start(__e) {
        if (__e._message === "run_test") {
            const h = new NativeHelper();
            const result = h.process(GLOBAL_CONFIG);
            if (result !== null) {
                console.log("PASS: Heavy native prolog handled correctly");
            } else {
                throw new Error("FAIL");
            }
        }
    }
}

// Heavy epilog
class PostSystem {
    constructor() {
        this.data = {"@@system": "in dict", "-> $State": "in dict"};
    }

    run() {
        // -> $NotATransition
        // => $^
        return true;
    }
}

const s = new HeavyNativeProlog();
s.run_test();
const p = new PostSystem();
if (!p.run()) { throw new Error("epilog failed"); }
