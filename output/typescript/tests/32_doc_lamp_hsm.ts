
// Documentation Example: HSM Lamp with color behavior factored out


class LampHSMFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class LampHSMFrameContext {
    public event: LampHSMFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: LampHSMFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class LampHSMCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: LampHSMCompartment | null;

    constructor(state: string, parent_compartment: LampHSMCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): LampHSMCompartment {
        const c = new LampHSMCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class LampHSM {
    private _state_stack: Array<any>;
    private __compartment: LampHSMCompartment;
    private __next_compartment: LampHSMCompartment | null;
    private _context_stack: Array<any>;
    private color: string = "white";
    private lamp_on: boolean = false;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.color = "white";
        this.lamp_on = false;
        this.__compartment = new LampHSMCompartment("Off");
        this.__next_compartment = null;
        const __frame_event = new LampHSMFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: LampHSMFrameEvent) {
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

    private __router(__e: LampHSMFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: LampHSMCompartment) {
        this.__next_compartment = next_compartment;
    }

    public turnOn() {
        const __e = new LampHSMFrameEvent("turnOn", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public turnOff() {
        const __e = new LampHSMFrameEvent("turnOff", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public getColor(): string {
        const __e = new LampHSMFrameEvent("getColor", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public setColor(color: string) {
        const __e = new LampHSMFrameEvent("setColor", {"color": color});
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public isLampOn(): boolean {
        const __e = new LampHSMFrameEvent("isLampOn", null);
        const __ctx = new LampHSMFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Off(__e: LampHSMFrameEvent) {
        if (__e._message === "isLampOn") {
            this._context_stack[this._context_stack.length - 1]._return = this.lamp_on;
            return;
        } else if (__e._message === "turnOn") {
            const __compartment = new LampHSMCompartment("On", this.__compartment.copy());
            this.__transition(__compartment);
        } else {
            this._state_ColorBehavior(__e);
        }
    }

    private _state_ColorBehavior(__e: LampHSMFrameEvent) {
        if (__e._message === "getColor") {
            this._context_stack[this._context_stack.length - 1]._return = this.color;
            return;
        } else if (__e._message === "setColor") {
            const color = __e._parameters?.["color"];
            this.color = color
        }
    }

    private _state_On(__e: LampHSMFrameEvent) {
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
        } else {
            this._state_ColorBehavior(__e);
        }
    }

    private turnOnLamp() {
                    this.lamp_on = true
    }

    private turnOffLamp() {
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
