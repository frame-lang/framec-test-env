class EnterExitFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class EnterExitFrameContext {
    public event: EnterExitFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: EnterExitFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class EnterExitCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: EnterExitCompartment | null;

    constructor(state: string, parent_compartment: EnterExitCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): EnterExitCompartment {
        const c = new EnterExitCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class EnterExit {
    private _state_stack: Array<any>;
    private __compartment: EnterExitCompartment;
    private __next_compartment: EnterExitCompartment | null;
    private _context_stack: Array<any>;
    private log: string[] =     [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.log =         [];
        this.__compartment = new EnterExitCompartment("Off");
        this.__next_compartment = null;
        const __frame_event = new EnterExitFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: EnterExitFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new EnterExitFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new EnterExitFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new EnterExitFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: EnterExitFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: EnterExitCompartment) {
        this.__next_compartment = next_compartment;
    }

    public toggle() {
        const __e = new EnterExitFrameEvent("toggle", null);
        const __ctx = new EnterExitFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_log(): string[] {
        const __e = new EnterExitFrameEvent("get_log", null);
        const __ctx = new EnterExitFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_On(__e: EnterExitFrameEvent) {
        if (__e._message === "<$") {
            this.log.push("exit:On");
            console.log("Exiting On state");
        } else if (__e._message === "$>") {
            this.log.push("enter:On");
            console.log("Entered On state");
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "toggle") {
            const __compartment = new EnterExitCompartment("Off", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private _state_Off(__e: EnterExitFrameEvent) {
        if (__e._message === "<$") {
            this.log.push("exit:Off");
            console.log("Exiting Off state");
        } else if (__e._message === "$>") {
            this.log.push("enter:Off");
            console.log("Entered Off state");
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "toggle") {
            const __compartment = new EnterExitCompartment("On", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }
}


function main() {
    console.log("=== Test 05: Enter/Exit Handlers ===");
    const s = new EnterExit();

    // Initial enter should have been called
    let log = s.get_log();
    if (!log.includes("enter:Off")) {
        throw new Error(`Expected 'enter:Off' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After construction: ${JSON.stringify(log)}`);

    // Toggle to On - should exit Off, enter On
    s.toggle();
    log = s.get_log();
    if (!log.includes("exit:Off")) {
        throw new Error(`Expected 'exit:Off' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("enter:On")) {
        throw new Error(`Expected 'enter:On' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After toggle to On: ${JSON.stringify(log)}`);

    // Toggle back to Off - should exit On, enter Off
    s.toggle();
    log = s.get_log();
    const enterOffCount = log.filter(x => x === "enter:Off").length;
    if (enterOffCount !== 2) {
        throw new Error(`Expected 2 'enter:Off' entries, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("exit:On")) {
        throw new Error(`Expected 'exit:On' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After toggle to Off: ${JSON.stringify(log)}`);

    console.log("PASS: Enter/Exit handlers work correctly");
}

main();
