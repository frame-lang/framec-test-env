class DomainVarsFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class DomainVarsFrameContext {
    public event: DomainVarsFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: DomainVarsFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class DomainVarsCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: DomainVarsCompartment | null;

    constructor(state: string, parent_compartment: DomainVarsCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): DomainVarsCompartment {
        const c = new DomainVarsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class DomainVars {
    private _state_stack: Array<any>;
    private __compartment: DomainVarsCompartment;
    private __next_compartment: DomainVarsCompartment | null;
    private _context_stack: Array<any>;
    private count: number = 0;
    private name: string = "counter";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.count = 0;
        this.name = "counter";
        this.__compartment = new DomainVarsCompartment("Counting");
        this.__next_compartment = null;
        const __frame_event = new DomainVarsFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: DomainVarsFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new DomainVarsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new DomainVarsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new DomainVarsFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: DomainVarsFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: DomainVarsCompartment) {
        this.__next_compartment = next_compartment;
    }

    public increment() {
        const __e = new DomainVarsFrameEvent("increment", null);
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public decrement() {
        const __e = new DomainVarsFrameEvent("decrement", null);
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_count(): number {
        const __e = new DomainVarsFrameEvent("get_count", null);
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public set_count(value: number) {
        const __e = new DomainVarsFrameEvent("set_count", {"value": value});
        const __ctx = new DomainVarsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    private _state_Counting(__e: DomainVarsFrameEvent) {
        if (__e._message === "decrement") {
            this.count -= 1;
            console.log(`${this.name}: decremented to ${this.count}`);
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = this.count;
            return;;
        } else if (__e._message === "increment") {
            this.count += 1;
            console.log(`${this.name}: incremented to ${this.count}`);
        } else if (__e._message === "set_count") {
            const value = __e._parameters?.["value"];
            this.count = value;
            console.log(`${this.name}: set to ${this.count}`);
        }
    }
}


function main() {
    console.log("=== Test 06: Domain Variables ===");
    const s = new DomainVars();

    // Initial value should be 0
    let count = s.get_count();
    if (count !== 0) {
        throw new Error(`Expected initial count=0, got ${count}`);
    }
    console.log(`Initial count: ${count}`);

    // Increment
    s.increment();
    count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }

    s.increment();
    count = s.get_count();
    if (count !== 2) {
        throw new Error(`Expected count=2, got ${count}`);
    }

    // Decrement
    s.decrement();
    count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }

    // Set directly
    s.set_count(100);
    count = s.get_count();
    if (count !== 100) {
        throw new Error(`Expected count=100, got ${count}`);
    }

    console.log(`Final count: ${count}`);
    console.log("PASS: Domain variables work correctly");
}

main();
