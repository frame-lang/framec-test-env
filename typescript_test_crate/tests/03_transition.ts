class WithTransition {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this._state = "First";
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
        // No enter handlers
    }

    private _exit(...args: any[]) {
        // No exit handlers
    }

    public next() {
        this._dispatch_event("next");
    }

    public get_state(): string {
        this._return_value = null
        this._dispatch_event("get_state")
        return this._return_value
    }

    private _s_Second_next() {
        console.log("Transitioning: Second -> First");
        this._transition("First", null, null);
    }

    private _s_Second_get_state() {
        this._return_value = "Second";
        return this._return_value;;
    }

    private _s_First_get_state() {
        this._return_value = "First";
        return this._return_value;;
    }

    private _s_First_next() {
        console.log("Transitioning: First -> Second");
        this._transition("Second", null, null);
    }
}


function main() {
    console.log("=== Test 03: State Transitions ===");
    const s = new WithTransition();

    // Initial state should be First
    let state = s.get_state();
    if (state !== "First") {
        throw new Error(`Expected 'First', got '${state}'`);
    }
    console.log(`Initial state: ${state}`);

    // Transition to Second
    s.next();
    state = s.get_state();
    if (state !== "Second") {
        throw new Error(`Expected 'Second', got '${state}'`);
    }
    console.log(`After first next(): ${state}`);

    // Transition back to First
    s.next();
    state = s.get_state();
    if (state !== "First") {
        throw new Error(`Expected 'First', got '${state}'`);
    }
    console.log(`After second next(): ${state}`);

    console.log("PASS: State transitions work correctly");
}

main();

