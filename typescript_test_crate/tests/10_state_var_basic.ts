class StateVarBasic {
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

    public reset() {
        this._dispatch_event("reset");
    }

    private _s_Counter_get_count() {
        this._return_value = this._state_context["count"];
        return this._return_value;;
    }

    private _s_Counter_reset() {
        this._state_context["count"] = 0;
    }

    private _s_Counter_increment() {
        this._state_context["count"] = this._state_context["count"] + 1;
        this._return_value = this._state_context["count"];
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 10: State Variable Basic ===");
    const s = new StateVarBasic();

    // Initial value should be 0
    if (s.get_count() !== 0) {
        throw new Error(`Expected 0, got ${s.get_count()}`);
    }
    console.log(`Initial count: ${s.get_count()}`);

    // Increment should return new value
    let result = s.increment();
    if (result !== 1) {
        throw new Error(`Expected 1 after first increment, got ${result}`);
    }
    console.log(`After first increment: ${result}`);

    // Second increment
    result = s.increment();
    if (result !== 2) {
        throw new Error(`Expected 2 after second increment, got ${result}`);
    }
    console.log(`After second increment: ${result}`);

    // Reset should set back to 0
    s.reset();
    if (s.get_count() !== 0) {
        throw new Error(`Expected 0 after reset, got ${s.get_count()}`);
    }
    console.log(`After reset: ${s.get_count()}`);

    console.log("PASS: State variable basic operations work correctly");
}

main();

