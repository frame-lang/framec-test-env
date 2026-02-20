class StateVarReentry {
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

    public go_other() {
        this._dispatch_event("go_other");
    }

    public come_back() {
        this._dispatch_event("come_back");
    }

    private _s_Other_increment() {
        this._return_value = -1;
        return this._return_value;;
    }

    private _s_Other_get_count() {
        this._return_value = -1;
        return this._return_value;;
    }

    private _s_Other_come_back() {
        this._transition("Counter", null, null);
    }

    private _s_Counter_go_other() {
        this._transition("Other", null, null);
    }

    private _s_Counter_increment() {
        this._state_context["count"] = this._state_context["count"] + 1;
        this._return_value = this._state_context["count"];
        return this._return_value;;
    }

    private _s_Counter_get_count() {
        this._return_value = this._state_context["count"];
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 11: State Variable Reentry ===");
    const s = new StateVarReentry();

    // Increment a few times
    s.increment();
    s.increment();
    let count = s.get_count();
    if (count !== 2) {
        throw new Error(`Expected 2 after two increments, got ${count}`);
    }
    console.log(`Count before leaving: ${count}`);

    // Leave the state
    s.go_other();
    console.log("Transitioned to Other state");

    // Come back - state var should be reinitialized to 0
    s.come_back();
    count = s.get_count();
    if (count !== 0) {
        throw new Error(`Expected 0 after re-entering Counter (state var reinit), got ${count}`);
    }
    console.log(`Count after re-entering Counter: ${count}`);

    // Increment again to verify it works
    const result = s.increment();
    if (result !== 1) {
        throw new Error(`Expected 1 after increment, got ${result}`);
    }
    console.log(`After increment: ${result}`);

    console.log("PASS: State variables reinitialize on state reentry");
}

main();

