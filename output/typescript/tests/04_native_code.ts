
function helper_function(x: number): number {
    // Native helper function defined before system
    return x * 2;
}


class NativeCodeFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class NativeCodeFrameContext {
    public event: NativeCodeFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: NativeCodeFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class NativeCodeCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: NativeCodeCompartment | null;

    constructor(state: string, parent_compartment: NativeCodeCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): NativeCodeCompartment {
        const c = new NativeCodeCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class NativeCode {
    private _state_stack: Array<any>;
    private __compartment: NativeCodeCompartment;
    private __next_compartment: NativeCodeCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new NativeCodeCompartment("Active");
        this.__next_compartment = null;
        const __frame_event = new NativeCodeFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: NativeCodeFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new NativeCodeFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new NativeCodeFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new NativeCodeFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: NativeCodeFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: NativeCodeCompartment) {
        this.__next_compartment = next_compartment;
    }

    public compute(value: number): number {
        const __e = new NativeCodeFrameEvent("compute", {"value": value});
        const __ctx = new NativeCodeFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public use_math(): number {
        const __e = new NativeCodeFrameEvent("use_math", null);
        const __ctx = new NativeCodeFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Active(__e: NativeCodeFrameEvent) {
        if (__e._message === "compute") {
            const value = __e._parameters?.["value"];
            // Native code with local variables
            const temp = value + 10;
            const result = helper_function(temp);
            console.log(`Computed: ${value} -> ${result}`);
            this._context_stack[this._context_stack.length - 1]._return = result;
            return;;
        } else if (__e._message === "use_math") {
            // Using Math module
            const result = Math.sqrt(16) + Math.PI;
            console.log(`Math result: ${result}`);
            this._context_stack[this._context_stack.length - 1]._return = result;
            return;;
        }
    }
}


function main() {
    console.log("=== Test 04: Native Code Preservation ===");
    const s = new NativeCode();

    // Test native code in handler with helper function
    const result = s.compute(5);
    const expected = (5 + 10) * 2;  // 30
    if (result !== expected) {
        throw new Error(`Expected ${expected}, got ${result}`);
    }
    console.log(`compute(5) = ${result}`);

    // Test Math module usage
    const mathResult = s.use_math();
    const expectedMath = Math.sqrt(16) + Math.PI;
    if (Math.abs(mathResult - expectedMath) >= 0.001) {
        throw new Error(`Expected ~${expectedMath}, got ${mathResult}`);
    }
    console.log(`use_math() = ${mathResult}`);

    console.log("PASS: Native code preservation works correctly");
}

main();
