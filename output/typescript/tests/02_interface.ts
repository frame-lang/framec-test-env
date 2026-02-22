class WithInterfaceFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class WithInterfaceCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: WithInterfaceCompartment | null;

    constructor(state: string, parent_compartment: WithInterfaceCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): WithInterfaceCompartment {
        const c = new WithInterfaceCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class WithInterface {
    private _state_stack: Array<any>;
    private __compartment: WithInterfaceCompartment;
    private __next_compartment: WithInterfaceCompartment | null;
    private _return_value: any;
    private call_count: number = 0;

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.call_count = 0;
        this.__compartment = new WithInterfaceCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new WithInterfaceFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: WithInterfaceFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new WithInterfaceFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new WithInterfaceFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new WithInterfaceFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: WithInterfaceFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: WithInterfaceCompartment) {
        this.__next_compartment = next_compartment;
    }

    public greet(name: string): string {
        this._return_value = null;
        const __e = new WithInterfaceFrameEvent("greet", {"0": name});
        this.__kernel(__e);
        return this._return_value;
    }

    public get_count(): number {
        this._return_value = null;
        const __e = new WithInterfaceFrameEvent("get_count", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Ready(__e: WithInterfaceFrameEvent) {
        if (__e._message === "get_count") {
            this._return_value = this.call_count;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "greet") {
            const name = __e._parameters?.["0"];
            this.call_count += 1;
            this._return_value = `Hello, ${name}!`;
            __e._return = this._return_value;
            return;;
        }
    }
}


function main() {
    console.log("=== Test 02: Interface Methods ===");
    const s = new WithInterface();

    // Test interface method with parameter and return
    const result = s.greet("World");
    if (result !== "Hello, World!") {
        throw new Error(`Expected 'Hello, World!', got '${result}'`);
    }
    console.log(`greet('World') = ${result}`);

    // Test domain variable access through interface
    let count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }
    console.log(`get_count() = ${count}`);

    // Call again to verify state
    s.greet("Frame");
    const count2 = s.get_count();
    if (count2 !== 2) {
        throw new Error(`Expected count=2, got ${count2}`);
    }
    console.log(`After second call: get_count() = ${count2}`);

    console.log("PASS: Interface methods work correctly");
}

main();
