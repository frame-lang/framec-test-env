class SystemReturnTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class SystemReturnTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: SystemReturnTestCompartment | null;

    constructor(state: string, parent_compartment: SystemReturnTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): SystemReturnTestCompartment {
        const c = new SystemReturnTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class SystemReturnTest {
    private _state_stack: Array<any>;
    private __compartment: SystemReturnTestCompartment;
    private __next_compartment: SystemReturnTestCompartment | null;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.__compartment = new SystemReturnTestCompartment("Calculator");
        this.__next_compartment = null;
        const __frame_event = new SystemReturnTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: SystemReturnTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new SystemReturnTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new SystemReturnTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new SystemReturnTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: SystemReturnTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: SystemReturnTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public add(a: number, b: number): number {
        this._return_value = null;
        const __e = new SystemReturnTestFrameEvent("add", {"0": a, "1": b});
        this.__kernel(__e);
        return this._return_value;
    }

    public multiply(a: number, b: number): number {
        this._return_value = null;
        const __e = new SystemReturnTestFrameEvent("multiply", {"0": a, "1": b});
        this.__kernel(__e);
        return this._return_value;
    }

    public greet(name: string): string {
        this._return_value = null;
        const __e = new SystemReturnTestFrameEvent("greet", {"0": name});
        this.__kernel(__e);
        return this._return_value;
    }

    public get_value(): number {
        this._return_value = null;
        const __e = new SystemReturnTestFrameEvent("get_value", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Calculator(__e: SystemReturnTestFrameEvent) {
        if (__e._message === "$>") {
            this.__compartment.state_vars["value"] = 0;
        } else if (__e._message === "add") {
            const a = __e._parameters?.["0"];
            const b = __e._parameters?.["1"];
            this._return_value = a + b;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "get_value") {
            this.__compartment.state_vars["value"] = 42;
            this._return_value = this.__compartment.state_vars["value"];
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "greet") {
            const name = __e._parameters?.["0"];
            this._return_value = "Hello, " + name + "!";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "multiply") {
            const a = __e._parameters?.["0"];
            const b = __e._parameters?.["1"];
            this._return_value = a * b;;
        }
    }
}


function main() {
    console.log("=== Test 13: System Return ===");
    const calc = new SystemReturnTest();

    // Test return sugar
    let result = calc.add(3, 5);
    if (result !== 8) {
        throw new Error(`Expected 8, got ${result}`);
    }
    console.log(`add(3, 5) = ${result}`);

    // Test system.return = expr
    result = calc.multiply(4, 7);
    if (result !== 28) {
        throw new Error(`Expected 28, got ${result}`);
    }
    console.log(`multiply(4, 7) = ${result}`);

    // Test string return
    const greeting = calc.greet("World");
    if (greeting !== "Hello, World!") {
        throw new Error(`Expected 'Hello, World!', got '${greeting}'`);
    }
    console.log(`greet('World') = ${greeting}`);

    // Test return with state variable
    const value = calc.get_value();
    if (value !== 42) {
        throw new Error(`Expected 42, got ${value}`);
    }
    console.log(`get_value() = ${value}`);

    console.log("PASS: System return works correctly");
}

main();
