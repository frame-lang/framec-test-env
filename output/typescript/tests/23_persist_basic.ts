class PersistTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class PersistTestFrameContext {
    public event: PersistTestFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: PersistTestFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class PersistTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: PersistTestCompartment | null;

    constructor(state: string, parent_compartment: PersistTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): PersistTestCompartment {
        const c = new PersistTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class PersistTest {
    private _state_stack: Array<any>;
    private __compartment: PersistTestCompartment;
    private __next_compartment: PersistTestCompartment | null;
    private _context_stack: Array<any>;
    private value: number = 0;
    private name: string = "default";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.value = 0;
        this.name = "default";
        this.__compartment = new PersistTestCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new PersistTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: PersistTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new PersistTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new PersistTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new PersistTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: PersistTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: PersistTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public set_value(v: number) {
        const __e = new PersistTestFrameEvent("set_value", {"v": v});
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_value(): number {
        const __e = new PersistTestFrameEvent("get_value", null);
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public go_active() {
        const __e = new PersistTestFrameEvent("go_active", null);
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public go_idle() {
        const __e = new PersistTestFrameEvent("go_idle", null);
        const __ctx = new PersistTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    private _state_Idle(__e: PersistTestFrameEvent) {
        if (__e._message === "get_value") {
            this._context_stack[this._context_stack.length - 1]._return = this.value;
            return;;
        } else if (__e._message === "go_active") {
            const __compartment = new PersistTestCompartment("Active", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "go_idle") {
            // Already idle
        } else if (__e._message === "set_value") {
            const v = __e._parameters?.["v"];
            this.value = v;
        }
    }

    private _state_Active(__e: PersistTestFrameEvent) {
        if (__e._message === "get_value") {
            this._context_stack[this._context_stack.length - 1]._return = this.value;
            return;;
        } else if (__e._message === "go_active") {
            // Already active
        } else if (__e._message === "go_idle") {
            const __compartment = new PersistTestCompartment("Idle", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "set_value") {
            const v = __e._parameters?.["v"];
            this.value = v * 2;
        }
    }

    public saveState(): any {
        return {
            _compartment: this.__compartment.copy(),
            _state_stack: this._state_stack.map(c => c.copy()),
            value: this.value,
            name: this.name,
        };
    }

    public static restoreState(data: any): PersistTest {
        const instance = Object.create(PersistTest.prototype);
        instance.__compartment = new PersistTestCompartment(data._compartment.state);
        instance.__compartment.state_args = {...(data._compartment.state_args || {})};
        instance.__compartment.state_vars = {...(data._compartment.state_vars || {})};
        instance.__compartment.enter_args = {...(data._compartment.enter_args || {})};
        instance.__compartment.exit_args = {...(data._compartment.exit_args || {})};
        instance.__compartment.forward_event = data._compartment.forward_event;
        instance.__next_compartment = null;
        instance._state_stack = (data._state_stack || []).map((c: any) => {
            const comp = new PersistTestCompartment(c.state);
            comp.state_args = {...(c.state_args || {})};
            comp.state_vars = {...(c.state_vars || {})};
            comp.enter_args = {...(c.enter_args || {})};
            comp.exit_args = {...(c.exit_args || {})};
            comp.forward_event = c.forward_event;
            return comp;
        });
        instance._return_value = null;
        instance.value = data.value;
        instance.name = data.name;
        return instance;
    }
}


function main(): void {
    console.log("=== Test 23: Persist Basic (TypeScript) ===");

    // Test 1: Create and modify system
    const s1 = new PersistTest();
    s1.set_value(10);
    s1.go_active();
    s1.set_value(5);  // Should be doubled to 10 in Active state

    // Test 2: Save state
    const data = s1.saveState();
    if (data._compartment.state !== 'Active') {
        throw new Error(`Expected 'Active', got ${data._compartment.state}`);
    }
    if (data.value !== 10) {
        throw new Error(`Expected 10, got ${data.value}`);
    }
    console.log(`1. Saved state: ${JSON.stringify(data)}`);

    // Test 3: Restore state
    const s2 = PersistTest.restoreState(data);
    if (s2.get_value() !== 10) {
        throw new Error(`Expected 10, got ${s2.get_value()}`);
    }
    console.log(`2. Restored value: ${s2.get_value()}`);

    // Test 4: Verify state is preserved (Active state doubles)
    s2.set_value(3);  // Should be doubled to 6 in Active state
    if (s2.get_value() !== 6) {
        throw new Error(`Expected 6, got ${s2.get_value()}`);
    }
    console.log(`3. After set_value(3) in Active: ${s2.get_value()}`);

    // Test 5: Verify transitions work after restore
    s2.go_idle();
    s2.set_value(4);  // Should NOT be doubled in Idle state
    if (s2.get_value() !== 4) {
        throw new Error(`Expected 4, got ${s2.get_value()}`);
    }
    console.log(`4. After go_idle, set_value(4): ${s2.get_value()}`);

    console.log("PASS: Persist basic works correctly");
}

main();
