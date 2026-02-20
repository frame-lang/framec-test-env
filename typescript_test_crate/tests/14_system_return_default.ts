
// NOTE: Default return value syntax (method(): type = default) not yet implemented.
// This test validates behavior when handler doesn't set system.return.


class SystemReturnDefaultTest {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this._state = "Start";
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
        if (this._state === "Start") {
            this._state_context["count"] = 0;
        }
    }

    private _exit(...args: any[]) {
        // No exit handlers
    }

    public handler_sets_value(): string {
        this._return_value = null
        this._dispatch_event("handler_sets_value")
        return this._return_value
    }

    public handler_no_return(): string | null {
        this._return_value = null
        this._dispatch_event("handler_no_return")
        return this._return_value
    }

    public get_count(): number {
        this._return_value = null
        this._dispatch_event("get_count")
        return this._return_value
    }

    private _s_Start_handler_sets_value() {
        this._return_value = "set_by_handler";
        return this._return_value;;
    }

    private _s_Start_handler_no_return() {
        // Does not set return - should return null/undefined
        this._state_context["count"] = this._state_context["count"] + 1;
    }

    private _s_Start_get_count() {
        this._return_value = this._state_context["count"];
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 14: System Return Default Behavior ===");
    const s = new SystemReturnDefaultTest();

    // Test 1: Handler explicitly sets return value
    const result1 = s.handler_sets_value();
    if (result1 !== "set_by_handler") {
        throw new Error(`Expected 'set_by_handler', got '${result1}'`);
    }
    console.log(`1. handler_sets_value() = '${result1}'`);

    // Test 2: Handler does NOT set return - should return null/undefined
    const result2 = s.handler_no_return();
    if (result2 !== null && result2 !== undefined) {
        throw new Error(`Expected null/undefined, got '${result2}'`);
    }
    console.log(`2. handler_no_return() = ${result2}`);

    // Test 3: Verify handler was called (side effect check)
    let count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }
    console.log(`3. Handler was called, count = ${count}`);

    // Test 4: Call again to verify idempotence
    const result4 = s.handler_no_return();
    if (result4 !== null && result4 !== undefined) {
        throw new Error(`Expected null/undefined again, got '${result4}'`);
    }
    count = s.get_count();
    if (count !== 2) {
        throw new Error(`Expected count=2, got ${count}`);
    }
    console.log(`4. Second call: result=${result4}, count=${count}`);

    console.log("PASS: System return default behavior works correctly");
}

main();

