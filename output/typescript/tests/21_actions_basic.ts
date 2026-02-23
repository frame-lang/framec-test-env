class ActionsTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class ActionsTestFrameContext {
    public event: ActionsTestFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: ActionsTestFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class ActionsTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: ActionsTestCompartment | null;

    constructor(state: string, parent_compartment: ActionsTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): ActionsTestCompartment {
        const c = new ActionsTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class ActionsTest {
    private _state_stack: Array<any>;
    private __compartment: ActionsTestCompartment;
    private __next_compartment: ActionsTestCompartment | null;
    private _context_stack: Array<any>;
    private log: string = "";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.log = "";
        this.__compartment = new ActionsTestCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new ActionsTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: ActionsTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new ActionsTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ActionsTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new ActionsTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: ActionsTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: ActionsTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public process(value: number): number {
        const __e = new ActionsTestFrameEvent("process", {"value": value});
        const __ctx = new ActionsTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_log(): string {
        const __e = new ActionsTestFrameEvent("get_log", null);
        const __ctx = new ActionsTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Ready(__e: ActionsTestFrameEvent) {
        if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;;
        } else if (__e._message === "process") {
            const value = __e._parameters?.["value"];
            this.__log_event("start");
            this.__validate_positive(value);
            this.__log_event("valid");
            const result = value * 2;
            this.__log_event("done");
            this._context_stack[this._context_stack.length - 1]._return = result;
            return;;
        }
    }

    private __log_event(msg: string) {
                    this.log = this.log + msg + ";";
    }

    private __validate_positive(n: number) {
                    if (n < 0) {
                        throw new Error(`Value must be positive: ${n}`);
                    }
    }
}


function main(): void {
    console.log("=== Test 21: Actions Basic (TypeScript) ===");
    const s = new ActionsTest();

    // Test 1: Actions are called correctly
    const result = s.process(5);
    if (result !== 10) {
        throw new Error(`Expected 10, got ${result}`);
    }
    console.log(`1. process(5) = ${result}`);

    // Test 2: Log shows action calls
    const log = s.get_log();
    if (!log.includes("start")) {
        throw new Error(`Missing 'start' in log: ${log}`);
    }
    if (!log.includes("valid")) {
        throw new Error(`Missing 'valid' in log: ${log}`);
    }
    if (!log.includes("done")) {
        throw new Error(`Missing 'done' in log: ${log}`);
    }
    console.log(`2. Log: ${log}`);

    // Test 3: Action with validation
    try {
        s.process(-1);
        throw new Error("Should have thrown Error");
    } catch (e) {
        if (e instanceof Error && e.message.includes("positive")) {
            console.log(`3. Validation caught: ${e.message}`);
        } else {
            throw e;
        }
    }

    console.log("PASS: Actions basic works correctly");
}

main();
