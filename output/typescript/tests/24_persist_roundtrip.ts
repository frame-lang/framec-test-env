class PersistRoundtripFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class PersistRoundtripFrameContext {
    public event: PersistRoundtripFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: PersistRoundtripFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class PersistRoundtripCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: PersistRoundtripCompartment | null;

    constructor(state: string, parent_compartment: PersistRoundtripCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): PersistRoundtripCompartment {
        const c = new PersistRoundtripCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class PersistRoundtrip {
    private _state_stack: Array<any>;
    private __compartment: PersistRoundtripCompartment;
    private __next_compartment: PersistRoundtripCompartment | null;
    private _context_stack: Array<any>;
    private counter: number = 0;
    private history: string[] =     [];
    private mode: string = "normal";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.counter = 0;
        this.history =         [];
        this.mode = "normal";
        this.__compartment = new PersistRoundtripCompartment("Idle");
        this.__next_compartment = null;
        const __frame_event = new PersistRoundtripFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: PersistRoundtripFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new PersistRoundtripFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new PersistRoundtripFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new PersistRoundtripFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: PersistRoundtripFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: PersistRoundtripCompartment) {
        this.__next_compartment = next_compartment;
    }

    public go_active() {
        const __e = new PersistRoundtripFrameEvent("go_active", null);
        const __ctx = new PersistRoundtripFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public go_idle() {
        const __e = new PersistRoundtripFrameEvent("go_idle", null);
        const __ctx = new PersistRoundtripFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_state(): string {
        const __e = new PersistRoundtripFrameEvent("get_state", null);
        const __ctx = new PersistRoundtripFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public set_counter(n: number) {
        const __e = new PersistRoundtripFrameEvent("set_counter", {"n": n});
        const __ctx = new PersistRoundtripFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_counter(): number {
        const __e = new PersistRoundtripFrameEvent("get_counter", null);
        const __ctx = new PersistRoundtripFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public add_history(msg: string) {
        const __e = new PersistRoundtripFrameEvent("add_history", {"msg": msg});
        const __ctx = new PersistRoundtripFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    public get_history(): string[] {
        const __e = new PersistRoundtripFrameEvent("get_history", null);
        const __ctx = new PersistRoundtripFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_Idle(__e: PersistRoundtripFrameEvent) {
        if (__e._message === "add_history") {
            const msg = __e._parameters?.["msg"];
            this.history.push("idle:" + msg);
        } else if (__e._message === "get_counter") {
            this._context_stack[this._context_stack.length - 1]._return = this.counter;
            return;;
        } else if (__e._message === "get_history") {
            this._context_stack[this._context_stack.length - 1]._return = this.history;
            return;;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "idle";
            return;;
        } else if (__e._message === "go_active") {
            this.history.push("idle->active");
            const __compartment = new PersistRoundtripCompartment("Active", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "go_idle") {
            // already idle
        } else if (__e._message === "set_counter") {
            const n = __e._parameters?.["n"];
            this.counter = n;
        }
    }

    private _state_Active(__e: PersistRoundtripFrameEvent) {
        if (__e._message === "add_history") {
            const msg = __e._parameters?.["msg"];
            this.history.push("active:" + msg);
        } else if (__e._message === "get_counter") {
            this._context_stack[this._context_stack.length - 1]._return = this.counter;
            return;;
        } else if (__e._message === "get_history") {
            this._context_stack[this._context_stack.length - 1]._return = this.history;
            return;;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "active";
            return;;
        } else if (__e._message === "go_active") {
            // already active
        } else if (__e._message === "go_idle") {
            this.history.push("active->idle");
            const __compartment = new PersistRoundtripCompartment("Idle", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "set_counter") {
            const n = __e._parameters?.["n"];
            this.counter = n * 2;
        }
    }

    public saveState(): any {
        return {
            _compartment: this.__compartment.copy(),
            _state_stack: this._state_stack.map(c => c.copy()),
            counter: this.counter,
            history: this.history,
            mode: this.mode,
        };
    }

    public static restoreState(data: any): PersistRoundtrip {
        const instance = Object.create(PersistRoundtrip.prototype);
        instance.__compartment = new PersistRoundtripCompartment(data._compartment.state);
        instance.__compartment.state_args = {...(data._compartment.state_args || {})};
        instance.__compartment.state_vars = {...(data._compartment.state_vars || {})};
        instance.__compartment.enter_args = {...(data._compartment.enter_args || {})};
        instance.__compartment.exit_args = {...(data._compartment.exit_args || {})};
        instance.__compartment.forward_event = data._compartment.forward_event;
        instance.__next_compartment = null;
        instance._state_stack = (data._state_stack || []).map((c: any) => {
            const comp = new PersistRoundtripCompartment(c.state);
            comp.state_args = {...(c.state_args || {})};
            comp.state_vars = {...(c.state_vars || {})};
            comp.enter_args = {...(c.enter_args || {})};
            comp.exit_args = {...(c.exit_args || {})};
            comp.forward_event = c.forward_event;
            return comp;
        });
        instance._return_value = null;
        instance.counter = data.counter;
        instance.history = data.history;
        instance.mode = data.mode;
        return instance;
    }
}


function main(): void {
    console.log("=== Test 24: Persist Roundtrip (TypeScript) ===");

    // Test 1: Create system and build up state
    const s1 = new PersistRoundtrip();
    s1.set_counter(5);
    s1.add_history("start");
    s1.go_active();
    s1.set_counter(3);  // Should be 6 in Active (doubled)
    s1.add_history("work");

    if (s1.get_state() !== "active") {
        throw new Error(`Expected active, got ${s1.get_state()}`);
    }
    if (s1.get_counter() !== 6) {
        throw new Error(`Expected 6, got ${s1.get_counter()}`);
    }
    console.log(`1. State before save: state=${s1.get_state()}, counter=${s1.get_counter()}`);
    console.log(`   History: ${JSON.stringify(s1.get_history())}`);

    // Test 2: Save state
    const data = s1.saveState();
    console.log(`2. Saved data keys: ${Object.keys(data)}`);
    if (data._compartment.state !== 'Active') {
        throw new Error("Expected Active state in save data");
    }
    if (data.counter !== 6) {
        throw new Error("Expected counter=6 in save data");
    }

    // Test 3: Restore to new instance
    const s2 = PersistRoundtrip.restoreState(data);

    if (s2.get_state() !== "active") {
        throw new Error(`Expected active, got ${s2.get_state()}`);
    }
    if (s2.get_counter() !== 6) {
        throw new Error(`Expected 6, got ${s2.get_counter()}`);
    }
    console.log(`3. Restored state: state=${s2.get_state()}, counter=${s2.get_counter()}`);

    // Test 4: State machine continues to work after restore
    s2.set_counter(2);  // Should be 4 in Active (doubled)
    if (s2.get_counter() !== 4) {
        throw new Error(`Expected 4, got ${s2.get_counter()}`);
    }
    console.log(`4. Counter after set_counter(2): ${s2.get_counter()}`);

    // Test 5: Verify history was preserved
    if (JSON.stringify(s2.get_history()) !== JSON.stringify(s1.get_history())) {
        throw new Error(`History mismatch: ${JSON.stringify(s2.get_history())} vs ${JSON.stringify(s1.get_history())}`);
    }
    console.log(`5. History preserved: ${JSON.stringify(s2.get_history())}`);

    // Test 6: Transitions work after restore
    s2.go_idle();
    if (s2.get_state() !== "idle") {
        throw new Error("Expected idle after go_idle");
    }
    s2.set_counter(10);  // Not doubled in Idle
    if (s2.get_counter() !== 10) {
        throw new Error(`Expected 10, got ${s2.get_counter()}`);
    }
    console.log(`6. After go_idle: state=${s2.get_state()}, counter=${s2.get_counter()}`);

    console.log("PASS: Persist roundtrip works correctly");
}

main();
