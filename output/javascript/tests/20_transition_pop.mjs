
export class TransitionPopTestFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class TransitionPopTestFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class TransitionPopTestCompartment {
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
        const c = new TransitionPopTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class TransitionPopTest {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new TransitionPopTestCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new TransitionPopTestFrameEvent("$>", null);
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
            const exit_event = new TransitionPopTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new TransitionPopTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new TransitionPopTestFrameEvent("$>", this.__compartment.enter_args);
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

    start() {
        const __e = new TransitionPopTestFrameEvent("start", null);
        const __ctx = new TransitionPopTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    process() {
        const __e = new TransitionPopTestFrameEvent("process", null);
        const __ctx = new TransitionPopTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_state() {
        const __e = new TransitionPopTestFrameEvent("get_state", null);
        const __ctx = new TransitionPopTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_log() {
        const __e = new TransitionPopTestFrameEvent("get_log", null);
        const __ctx = new TransitionPopTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Working(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Working";
            return;;
        } else if (__e._message === "process") {
            this.log.push("working:process:before_pop");
            this.__transition(this._state_stack.pop());
            return;
            // This should NOT execute because pop transitions away
            this.log.push("working:process:after_pop");
        }
    }

    _state_Idle(__e) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Idle";
            return;;
        } else if (__e._message === "process") {
            this.log.push("idle:process");
        } else if (__e._message === "start") {
            this.log.push("idle:start:push");
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new TransitionPopTestCompartment("Working", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("=== Test 20: Transition Pop (JavaScript) ===");
    const s = new TransitionPopTest();

    // Initial state should be Idle
    if (s.get_state() !== "Idle") throw new Error(`Expected 'Idle', got '${s.get_state()}'`);
    console.log(`Initial state: ${s.get_state()}`);

    // start() pushes Idle, transitions to Working
    s.start();
    if (s.get_state() !== "Working") throw new Error(`Expected 'Working', got '${s.get_state()}'`);
    console.log(`After start(): ${s.get_state()}`);

    // process() in Working does pop transition back to Idle
    s.process();
    if (s.get_state() !== "Idle") throw new Error(`Expected 'Idle' after pop, got '${s.get_state()}'`);
    console.log(`After process() with pop: ${s.get_state()}`);

    const log = s.get_log();
    console.log(`Log: ${JSON.stringify(log)}`);

    // Verify log contents
    if (!log.includes("idle:start:push")) throw new Error("Expected 'idle:start:push' in log");
    if (!log.includes("working:process:before_pop")) throw new Error("Expected 'working:process:before_pop' in log");
    if (log.includes("working:process:after_pop")) throw new Error("Should NOT have 'working:process:after_pop' in log");

    console.log("PASS: Transition pop works correctly");
}

main();
