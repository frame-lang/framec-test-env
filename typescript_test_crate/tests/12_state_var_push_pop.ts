class StateVarPushPop {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this._state = "Counter";
        this._enter();
    }

    private _transition(target_state: string, exit_args: any = null, enter_args: any = null) {
        if (exit_args) {
            this._exit(...exit_args);
        } else {
            this._exit();
        }
        this._state = target_state;
        if (enter_args) {
            this._enter(...enter_args);
        } else {
            this._enter();
        }
    }

    private _change_state(target_state: string) {
        this._state = target_state;
    }

    private _dispatch_event(event: string, ...args: any[]) {
        const handler_name = `_s_${this._state}_${event}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            return handler.apply(this, args);
        }
    }

    private _enter(...args: any[]) {
        if (this._state === "Counter") {
            this._state_context["count"] = 0;
        } else if (this._state === "Other") {
            this._state_context["other_count"] = 100;
        }
    }

    private _exit(...args: any[]) {
        // No exit handlers
    }

    public increment(): number {
        this._return_value = null
        this._dispatch_event("increment")
        return this._return_value
    }

    public get_count(): number {
        this._return_value = null
        this._dispatch_event("get_count")
        return this._return_value
    }

    public save_and_go() {
        this._dispatch_event("save_and_go");
    }

    public restore() {
        this._dispatch_event("restore");
    }

    private _s_Counter_get_count() {
        this._return_value = this._state_context["count"];
        return this._return_value;;
    }

    private _s_Counter_increment() {
        this._state_context["count"] = this._state_context["count"] + 1;
        this._return_value = this._state_context["count"];
        return this._return_value;;
    }

    private _s_Counter_save_and_go() {
        this._state_stack.push({state: this._state, context: {...this._state_context}});
        this._transition("Other", null, null);
    }

    private _s_Other_increment() {
        this._state_context["other_count"] = this._state_context["other_count"] + 1;
        this._return_value = this._state_context["other_count"];
        return this._return_value;;
    }

    private _s_Other_get_count() {
        this._return_value = this._state_context["other_count"];
        return this._return_value;;
    }

    private _s_Other_restore() {
        const __saved = this._state_stack.pop()!;
        this._exit();
        this._state = __saved.state;
        this._state_context = __saved.context;
        return;
    }
}


function main() {
    console.log("=== Test 12: State Variable Push/Pop ===");
    const s = new StateVarPushPop();

    // Increment counter to 3
    s.increment();
    s.increment();
    s.increment();
    let count = s.get_count();
    if (count !== 3) {
        throw new Error(`Expected 3, got ${count}`);
    }
    console.log(`Counter before push: ${count}`);

    // Push and go to Other state
    s.save_and_go();
    console.log("Pushed and transitioned to Other");

    // In Other state, count should be 100 (Other's state var)
    count = s.get_count();
    if (count !== 100) {
        throw new Error(`Expected 100 in Other state, got ${count}`);
    }
    console.log(`Other state count: ${count}`);

    // Increment in Other
    s.increment();
    count = s.get_count();
    if (count !== 101) {
        throw new Error(`Expected 101 after increment, got ${count}`);
    }
    console.log(`Other state after increment: ${count}`);

    // Pop back - should restore Counter with count=3
    s.restore();
    console.log("Popped back to Counter");

    count = s.get_count();
    if (count !== 3) {
        throw new Error(`Expected 3 after pop (preserved), got ${count}`);
    }
    console.log(`Counter after pop: ${count}`);

    // Increment to verify it works
    s.increment();
    count = s.get_count();
    if (count !== 4) {
        throw new Error(`Expected 4, got ${count}`);
    }
    console.log(`Counter after increment: ${count}`);

    console.log("PASS: State variables preserved across push/pop");
}

main();

