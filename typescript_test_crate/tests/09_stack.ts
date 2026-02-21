class StackOpsFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class StackOpsCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: StackOpsCompartment | null;

    constructor(state: string, parent_compartment: StackOpsCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): StackOpsCompartment {
        const c = new StackOpsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class StackOps {
    private _state_stack: Array<any>;
    private __compartment: StackOpsCompartment;
    private __next_compartment: StackOpsCompartment | null;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.__compartment = new StackOpsCompartment("Main");
        this.__next_compartment = null;
        const __frame_event = new StackOpsFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: StackOpsFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new StackOpsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new StackOpsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new StackOpsFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: StackOpsFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: StackOpsCompartment) {
        this.__next_compartment = next_compartment;
    }

    public push_and_go() {
        const __e = new StackOpsFrameEvent("push_and_go", null);
        this.__kernel(__e);
    }

    public pop_back() {
        const __e = new StackOpsFrameEvent("pop_back", null);
        this.__kernel(__e);
    }

    public do_work(): string {
        this._return_value = null;
        const __e = new StackOpsFrameEvent("do_work", null);
        this.__kernel(__e);
        return this._return_value;
    }

    public get_state(): string {
        this._return_value = null;
        const __e = new StackOpsFrameEvent("get_state", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Sub(__e: StackOpsFrameEvent) {
        if (__e._message === "do_work") {
            this._return_value = "Working in Sub";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "get_state") {
            this._return_value = "Sub";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "pop_back") {
            console.log("Popping back to previous state");
            this.__compartment = this._state_stack.pop()!;
            return;
        } else if (__e._message === "push_and_go") {
            console.log("Already in Sub");
        }
    }

    private _state_Main(__e: StackOpsFrameEvent) {
        if (__e._message === "do_work") {
            this._return_value = "Working in Main";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "get_state") {
            this._return_value = "Main";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "pop_back") {
            console.log("Cannot pop - nothing on stack in Main");
        } else if (__e._message === "push_and_go") {
            console.log("Pushing Main to stack, going to Sub");
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new StackOpsCompartment("Sub", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }
}


function main() {
    console.log("=== Test 09: Stack Push/Pop ===");
    const s = new StackOps();

    // Initial state should be Main
    let state = s.get_state();
    if (state !== "Main") {
        throw new Error(`Expected 'Main', got '${state}'`);
    }
    console.log(`Initial state: ${state}`);

    // Do work in Main
    let work = s.do_work();
    if (work !== "Working in Main") {
        throw new Error(`Expected 'Working in Main', got '${work}'`);
    }
    console.log(`do_work(): ${work}`);

    // Push and go to Sub
    s.push_and_go();
    state = s.get_state();
    if (state !== "Sub") {
        throw new Error(`Expected 'Sub', got '${state}'`);
    }
    console.log(`After push_and_go(): ${state}`);

    // Do work in Sub
    work = s.do_work();
    if (work !== "Working in Sub") {
        throw new Error(`Expected 'Working in Sub', got '${work}'`);
    }
    console.log(`do_work(): ${work}`);

    // Pop back to Main
    s.pop_back();
    state = s.get_state();
    if (state !== "Main") {
        throw new Error(`Expected 'Main' after pop, got '${state}'`);
    }
    console.log(`After pop_back(): ${state}`);

    console.log("PASS: Stack push/pop works correctly");
}

main();
