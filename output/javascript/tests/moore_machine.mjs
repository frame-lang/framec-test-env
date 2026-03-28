
// Moore Machine - output depends ONLY on state (output on entry)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

export class MooreMachineFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class MooreMachineFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class MooreMachineCompartment {
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
        const c = new MooreMachineCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class MooreMachine {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    current_output = 0;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new MooreMachineCompartment("Q0");
        this.__next_compartment = null;
        const __frame_event = new MooreMachineFrameEvent("$>", null);
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
            const exit_event = new MooreMachineFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new MooreMachineFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new MooreMachineFrameEvent("$>", this.__compartment.enter_args);
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

    i_0() {
        const __e = new MooreMachineFrameEvent("i_0", null);
        const __ctx = new MooreMachineFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    i_1() {
        const __e = new MooreMachineFrameEvent("i_1", null);
        const __ctx = new MooreMachineFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Q0(__e) {
        if (__e._message === "$>") {
            this.set_output(0);
        } else if (__e._message === "i_0") {
            const __compartment = new MooreMachineCompartment("Q1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            const __compartment = new MooreMachineCompartment("Q2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Q1(__e) {
        if (__e._message === "$>") {
            this.set_output(0);
        } else if (__e._message === "i_0") {
            const __compartment = new MooreMachineCompartment("Q1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            const __compartment = new MooreMachineCompartment("Q3", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Q2(__e) {
        if (__e._message === "$>") {
            this.set_output(0);
        } else if (__e._message === "i_0") {
            const __compartment = new MooreMachineCompartment("Q4", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            const __compartment = new MooreMachineCompartment("Q2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Q4(__e) {
        if (__e._message === "$>") {
            this.set_output(1);
        } else if (__e._message === "i_0") {
            const __compartment = new MooreMachineCompartment("Q1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            const __compartment = new MooreMachineCompartment("Q3", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Q3(__e) {
        if (__e._message === "$>") {
            this.set_output(1);
        } else if (__e._message === "i_0") {
            const __compartment = new MooreMachineCompartment("Q4", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            const __compartment = new MooreMachineCompartment("Q2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    set_output(value) {
                    this.current_output = value;
    }

    get_output() {
                    return this.current_output;
    }
}

function main() {
    console.log("TAP version 14");
    console.log("1..5");

    const m = new MooreMachine();

    // Initial state Q0 has output 0
    if (m.get_output() === 0) {
        console.log("ok 1 - moore initial state Q0 has output 0");
    } else {
        console.log(`not ok 1 - moore initial state Q0 has output 0 # got ${m.get_output()}`);
    }

    // i_0: Q0 -> Q1 (output 0)
    m.i_0();
    if (m.get_output() === 0) {
        console.log("ok 2 - moore Q1 has output 0");
    } else {
        console.log(`not ok 2 - moore Q1 has output 0 # got ${m.get_output()}`);
    }

    // i_1: Q1 -> Q3 (output 1)
    m.i_1();
    if (m.get_output() === 1) {
        console.log("ok 3 - moore Q3 has output 1");
    } else {
        console.log(`not ok 3 - moore Q3 has output 1 # got ${m.get_output()}`);
    }

    // i_0: Q3 -> Q4 (output 1)
    m.i_0();
    if (m.get_output() === 1) {
        console.log("ok 4 - moore Q4 has output 1");
    } else {
        console.log(`not ok 4 - moore Q4 has output 1 # got ${m.get_output()}`);
    }

    // i_0: Q4 -> Q1 (output 0)
    m.i_0();
    if (m.get_output() === 0) {
        console.log("ok 5 - moore Q1 has output 0 again");
    } else {
        console.log(`not ok 5 - moore Q1 has output 0 again # got ${m.get_output()}`);
    }

    console.log("# PASS - Moore machine outputs depend ONLY on state");
}

main();
