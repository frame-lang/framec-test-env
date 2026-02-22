class WithParamsFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class WithParamsCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: WithParamsCompartment | null;

    constructor(state: string, parent_compartment: WithParamsCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): WithParamsCompartment {
        const c = new WithParamsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class WithParams {
    private _state_stack: Array<any>;
    private __compartment: WithParamsCompartment;
    private __next_compartment: WithParamsCompartment | null;
    private _return_value: any;
    private total: number = 0;

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.total = 0;
        this.__compartment = new WithParamsCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new WithParamsFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: WithParamsFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new WithParamsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new WithParamsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new WithParamsFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: WithParamsFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: WithParamsCompartment) {
        this.__next_compartment = next_compartment;
    }

    public start(initial: number) {
        const __e = new WithParamsFrameEvent("start", {"0": initial});
        this.__kernel(__e);
    }

    public add(value: number) {
        const __e = new WithParamsFrameEvent("add", {"0": value});
        this.__kernel(__e);
    }

    public multiply(a: number, b: number): number {
        this._return_value = null;
        const __e = new WithParamsFrameEvent("multiply", {"0": a, "1": b});
        this.__kernel(__e);
        return this._return_value;
    }

    public get_total(): number {
        this._return_value = null;
        const __e = new WithParamsFrameEvent("get_total", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Idle(__e: WithParamsFrameEvent) {
        if (__e._message === "add") {
            const value = __e._parameters?.["0"];
            console.log("Cannot add in Idle state");
        } else if (__e._message === "get_total") {
            this._return_value = this.total;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "multiply") {
            const a = __e._parameters?.["0"];
            const b = __e._parameters?.["1"];
            this._return_value = 0;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "start") {
            const initial = __e._parameters?.["0"];
            this.total = initial;
            console.log(`Started with initial value: ${initial}`);
            const __compartment = new WithParamsCompartment("Running", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private _state_Running(__e: WithParamsFrameEvent) {
        if (__e._message === "add") {
            const value = __e._parameters?.["0"];
            this.total += value;
            console.log(`Added ${value}, total is now ${this.total}`);
        } else if (__e._message === "get_total") {
            this._return_value = this.total;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "multiply") {
            const a = __e._parameters?.["0"];
            const b = __e._parameters?.["1"];
            const result = a * b;
            this.total += result;
            console.log(`Multiplied ${a} * ${b} = ${result}, total is now ${this.total}`);
            this._return_value = result;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "start") {
            const initial = __e._parameters?.["0"];
            console.log("Already running");
        }
    }
}


function main() {
    console.log("=== Test 07: Handler Parameters ===");
    const s = new WithParams();

    // Initial total should be 0
    let total = s.get_total();
    if (total !== 0) {
        throw new Error(`Expected initial total=0, got ${total}`);
    }

    // Start with initial value
    s.start(100);
    total = s.get_total();
    if (total !== 100) {
        throw new Error(`Expected total=100, got ${total}`);
    }
    console.log(`After start(100): total = ${total}`);

    // Add value
    s.add(25);
    total = s.get_total();
    if (total !== 125) {
        throw new Error(`Expected total=125, got ${total}`);
    }
    console.log(`After add(25): total = ${total}`);

    // Multiply with two params
    const result = s.multiply(3, 5);
    if (result !== 15) {
        throw new Error(`Expected multiply result=15, got ${result}`);
    }
    total = s.get_total();
    if (total !== 140) {
        throw new Error(`Expected total=140, got ${total}`);
    }
    console.log(`After multiply(3,5): result = ${result}, total = ${total}`);

    console.log("PASS: Handler parameters work correctly");
}

main();
