class ForwardEnterFirstFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class ForwardEnterFirstFrameContext {
    public event: ForwardEnterFirstFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: ForwardEnterFirstFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class ForwardEnterFirstCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: ForwardEnterFirstCompartment | null;

    constructor(state: string, parent_compartment: ForwardEnterFirstCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): ForwardEnterFirstCompartment {
        const c = new ForwardEnterFirstCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class ForwardEnterFirst {
    private _state_stack: Array<any>;
    private __compartment: ForwardEnterFirstCompartment;
    private __next_compartment: ForwardEnterFirstCompartment | null;
    private _context_stack: Array<any>;
    private log: string[] =     [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.log =         [];
        this.__compartment = new ForwardEnterFirstCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new ForwardEnterFirstFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: ForwardEnterFirstFrameEvent) {
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

    private __router(__e: ForwardEnterFirstFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: ForwardEnterFirstCompartment) {
        this.__next_compartment = next_compartment;
    }

    public process() {
        const __e = new ForwardEnterFirstFrameEvent("process", null);
        const __ctx = new ForwardEnterFirstFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_counter(): number {
        const __e = new ForwardEnterFirstFrameEvent("get_counter", null);
        const __ctx = new ForwardEnterFirstFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_log(): string[] {
        const __e = new ForwardEnterFirstFrameEvent("get_log", null);
        const __ctx = new ForwardEnterFirstFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Working(__e: ForwardEnterFirstFrameEvent) {
        if (__e._message === "$>") {
            if (!("counter" in this.__compartment.state_vars)) {
                this.__compartment.state_vars["counter"] = 100;
            }
            this.log.push("Working:enter")
        } else if (__e._message === "get_counter") {
            this._context_stack[this._context_stack.length - 1]._return = this.__compartment.state_vars["counter"];
            return;
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "process") {
            this.log.push("Working:process:counter=" + this.__compartment.state_vars["counter"].toString())
            this.__compartment.state_vars["counter"] = this.__compartment.state_vars["counter"] + 1;
        }
    }

    private _state_Idle(__e: ForwardEnterFirstFrameEvent) {
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


function main(): void {
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
