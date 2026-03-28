
// Documentation Example: HSM Lamp with color behavior factored out

export class LampHSMFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class LampHSMFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class LampHSMCompartment {
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
        const c = new LampHSMCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class LampHSM {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    color = "white";
    lamp_on = false;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new LampHSMCompartment("ColorBehavior", null);
        this.__compartment = new LampHSMCompartment("Off", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new LampHSMFrameEvent("$>", null);
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
            const exit_event = new LampHSMFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new LampHSMFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new LampHSMFrameEvent("$>", this.__compartment.enter_args);
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
        const __e = new LampHSMFrameEvent("turnOn", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    turnOff() {
        const __e = new LampHSMFrameEvent("turnOff", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    getColor() {
        const __e = new LampHSMFrameEvent("getColor", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    setColor(color) {
        const __e = new LampHSMFrameEvent("setColor", {"color": color});
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    isLampOn() {
        const __e = new LampHSMFrameEvent("isLampOn", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_ColorBehavior(__e) {
        if (__e._message === "getColor") {
            this._context_stack[this._context_stack.length - 1]._return = this.color;
            return;
        } else if (__e._message === "setColor") {
            const color = __e._parameters?.["color"];
            this.color = color
        }
    }

    _state_Off(__e) {
        if (__e._message === "isLampOn") {
            this._context_stack[this._context_stack.length - 1]._return = this.lamp_on;
            return;
        } else if (__e._message === "turnOn") {
            const __compartment = new LampHSMCompartment("On", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else {
            this._state_ColorBehavior(__e);
        }
    }

    _state_On(__e) {
        if (__e._message === "<$") {
            this.turnOffLamp()
        } else if (__e._message === "$>") {
            this.turnOnLamp()
        } else if (__e._message === "isLampOn") {
            this._context_stack[this._context_stack.length - 1]._return = this.lamp_on;
            return;
        } else if (__e._message === "turnOff") {
            const __compartment = new LampHSMCompartment("Off", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else {
            this._state_ColorBehavior(__e);
        }
    }

    turnOnLamp() {
                    this.lamp_on = true
    }

    turnOffLamp() {
                    this.lamp_on = false
    }
}

function main() {
    console.log("=== Test 32: Doc Lamp HSM ===");
    const lamp = new LampHSM();

    // Color behavior available in both states
    if (lamp.getColor() !== "white") {
        throw new Error(`Expected 'white', got '${lamp.getColor()}'`);
    }
    lamp.setColor("red");
    if (lamp.getColor() !== "red") {
        throw new Error(`Expected 'red', got '${lamp.getColor()}'`);
    }

    // Turn on
    lamp.turnOn();
    if (lamp.isLampOn() !== true) {
        throw new Error("Lamp should be on");
    }

    // Color still works when on
    lamp.setColor("green");
    if (lamp.getColor() !== "green") {
        throw new Error(`Expected 'green', got '${lamp.getColor()}'`);
    }

    // Turn off
    lamp.turnOff();
    if (lamp.isLampOn() !== false) {
        throw new Error("Lamp should be off");
    }

    // Color still works when off
    if (lamp.getColor() !== "green") {
        throw new Error(`Expected 'green', got '${lamp.getColor()}'`);
    }

    console.log("PASS: HSM lamp works correctly");
}

main();
