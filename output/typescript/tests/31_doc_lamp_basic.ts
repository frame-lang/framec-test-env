
// Documentation Example: Basic Lamp with enter/exit events


class LampFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class LampCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: LampCompartment | null;

    constructor(state: string, parent_compartment: LampCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): LampCompartment {
        const c = new LampCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class Lamp {
    private _state_stack: Array<any>;
    private __compartment: LampCompartment;
    private __next_compartment: LampCompartment | null;
    private _return_value: any;
    private color: string = "white";
    private switch_closed: boolean = false;

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.color = "white";
        this.switch_closed = false;
        this.__compartment = new LampCompartment("Off");
        this.__next_compartment = null;
        const __frame_event = new LampFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: LampFrameEvent) {
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

    private __router(__e: LampFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: LampCompartment) {
        this.__next_compartment = next_compartment;
    }

    public turnOn() {
        const __e = new LampFrameEvent("turnOn", null);
        this.__kernel(__e);
    }

    public turnOff() {
        const __e = new LampFrameEvent("turnOff", null);
        this.__kernel(__e);
    }

    public getColor(): string {
        this._return_value = null;
        const __e = new LampFrameEvent("getColor", null);
        this.__kernel(__e);
        return this._return_value;
    }

    public setColor(color: string) {
        const __e = new LampFrameEvent("setColor", {"0": color});
        this.__kernel(__e);
    }

    public isSwitchClosed(): boolean {
        this._return_value = null;
        const __e = new LampFrameEvent("isSwitchClosed", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_On(__e: LampFrameEvent) {
        if (__e._message === "<$") {
            this.openSwitch()
        } else if (__e._message === "$>") {
            this.closeSwitch()
        } else if (__e._message === "getColor") {
            this._return_value = this.color;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "isSwitchClosed") {
            this._return_value = this.switch_closed;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "setColor") {
            const color = __e._parameters?.["0"];
            this.color = color
        } else if (__e._message === "turnOff") {
            const __compartment = new LampCompartment("Off", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private _state_Off(__e: LampFrameEvent) {
        if (__e._message === "getColor") {
            this._return_value = this.color;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "isSwitchClosed") {
            this._return_value = this.switch_closed;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "setColor") {
            const color = __e._parameters?.["0"];
            this.color = color
        } else if (__e._message === "turnOn") {
            const __compartment = new LampCompartment("On", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private closeSwitch() {
                    this.switch_closed = true
    }

    private openSwitch() {
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
