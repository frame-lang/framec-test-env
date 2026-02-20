class TransitionPopTest {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private log: string[] =     [];

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.log =         [];
        this._state = "Idle";
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

    public start() {
        this._dispatch_event("start");
    }

    public process() {
        this._dispatch_event("process");
    }

    public get_state(): string {
        this._return_value = null
        this._dispatch_event("get_state")
        return this._return_value
    }

    public get_log(): string[] {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Idle_process() {
        this.log.push("idle:process");
    }

    private _s_Idle_start() {
        this.log.push("idle:start:push");
        this._state_stack.push({state: this._state, context: {...this._state_context}});
        this._transition("Working", null, null);
    }

    private _s_Idle_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Idle_get_state() {
        this._return_value = "Idle";
        return this._return_value;;
    }

    private _s_Working_get_state() {
        this._return_value = "Working";
        return this._return_value;;
    }

    private _s_Working_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Working_process() {
        this.log.push("working:process:before_pop");
        const __saved = this._state_stack.pop()!;
        this._exit();
        this._state = __saved.state;
        this._state_context = __saved.context;
        return;
        // This should NOT execute because pop transitions away
        this.log.push("working:process:after_pop");
    }
}


function main(): void {
    console.log("=== Test 20: Transition Pop (TypeScript) ===");
    const s = new TransitionPopTest();

    // Initial state should be Idle
    if (s.get_state() !== "Idle") throw new Error(`Expected 'Idle', got '${s.get_state()}'`);
    console.log(`Initial state: ${s.get_state()}`);

    // start() pushes Idle, transitions to Working
    s.start();
    if (s.get_state() !== "Working") throw new Error(`Expected 'Working', got '${s.get_state()}'`);
    console.log(`After start(): ${s.get_state()}`);

    // process() in Working does pop transition back to Idle
    s.process();
    if (s.get_state() !== "Idle") throw new Error(`Expected 'Idle' after pop, got '${s.get_state()}'`);
    console.log(`After process() with pop: ${s.get_state()}`);

    const log = s.get_log();
    console.log(`Log: ${JSON.stringify(log)}`);

    // Verify log contents
    if (!log.includes("idle:start:push")) throw new Error("Expected 'idle:start:push' in log");
    if (!log.includes("working:process:before_pop")) throw new Error("Expected 'working:process:before_pop' in log");
    if (log.includes("working:process:after_pop")) throw new Error("Should NOT have 'working:process:after_pop' in log");

    console.log("PASS: Transition pop works correctly");
}

main();

