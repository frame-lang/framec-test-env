class WithTransitionFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class WithTransitionFrameContext {
    public event: WithTransitionFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: WithTransitionFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class WithTransitionCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: WithTransitionCompartment | null;

    constructor(state: string, parent_compartment: WithTransitionCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): WithTransitionCompartment {
        const c = new WithTransitionCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class WithTransition {
    private _state_stack: Array<any>;
    private __compartment: WithTransitionCompartment;
    private __next_compartment: WithTransitionCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new WithTransitionCompartment("First");
        this.__next_compartment = null;
        const __frame_event = new WithTransitionFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: WithTransitionFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new WithTransitionFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new WithTransitionFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new WithTransitionFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: WithTransitionFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: WithTransitionCompartment) {
        this.__next_compartment = next_compartment;
    }

    public next() {
        const __e = new WithTransitionFrameEvent("next", null);
        const __ctx = new WithTransitionFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_state(): string {
        const __e = new WithTransitionFrameEvent("get_state", null);
        const __ctx = new WithTransitionFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_First(__e: WithTransitionFrameEvent) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "First";
            return;;
        } else if (__e._message === "next") {
            console.log("Transitioning: First -> Second");
            const __compartment = new WithTransitionCompartment("Second", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private _state_Second(__e: WithTransitionFrameEvent) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Second";
            return;;
        } else if (__e._message === "next") {
            console.log("Transitioning: Second -> First");
            const __compartment = new WithTransitionCompartment("First", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }
}


function main() {
    console.log("=== Test 03: State Transitions ===");
    const s = new WithTransition();

    // Initial state should be First
    let state = s.get_state();
    if (state !== "First") {
        throw new Error(`Expected 'First', got '${state}'`);
    }
    console.log(`Initial state: ${state}`);

    // Transition to Second
    s.next();
    state = s.get_state();
    if (state !== "Second") {
        throw new Error(`Expected 'Second', got '${state}'`);
    }
    console.log(`After first next(): ${state}`);

    // Transition back to First
    s.next();
    state = s.get_state();
    if (state !== "First") {
        throw new Error(`Expected 'First', got '${state}'`);
    }
    console.log(`After second next(): ${state}`);

    console.log("PASS: State transitions work correctly");
}

main();
