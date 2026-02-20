
// Tests that nested interface calls maintain separate return contexts


class SystemReturnReentrantTest {
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
            this._state_context["log"] = "";
        }
    }

    private _exit(...args: any[]) {
        // No exit handlers
    }

    public outer_call(): string {
        this._return_value = null
        this._dispatch_event("outer_call")
        return this._return_value
    }

    public inner_call(): string {
        this._return_value = null
        this._dispatch_event("inner_call")
        return this._return_value
    }

    public nested_call(): string {
        this._return_value = null
        this._dispatch_event("nested_call")
        return this._return_value
    }

    public get_log(): string {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Start_get_log() {
        this._return_value = this._state_context["log"];
        return this._return_value;;
    }

    private _s_Start_inner_call() {
        this._state_context["log"] = this._state_context["log"] + "inner,";
        this._return_value = "inner_result";
        return this._return_value;;
    }

    private _s_Start_outer_call() {
        this._state_context["log"] = this._state_context["log"] + "outer_start,";
        // Call inner method - this creates nested return context
        const inner_result = this.inner_call();
        this._state_context["log"] = this._state_context["log"] + "outer_after_inner,";
        // Our return should be independent of inner's return
        this._return_value = "outer_result:" + inner_result;
        return this._return_value;;
    }

    private _s_Start_nested_call() {
        this._state_context["log"] = this._state_context["log"] + "nested_start,";
        // Two levels of nesting
        const result1 = this.inner_call();
        const result2 = this.outer_call();
        this._state_context["log"] = this._state_context["log"] + "nested_end,";
        this._return_value = "nested:" + result1 + "+" + result2;
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 16: System Return Reentrant (Nested Calls) ===");

    // Test 1: Simple inner call
    const s1 = new SystemReturnReentrantTest();
    const result1 = s1.inner_call();
    if (result1 !== "inner_result") {
        throw new Error(`Expected 'inner_result', got '${result1}'`);
    }
    console.log(`1. inner_call() = '${result1}'`);

    // Test 2: Outer calls inner - return contexts should be separate
    const s2 = new SystemReturnReentrantTest();
    const result2 = s2.outer_call();
    if (result2 !== "outer_result:inner_result") {
        throw new Error(`Expected 'outer_result:inner_result', got '${result2}'`);
    }
    const log2 = s2.get_log();
    if (!log2.includes("outer_start")) {
        throw new Error(`Missing outer_start in log: ${log2}`);
    }
    if (!log2.includes("inner")) {
        throw new Error(`Missing inner in log: ${log2}`);
    }
    if (!log2.includes("outer_after_inner")) {
        throw new Error(`Missing outer_after_inner in log: ${log2}`);
    }
    console.log(`2. outer_call() = '${result2}'`);
    console.log(`   Log: '${log2}'`);

    // Test 3: Deeply nested calls
    const s3 = new SystemReturnReentrantTest();
    const result3 = s3.nested_call();
    const expected = "nested:inner_result+outer_result:inner_result";
    if (result3 !== expected) {
        throw new Error(`Expected '${expected}', got '${result3}'`);
    }
    console.log(`3. nested_call() = '${result3}'`);

    console.log("PASS: System return reentrant (nested calls) works correctly");
}

main();

