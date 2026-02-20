
function helper_function(x: number): number {
    // Native helper function defined before system
    return x * 2;
}


class NativeCode {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this._state = "Active";
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

    public compute(value: number): number {
        this._return_value = null
        this._dispatch_event("compute", value)
        return this._return_value
    }

    public use_math(): number {
        this._return_value = null
        this._dispatch_event("use_math")
        return this._return_value
    }

    private _s_Active_compute(value: number) {
        // Native code with local variables
        const temp = value + 10;
        const result = helper_function(temp);
        console.log(`Computed: ${value} -> ${result}`);
        this._return_value = result;
        return this._return_value;;
    }

    private _s_Active_use_math() {
        // Using Math module
        const result = Math.sqrt(16) + Math.PI;
        console.log(`Math result: ${result}`);
        this._return_value = result;
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 04: Native Code Preservation ===");
    const s = new NativeCode();

    // Test native code in handler with helper function
    const result = s.compute(5);
    const expected = (5 + 10) * 2;  // 30
    if (result !== expected) {
        throw new Error(`Expected ${expected}, got ${result}`);
    }
    console.log(`compute(5) = ${result}`);

    // Test Math module usage
    const mathResult = s.use_math();
    const expectedMath = Math.sqrt(16) + Math.PI;
    if (Math.abs(mathResult - expectedMath) >= 0.001) {
        throw new Error(`Expected ~${expectedMath}, got ${mathResult}`);
    }
    console.log(`use_math() = ${mathResult}`);

    console.log("PASS: Native code preservation works correctly");
}

main();

