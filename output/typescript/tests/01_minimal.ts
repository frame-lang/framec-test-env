class MinimalFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class MinimalFrameContext {
    public event: MinimalFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: MinimalFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class MinimalCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: MinimalCompartment | null;

    constructor(state: string, parent_compartment: MinimalCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): MinimalCompartment {
        const c = new MinimalCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class Minimal {
    private _state_stack: Array<any>;
    private __compartment: MinimalCompartment;
    private __next_compartment: MinimalCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new MinimalCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new MinimalFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: MinimalFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new MinimalFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new MinimalFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new MinimalFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: MinimalFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: MinimalCompartment) {
        this.__next_compartment = next_compartment;
    }

    public is_alive(): boolean {
        const __e = new MinimalFrameEvent("is_alive", null);
        const __ctx = new MinimalFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Start(__e: MinimalFrameEvent) {
        if (__e._message === "is_alive") {
            this._context_stack[this._context_stack.length - 1]._return = true;
            return;;
        }
    }
}


function main() {
    console.log("=== Test 01: Minimal System ===");
    const s = new Minimal();

    // Test that system instantiates and responds
    const result = s.is_alive();
    if (result !== true) {
        throw new Error(`Expected true, got ${result}`);
    }
    console.log(`is_alive() = ${result}`);

    console.log("PASS: Minimal system works correctly");
}

main();
