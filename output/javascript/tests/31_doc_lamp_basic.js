
// Documentation Example: Basic Lamp with enter/exit events

export class LampFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class LampFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class LampCompartment {
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
        const c = new LampCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class Lamp {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    color = "white";
    switch_closed = false;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new LampCompartment("Off");
        this.__next_compartment = null;
        const __frame_event = new LampFrameEvent("$>", null);
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
            const exit_event = new LampFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new LampFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new LampFrameEvent("$>", this.__compartment.enter_args);
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

    turnOn() {
        const __e = new LampFrameEvent("turnOn", null);
        const __ctx = new LampFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    turnOff() {
        const __e = new LampFrameEvent("turnOff", null);
        const __ctx = new LampFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    getColor() {
        const __e = new LampFrameEvent("getColor", null);
        const __ctx = new LampFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    setColor(color) {
        const __e = new LampFrameEvent("setColor", {"color": color});
        const __ctx = new LampFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    isSwitchClosed() {
        const __e = new LampFrameEvent("isSwitchClosed", null);
        const __ctx = new LampFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_On(__e) {
        if (__e._message === "<$") {
            this.openSwitch()
        } else if (__e._message === "$>") {
            this.closeSwitch()
        } else if (__e._message === "getColor") {
            this._context_stack[this._context_stack.length - 1]._return = this.color;
            return;
        } else if (__e._message === "isSwitchClosed") {
            this._context_stack[this._context_stack.length - 1]._return = this.switch_closed;
            return;
        } else if (__e._message === "setColor") {
            const color = __e._parameters?.["color"];
            this.color = color
        } else if (__e._message === "turnOff") {
            const __compartment = new LampCompartment("Off", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Off(__e) {
        if (__e._message === "getColor") {
            this._context_stack[this._context_stack.length - 1]._return = this.color;
            return;
        } else if (__e._message === "isSwitchClosed") {
            this._context_stack[this._context_stack.length - 1]._return = this.switch_closed;
            return;
        } else if (__e._message === "setColor") {
            const color = __e._parameters?.["color"];
            this.color = color
        } else if (__e._message === "turnOn") {
            const __compartment = new LampCompartment("On", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    closeSwitch() {
                    this.switch_closed = true
    }

    openSwitch() {
                    this.switch_closed = false
    }
}

function main() {
    console.log("=== Test 31: Doc Lamp Basic ===");
    const lamp = new Lamp();

    // Initially off
    if (lamp.isSwitchClosed() !== false) {
        throw new Error("Switch should be open initially");
    }

    // Turn on - should close switch
    lamp.turnOn();
    if (lamp.isSwitchClosed() !== true) {
        throw new Error("Switch should be closed after turnOn");
    }

    // Check color
    if (lamp.getColor() !== "white") {
        throw new Error(`Expected 'white', got '${lamp.getColor()}'`);
    }

    // Set color
    lamp.setColor("blue");
    if (lamp.getColor() !== "blue") {
        throw new Error(`Expected 'blue', got '${lamp.getColor()}'`);
    }

    // Turn off - should open switch
    lamp.turnOff();
    if (lamp.isSwitchClosed() !== false) {
        throw new Error("Switch should be open after turnOff");
    }

    console.log("PASS: Basic lamp works correctly");
}

main();
