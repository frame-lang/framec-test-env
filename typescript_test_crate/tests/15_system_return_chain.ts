
// Tests that system.return follows "last writer wins" across transition lifecycle


class SystemReturnChainTest {
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
        const handler_name = `_s_${this._state}_enter`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, ...args);
        }
    }

    private _exit(...args: any[]) {
        const handler_name = `_s_${this._state}_exit`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, ...args);
        }
    }

    public test_enter_sets(): string {
        this._return_value = null
        this._dispatch_event("test_enter_sets")
        return this._return_value
    }

    public test_exit_then_enter(): string {
        this._return_value = null
        this._dispatch_event("test_exit_then_enter")
        return this._return_value
    }

    public get_state(): string {
        this._return_value = null
        this._dispatch_event("get_state")
        return this._return_value
    }

    private _s_BothSet_enter() {
        // Enter handler sets return - should overwrite exit's value
        this._return_value = "enter_wins";;
    }

    private _s_BothSet_get_state() {
        this._return_value = "BothSet";
        return this._return_value;;
    }

    private _s_EnterSetter_enter() {
        // Enter handler sets return value
        this._return_value = "from_enter";;
    }

    private _s_EnterSetter_get_state() {
        this._return_value = "EnterSetter";
        return this._return_value;;
    }

    private _s_Start_test_exit_then_enter() {
        this._transition("BothSet", null, null);
    }

    private _s_Start_get_state() {
        this._return_value = "Start";
        return this._return_value;;
    }

    private _s_Start_test_enter_sets() {
        this._transition("EnterSetter", null, null);
    }

    private _s_Start_exit() {
        // Exit handler sets initial value
        this._return_value = "from_exit";;
    }
}


function main() {
    console.log("=== Test 15: System Return Chain (Last Writer Wins) ===");

    // Test 1: Start exit + EnterSetter enter
    // Start's exit sets "from_exit", EnterSetter's enter sets "from_enter"
    // Enter should win (last writer)
    const s1 = new SystemReturnChainTest();
    const result1 = s1.test_enter_sets();
    if (result1 !== "from_enter") {
        throw new Error(`Expected 'from_enter', got '${result1}'`);
    }
    if (s1.get_state() !== "EnterSetter") {
        throw new Error(`Expected state 'EnterSetter'`);
    }
    console.log(`1. Exit set then enter set - enter wins: '${result1}'`);

    // Test 2: Both handlers set, enter wins
    const s2 = new SystemReturnChainTest();
    const result2 = s2.test_exit_then_enter();
    if (result2 !== "enter_wins") {
        throw new Error(`Expected 'enter_wins', got '${result2}'`);
    }
    if (s2.get_state() !== "BothSet") {
        throw new Error(`Expected state 'BothSet'`);
    }
    console.log(`2. Both set - enter wins: '${result2}'`);

    console.log("PASS: System return chain (last writer wins) works correctly");
}

main();

