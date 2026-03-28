
// Mealy Machine - output depends on state AND input (output on transitions)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

export class MealyMachineFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class MealyMachineFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class MealyMachineCompartment {
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
        const c = new MealyMachineCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class MealyMachine {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    last_output = -1;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new MealyMachineCompartment("Q0");
        this.__next_compartment = null;
        const __frame_event = new MealyMachineFrameEvent("$>", null);
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
            const exit_event = new MealyMachineFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new MealyMachineFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new MealyMachineFrameEvent("$>", this.__compartment.enter_args);
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
        const __e = new MealyMachineFrameEvent("i_0", null);
        const __ctx = new MealyMachineFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    i_1() {
        const __e = new MealyMachineFrameEvent("i_1", null);
        const __ctx = new MealyMachineFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    _state_Q0(__e) {
        if (__e._message === "i_0") {
            this.emit_output(0);
            const __compartment = new MealyMachineCompartment("Q1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            this.emit_output(0);
            const __compartment = new MealyMachineCompartment("Q2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Q1(__e) {
        if (__e._message === "i_0") {
            this.emit_output(0);
            const __compartment = new MealyMachineCompartment("Q1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            this.emit_output(1);
            const __compartment = new MealyMachineCompartment("Q2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Q2(__e) {
        if (__e._message === "i_0") {
            this.emit_output(1);
            const __compartment = new MealyMachineCompartment("Q1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "i_1") {
            this.emit_output(0);
            const __compartment = new MealyMachineCompartment("Q2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    emit_output(value) {
                    this.last_output = value;
    }

    get_last_output() {
                    return this.last_output;
    }
}

function main() {
    console.log("TAP version 14");
    console.log("1..4");

    const m = new MealyMachine();

    m.i_0();  // Q0 -> Q1, output 0
    if (m.get_last_output() === 0) {
        console.log("ok 1 - mealy i_0 from Q0 outputs 0");
    } else {
        console.log(`not ok 1 - mealy i_0 from Q0 outputs 0 # got ${m.get_last_output()}`);
    }

    m.i_0();  // Q1 -> Q1, output 0
    if (m.get_last_output() === 0) {
        console.log("ok 2 - mealy i_0 from Q1 outputs 0");
    } else {
        console.log(`not ok 2 - mealy i_0 from Q1 outputs 0 # got ${m.get_last_output()}`);
    }

    m.i_1();  // Q1 -> Q2, output 1
    if (m.get_last_output() === 1) {
        console.log("ok 3 - mealy i_1 from Q1 outputs 1");
    } else {
        console.log(`not ok 3 - mealy i_1 from Q1 outputs 1 # got ${m.get_last_output()}`);
    }

    m.i_0();  // Q2 -> Q1, output 1
    if (m.get_last_output() === 1) {
        console.log("ok 4 - mealy i_0 from Q2 outputs 1");
    } else {
        console.log(`not ok 4 - mealy i_0 from Q2 outputs 1 # got ${m.get_last_output()}`);
    }

    console.log("# PASS - Mealy machine outputs depend on state AND input");
}

main();
