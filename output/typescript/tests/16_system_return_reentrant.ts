
// Tests that nested interface calls maintain separate return contexts


class SystemReturnReentrantTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class SystemReturnReentrantTestFrameContext {
    public event: SystemReturnReentrantTestFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: SystemReturnReentrantTestFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class SystemReturnReentrantTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: SystemReturnReentrantTestCompartment | null;

    constructor(state: string, parent_compartment: SystemReturnReentrantTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): SystemReturnReentrantTestCompartment {
        const c = new SystemReturnReentrantTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class SystemReturnReentrantTest {
    private _state_stack: Array<any>;
    private __compartment: SystemReturnReentrantTestCompartment;
    private __next_compartment: SystemReturnReentrantTestCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new SystemReturnReentrantTestCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new SystemReturnReentrantTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: SystemReturnReentrantTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new SystemReturnReentrantTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new SystemReturnReentrantTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new SystemReturnReentrantTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: SystemReturnReentrantTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: SystemReturnReentrantTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public outer_call(): string {
        const __e = new SystemReturnReentrantTestFrameEvent("outer_call", null);
        const __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public inner_call(): string {
        const __e = new SystemReturnReentrantTestFrameEvent("inner_call", null);
        const __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public nested_call(): string {
        const __e = new SystemReturnReentrantTestFrameEvent("nested_call", null);
        const __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_log(): string {
        const __e = new SystemReturnReentrantTestFrameEvent("get_log", null);
        const __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Start(__e: SystemReturnReentrantTestFrameEvent) {
        if (__e._message === "$>") {
            this.__compartment.state_vars["log"] = "";
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.__compartment.state_vars["log"];
            return;;
        } else if (__e._message === "inner_call") {
            this.__compartment.state_vars["log"] = this.__compartment.state_vars["log"] + "inner,";
            this._context_stack[this._context_stack.length - 1]._return = "inner_result";
            return;;
        } else if (__e._message === "nested_call") {
            this.__compartment.state_vars["log"] = this.__compartment.state_vars["log"] + "nested_start,";
            // Two levels of nesting
            const result1 = this.inner_call();
            const result2 = this.outer_call();
            this.__compartment.state_vars["log"] = this.__compartment.state_vars["log"] + "nested_end,";
            this._context_stack[this._context_stack.length - 1]._return = "nested:" + result1 + "+" + result2;
            return;;
        } else if (__e._message === "outer_call") {
            this.__compartment.state_vars["log"] = this.__compartment.state_vars["log"] + "outer_start,";
            // Call inner method - this creates nested return context
            const inner_result = this.inner_call();
            this.__compartment.state_vars["log"] = this.__compartment.state_vars["log"] + "outer_after_inner,";
            // Our return should be independent of inner's return
            this._context_stack[this._context_stack.length - 1]._return = "outer_result:" + inner_result;
            return;;
        }
    }
}


function main() {
    console.log("=== Test 16: System Return Reentrant (Nested Calls) ===");

    // Test 1: Simple inner call
    const s1 = new SystemReturnReentrantTest();
    const result1 = s1.inner_call();
    if (result1 !== "inner_result") {
        throw new Error(`Expected 'inner_result', got '${result1}'`);
    }
    console.log(`1. inner_call() = '${result1}'`);

    // Test 2: Outer calls inner - return contexts should be separate
    const s2 = new SystemReturnReentrantTest();
    const result2 = s2.outer_call();
    if (result2 !== "outer_result:inner_result") {
        throw new Error(`Expected 'outer_result:inner_result', got '${result2}'`);
    }
    const log2 = s2.get_log();
    if (!log2.includes("outer_start")) {
        throw new Error(`Missing outer_start in log: ${log2}`);
    }
    if (!log2.includes("inner")) {
        throw new Error(`Missing inner in log: ${log2}`);
    }
    if (!log2.includes("outer_after_inner")) {
        throw new Error(`Missing outer_after_inner in log: ${log2}`);
    }
    console.log(`2. outer_call() = '${result2}'`);
    console.log(`   Log: '${log2}'`);

    // Test 3: Deeply nested calls
    const s3 = new SystemReturnReentrantTest();
    const result3 = s3.nested_call();
    const expected = "nested:inner_result+outer_result:inner_result";
    if (result3 !== expected) {
        throw new Error(`Expected '${expected}', got '${result3}'`);
    }
    console.log(`3. nested_call() = '${result3}'`);

    console.log("PASS: System return reentrant (nested calls) works correctly");
}

main();
