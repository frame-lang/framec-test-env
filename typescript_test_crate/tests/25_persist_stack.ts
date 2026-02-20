class PersistStackFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;
    public _return: any;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
        this._return = null;
    }
}


class PersistStackCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: PersistStackCompartment | null;

    constructor(state: string, parent_compartment: PersistStackCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): PersistStackCompartment {
        const c = new PersistStackCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class PersistStack {
    private _state_stack: Array<any>;
    private __compartment: PersistStackCompartment;
    private __next_compartment: PersistStackCompartment | null;
    private _return_value: any;
    private depth: number = 0;

    constructor() {
        this._state_stack = [];
        this._return_value = null;
        this.depth = 0;
        this.__compartment = new PersistStackCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new PersistStackFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: PersistStackFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new PersistStackFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new PersistStackFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new PersistStackFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: PersistStackFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: PersistStackCompartment) {
        this.__next_compartment = next_compartment;
    }

    public push_and_go() {
        const __e = new PersistStackFrameEvent("push_and_go", null);
        this.__kernel(__e);
    }

    public pop_back() {
        const __e = new PersistStackFrameEvent("pop_back", null);
        this.__kernel(__e);
    }

    public get_state(): string {
        this._return_value = null;
        const __e = new PersistStackFrameEvent("get_state", null);
        this.__kernel(__e);
        return this._return_value;
    }

    public get_depth(): number {
        this._return_value = null;
        const __e = new PersistStackFrameEvent("get_depth", null);
        this.__kernel(__e);
        return this._return_value;
    }

    private _state_Middle(__e: PersistStackFrameEvent) {
        if (__e._message === "get_depth") {
            this._return_value = this.depth;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "get_state") {
            this._return_value = "middle";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "pop_back") {
            this.depth = this.depth - 1;
            this.__compartment = this._state_stack.pop()!;
            return;
        } else if (__e._message === "push_and_go") {
            this.depth = this.depth + 1;
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new PersistStackCompartment("End");
            this.__transition(__compartment);
        }
    }

    private _state_End(__e: PersistStackFrameEvent) {
        if (__e._message === "get_depth") {
            this._return_value = this.depth;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "get_state") {
            this._return_value = "end";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "pop_back") {
            this.depth = this.depth - 1;
            this.__compartment = this._state_stack.pop()!;
            return;
        } else if (__e._message === "push_and_go") {
            // can't go further
        }
    }

    private _state_Start(__e: PersistStackFrameEvent) {
        if (__e._message === "get_depth") {
            this._return_value = this.depth;
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "get_state") {
            this._return_value = "start";
            __e._return = this._return_value;
            return;;
        } else if (__e._message === "pop_back") {
            // nothing to pop
        } else if (__e._message === "push_and_go") {
            this.depth = this.depth + 1;
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new PersistStackCompartment("Middle");
            this.__transition(__compartment);
        }
    }

    public saveState(): any {
        return {
            _compartment: this.__compartment.copy(),
            _state_stack: this._state_stack.map(c => c.copy()),
            depth: this.depth,
        };
    }

    public static restoreState(data: any): PersistStack {
        const instance = Object.create(PersistStack.prototype);
        instance.__compartment = new PersistStackCompartment(data._compartment.state);
        instance.__compartment.state_args = {...(data._compartment.state_args || {})};
        instance.__compartment.state_vars = {...(data._compartment.state_vars || {})};
        instance.__compartment.enter_args = {...(data._compartment.enter_args || {})};
        instance.__compartment.exit_args = {...(data._compartment.exit_args || {})};
        instance.__compartment.forward_event = data._compartment.forward_event;
        instance.__next_compartment = null;
        instance._state_stack = (data._state_stack || []).map((c: any) => {
            const comp = new PersistStackCompartment(c.state);
            comp.state_args = {...(c.state_args || {})};
            comp.state_vars = {...(c.state_vars || {})};
            comp.enter_args = {...(c.enter_args || {})};
            comp.exit_args = {...(c.exit_args || {})};
            comp.forward_event = c.forward_event;
            return comp;
        });
        instance._return_value = null;
        instance.depth = data.depth;
        return instance;
    }
}


function main(): void {
    console.log("=== Test 25: Persist Stack (TypeScript) ===");

    // Test 1: Build up a stack
    const s1 = new PersistStack();
    console.assert(s1.get_state() === "start", `Expected start, got ${s1.get_state()}`);

    s1.push_and_go();  // Start -> Middle (push Start)
    console.assert(s1.get_state() === "middle", `Expected middle, got ${s1.get_state()}`);
    console.assert(s1.get_depth() === 1, `Expected depth 1, got ${s1.get_depth()}`);

    s1.push_and_go();  // Middle -> End (push Middle)
    console.assert(s1.get_state() === "end", `Expected end, got ${s1.get_state()}`);
    console.assert(s1.get_depth() === 2, `Expected depth 2, got ${s1.get_depth()}`);

    console.log(`1. Built stack: state=${s1.get_state()}, depth=${s1.get_depth()}`);

    // Test 2: Save state (should include stack)
    const data = s1.saveState();
    console.log(`2. Saved data: ${JSON.stringify(data)}`);
    console.assert(data._state === 'End', `Expected End state`);
    console.assert(data._state_stack !== undefined, "Expected _state_stack in saved data");
    console.assert(data._state_stack.length === 2, `Expected 2 items in stack, got ${data._state_stack.length}`);

    // Test 3: Restore and verify stack works
    const s2 = PersistStack.restoreState(data);
    console.assert(s2.get_state() === "end", `Restored: expected end, got ${s2.get_state()}`);
    console.assert(s2.get_depth() === 2, `Restored: expected depth 2, got ${s2.get_depth()}`);
    console.log(`3. Restored: state=${s2.get_state()}, depth=${s2.get_depth()}`);

    // Test 4: Pop should work after restore
    s2.pop_back();  // End -> Middle (pop)
    console.assert(s2.get_state() === "middle", `After pop: expected middle, got ${s2.get_state()}`);
    console.assert(s2.get_depth() === 1, `After pop: expected depth 1, got ${s2.get_depth()}`);
    console.log(`4. After pop: state=${s2.get_state()}, depth=${s2.get_depth()}`);

    // Test 5: Pop again
    s2.pop_back();  // Middle -> Start (pop)
    console.assert(s2.get_state() === "start", `After 2nd pop: expected start, got ${s2.get_state()}`);
    console.assert(s2.get_depth() === 0, `After 2nd pop: expected depth 0, got ${s2.get_depth()}`);
    console.log(`5. After 2nd pop: state=${s2.get_state()}, depth=${s2.get_depth()}`);

    console.log("PASS: Persist stack works correctly");
}

main();
