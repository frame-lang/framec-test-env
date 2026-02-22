
// Documentation Example: HSM with History (History203)
// Refactored common gotoC behavior into parent state $AB


class HistoryHSMFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class HistoryHSMCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: HistoryHSMCompartment | null;

    constructor(state: string, parent_compartment: HistoryHSMCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): HistoryHSMCompartment {
        const c = new HistoryHSMCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class HistoryHSM {
    private _state_stack: Array<any>;
    private __compartment: HistoryHSMCompartment;
    private __next_compartment: HistoryHSMCompartment | null;
    private _return_value: any;
    private log: string[] =     [];

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.log =         [];
        this.__compartment = new HistoryHSMCompartment("Waiting");
        this.__next_compartment = null;
        const __frame_event = new HistoryHSMFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: HistoryHSMFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new HistoryHSMFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HistoryHSMFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HistoryHSMFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: HistoryHSMFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: HistoryHSMCompartment) {
        this.__next_compartment = next_compartment;
    }

    public gotoA() {
        const __e = new HistoryHSMFrameEvent("gotoA", null);
        this.__kernel(__e);
    }

    public gotoB() {
        const __e = new HistoryHSMFrameEvent("gotoB", null);
        this.__kernel(__e);
    }

    public gotoC() {
        const __e = new HistoryHSMFrameEvent("gotoC", null);
        this.__kernel(__e);
    }

    public goBack() {
        const __e = new HistoryHSMFrameEvent("goBack", null);
        this.__kernel(__e);
    }

    public get_state(): string {
        this._return_value = null;
        const __e = new HistoryHSMFrameEvent("get_state", null);
        this.__kernel(__e);
        return this._return_value;
    }

    public get_log(): string[] {
        this._return_value = null;
        const __e = new HistoryHSMFrameEvent("get_log", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Waiting(__e: HistoryHSMFrameEvent) {
        if (__e._message === "$>") {
            this.log_msg("In $Waiting")
        } else if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "get_state") {
            this._return_value = "Waiting";
            __e._return = this._return_value;
            return;
        } else if (__e._message === "gotoA") {
            this.log_msg("gotoA")
            const __compartment = new HistoryHSMCompartment("A", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "gotoB") {
            this.log_msg("gotoB")
            const __compartment = new HistoryHSMCompartment("B", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private _state_AB(__e: HistoryHSMFrameEvent) {
        if (__e._message === "gotoC") {
            this.log_msg("gotoC in $AB")
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new HistoryHSMCompartment("C", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private _state_C(__e: HistoryHSMFrameEvent) {
        if (__e._message === "$>") {
            this.log_msg("In $C")
        } else if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "get_state") {
            this._return_value = "C";
            __e._return = this._return_value;
            return;
        } else if (__e._message === "goBack") {
            this.log_msg("goBack")
            this.__compartment = this._state_stack.pop()!;
            return;
        }
    }

    private _state_A(__e: HistoryHSMFrameEvent) {
        if (__e._message === "$>") {
            this.log_msg("In $A")
        } else if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "get_state") {
            this._return_value = "A";
            __e._return = this._return_value;
            return;
        } else if (__e._message === "gotoB") {
            this.log_msg("gotoB")
            const __compartment = new HistoryHSMCompartment("B", this.__compartment.copy());
            this.__transition(__compartment);
        } else {
            this._state_AB(__e);
        }
    }

    private _state_B(__e: HistoryHSMFrameEvent) {
        if (__e._message === "$>") {
            this.log_msg("In $B")
        } else if (__e._message === "get_log") {
            this._return_value = this.log;
            __e._return = this._return_value;
            return;
        } else if (__e._message === "get_state") {
            this._return_value = "B";
            __e._return = this._return_value;
            return;
        } else if (__e._message === "gotoA") {
            this.log_msg("gotoA")
            const __compartment = new HistoryHSMCompartment("A", this.__compartment.copy());
            this.__transition(__compartment);
        } else {
            this._state_AB(__e);
        }
    }

    private log_msg(msg: string) {
                    this.log.push(msg)
    }
}


function main() {
    console.log("=== Test 34: Doc History HSM ===");
    const h = new HistoryHSM();

    // Start in Waiting
    if (h.get_state() !== "Waiting") {
        throw new Error(`Expected 'Waiting', got '${h.get_state()}'`);
    }

    // Go to A
    h.gotoA();
    if (h.get_state() !== "A") {
        throw new Error(`Expected 'A', got '${h.get_state()}'`);
    }

    // Go to C (using inherited gotoC from $AB)
    h.gotoC();
    if (h.get_state() !== "C") {
        throw new Error(`Expected 'C', got '${h.get_state()}'`);
    }

    // Go back (should pop to A)
    h.goBack();
    if (h.get_state() !== "A") {
        throw new Error(`Expected 'A' after goBack, got '${h.get_state()}'`);
    }

    // Go to B
    h.gotoB();
    if (h.get_state() !== "B") {
        throw new Error(`Expected 'B', got '${h.get_state()}'`);
    }

    // Go to C (again using inherited gotoC)
    h.gotoC();
    if (h.get_state() !== "C") {
        throw new Error(`Expected 'C', got '${h.get_state()}'`);
    }

    // Go back (should pop to B)
    h.goBack();
    if (h.get_state() !== "B") {
        throw new Error(`Expected 'B' after goBack, got '${h.get_state()}'`);
    }

    console.log("Log:", h.get_log());
    console.log("PASS: HSM with history works correctly");
}

main();
