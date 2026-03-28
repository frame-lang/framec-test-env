
export class ForwardEnterFirstFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class ForwardEnterFirstFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class ForwardEnterFirstCompartment {
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
        const c = new ForwardEnterFirstCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class ForwardEnterFirst {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new ForwardEnterFirstCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new ForwardEnterFirstFrameEvent("$>", null);
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
            const exit_event = new ForwardEnterFirstFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ForwardEnterFirstFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new ForwardEnterFirstFrameEvent("$>", this.__compartment.enter_args);
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

    process() {
        const __e = new ForwardEnterFirstFrameEvent("process", null);
        const __ctx = new ForwardEnterFirstFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_counter() {
        const __e = new ForwardEnterFirstFrameEvent("get_counter", null);
        const __ctx = new ForwardEnterFirstFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_log() {
        const __e = new ForwardEnterFirstFrameEvent("get_log", null);
        const __ctx = new ForwardEnterFirstFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Working(__e) {
        // HSM: Navigate to this state's compartment for state var access
        let __sv_comp = this.__compartment;
        while (__sv_comp !== null && __sv_comp.state !== "Working") {
            __sv_comp = __sv_comp.parent_compartment;
        }
        if (__e._message === "$>") {
            if (!("counter" in __sv_comp.state_vars)) {
                __sv_comp.state_vars["counter"] = 100;
            }
            this.log.push("Working:enter")
        } else if (__e._message === "get_counter") {
            this._context_stack[this._context_stack.length - 1]._return = __sv_comp.state_vars["counter"];
            return;
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "process") {
            this.log.push("Working:process:counter=" + __sv_comp.state_vars["counter"].toString())
            __sv_comp.state_vars["counter"] = __sv_comp.state_vars["counter"] + 1;
        }
    }

    _state_Idle(__e) {
        if (__e._message === "get_counter") {
            this._context_stack[this._context_stack.length - 1]._return = -1;
            return;
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "process") {
            const __compartment = new ForwardEnterFirstCompartment("Working", this.__compartment.copy());
            __compartment.forward_event = __e;
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("=== Test 29: Forward Enter First ===");
    const s = new ForwardEnterFirst();

    if (s.get_counter() !== -1) {
        throw new Error("Expected -1 in Idle");
    }

    s.process();

    const counter = s.get_counter();
    const log = s.get_log();
    console.log(`Counter after forward: ${counter}`);
    console.log(`Log: ${JSON.stringify(log)}`);

    if (!log.includes("Working:enter")) {
        throw new Error(`Expected 'Working:enter' in log: ${log}`);
    }

    if (!log.includes("Working:process:counter=100")) {
        throw new Error(`Expected 'Working:process:counter=100' in log: ${log}`);
    }

    if (counter !== 101) {
        throw new Error(`Expected counter=101, got ${counter}`);
    }

    const enterIdx = log.indexOf("Working:enter");
    const processIdx = log.indexOf("Working:process:counter=100");
    if (enterIdx >= processIdx) {
        throw new Error(`$> should run before process: ${log}`);
    }

    console.log("PASS: Forward sends $> first for non-$> events");
}

main();
