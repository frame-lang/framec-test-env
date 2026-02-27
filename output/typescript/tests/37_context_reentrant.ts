
// Test: Context Stack Reentrancy
// Validates that nested interface calls maintain separate contexts


class ContextReentrantTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class ContextReentrantTestFrameContext {
    public event: ContextReentrantTestFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: ContextReentrantTestFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class ContextReentrantTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: ContextReentrantTestCompartment | null;

    constructor(state: string, parent_compartment: ContextReentrantTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): ContextReentrantTestCompartment {
        const c = new ContextReentrantTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class ContextReentrantTest {
    private _state_stack: Array<any>;
    private __compartment: ContextReentrantTestCompartment;
    private __next_compartment: ContextReentrantTestCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new ContextReentrantTestCompartment("Ready");
        this.__next_compartment = null;
        const __frame_event = new ContextReentrantTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: ContextReentrantTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new ContextReentrantTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ContextReentrantTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new ContextReentrantTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: ContextReentrantTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: ContextReentrantTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public outer(x: number): string {
        const __e = new ContextReentrantTestFrameEvent("outer", {"x": x});
        const __ctx = new ContextReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public inner(y: number): string {
        const __e = new ContextReentrantTestFrameEvent("inner", {"y": y});
        const __ctx = new ContextReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public deeply_nested(z: number): string {
        const __e = new ContextReentrantTestFrameEvent("deeply_nested", {"z": z});
        const __ctx = new ContextReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_both(a: number, b: number): string {
        const __e = new ContextReentrantTestFrameEvent("get_both", {"a": a, "b": b});
        const __ctx = new ContextReentrantTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Ready(__e: ContextReentrantTestFrameEvent) {
        if (__e._message === "deeply_nested") {
            const z = __e._parameters?.["z"];
            // 3 levels deep
            const outer_result = this.outer(this._context_stack[this._context_stack.length - 1].event._parameters["z"]);
            this._context_stack[this._context_stack.length - 1]._return = "deep:" + this._context_stack[this._context_stack.length - 1].event._parameters["z"] + "," + outer_result;;
        } else if (__e._message === "get_both") {
            const a = __e._parameters?.["a"];
            const b = __e._parameters?.["b"];
            // Test that we can access multiple params
            const result_a = this.inner(this._context_stack[this._context_stack.length - 1].event._parameters["a"]);
            const result_b = this.inner(this._context_stack[this._context_stack.length - 1].event._parameters["b"]);
            // After both inner calls, @@.a and @@.b should still be our params
            this._context_stack[this._context_stack.length - 1]._return = "a=" + this._context_stack[this._context_stack.length - 1].event._parameters["a"] + ",b=" + this._context_stack[this._context_stack.length - 1].event._parameters["b"] + ",results=" + result_a + "+" + result_b;;
        } else if (__e._message === "inner") {
            const y = __e._parameters?.["y"];
            // Inner has its own context
            // @@.y should be inner's param, not outer's
            this._context_stack[this._context_stack.length - 1]._return = String(this._context_stack[this._context_stack.length - 1].event._parameters["y"]);;
        } else if (__e._message === "outer") {
            const x = __e._parameters?.["x"];
            // Set our return before calling inner
            this._context_stack[this._context_stack.length - 1]._return = "outer_initial";;

            // Call inner - should NOT clobber our return
            const inner_result = this.inner(this._context_stack[this._context_stack.length - 1].event._parameters["x"] * 10);

            // Our return should still be accessible
            // Update it with combined result
            this._context_stack[this._context_stack.length - 1]._return = "outer:" + this._context_stack[this._context_stack.length - 1].event._parameters["x"] + ",inner:" + inner_result;;
        }
    }
}


function main(): void {
    console.log("=== Test 37: Context Reentrant ===");
    const s = new ContextReentrantTest();

    // Test 1: Simple nesting - outer calls inner
    let result = s.outer(5);
    let expected = "outer:5,inner:50";
    if (result !== expected) throw new Error(`Expected '${expected}', got '${result}'`);
    console.log(`1. outer(5) = '${result}'`);

    // Test 2: Inner alone
    result = s.inner(42);
    if (result !== "42") throw new Error(`Expected '42', got '${result}'`);
    console.log(`2. inner(42) = '${result}'`);

    // Test 3: Deep nesting (3 levels)
    result = s.deeply_nested(3);
    expected = "deep:3,outer:3,inner:30";
    if (result !== expected) throw new Error(`Expected '${expected}', got '${result}'`);
    console.log(`3. deeply_nested(3) = '${result}'`);

    // Test 4: Multiple inner calls, params preserved
    result = s.get_both(10, 20);
    expected = "a=10,b=20,results=10+20";
    if (result !== expected) throw new Error(`Expected '${expected}', got '${result}'`);
    console.log(`4. get_both(10, 20) = '${result}'`);

    console.log("PASS: Context reentrant works correctly");
}

main();
