class WithParamsFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class WithParamsFrameContext {
    public event: WithParamsFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: WithParamsFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
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
    private _context_stack: Array<any>;
    private total: number = 0;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
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
        const __e = new WithParamsFrameEvent("start", {"initial": initial});
        const __ctx = new WithParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public add(value: number) {
        const __e = new WithParamsFrameEvent("add", {"value": value});
        const __ctx = new WithParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public multiply(a: number, b: number): number {
        const __e = new WithParamsFrameEvent("multiply", {"a": a, "b": b});
        const __ctx = new WithParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_total(): number {
        const __e = new WithParamsFrameEvent("get_total", null);
        const __ctx = new WithParamsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Running(__e: WithParamsFrameEvent) {
        if (__e._message === "add") {
            const value = __e._parameters?.["value"];
            this.total += value;
            console.log(`Added ${value}, total is now ${this.total}`);
        } else if (__e._message === "get_total") {
            this._context_stack[this._context_stack.length - 1]._return = this.total;
            return;;
        } else if (__e._message === "multiply") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            const result = a * b;
            this.total += result;
            console.log(`Multiplied ${a} * ${b} = ${result}, total is now ${this.total}`);
            this._context_stack[this._context_stack.length - 1]._return = result;
            return;;
        } else if (__e._message === "start") {
            const initial = __e._parameters?.["initial"];
            console.log("Already running");
        }
    }

    private _state_Idle(__e: WithParamsFrameEvent) {
        if (__e._message === "add") {
            const value = __e._parameters?.["value"];
            console.log("Cannot add in Idle state");
        } else if (__e._message === "get_total") {
            this._context_stack[this._context_stack.length - 1]._return = this.total;
            return;;
        } else if (__e._message === "multiply") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            this._context_stack[this._context_stack.length - 1]._return = 0;
            return;;
        } else if (__e._message === "start") {
            const initial = __e._parameters?.["initial"];
            this.total = initial;
            console.log(`Started with initial value: ${initial}`);
            const __compartment = new WithParamsCompartment("Running", this.__compartment.copy());
            this.__transition(__compartment);
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
