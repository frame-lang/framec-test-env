class EventForwardTest {
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

    public process() {
        this._dispatch_event("process");
    }

    public get_log(): string[] {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Idle_process() {
        this.log.push("idle:process:before");
        this._transition("Working", null, null);
        return this._dispatch_event("process");
        // This should NOT execute because -> => returns after dispatch
        this.log.push("idle:process:after");
    }

    private _s_Idle_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Working_process() {
        this.log.push("working:process");
    }

    private _s_Working_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }
}


function main(): void {
    console.log("=== Test 19: Transition Forward (TypeScript) ===");
    const s = new EventForwardTest();
    s.process();
    const log = s.get_log();
    console.log(`Log: ${JSON.stringify(log)}`);

    // After transition-forward:
    // - Idle logs "idle:process:before"
    // - Transition to Working
    // - Working handles process(), logs "working:process"
    // - Return prevents "idle:process:after"
    if (!log.includes("idle:process:before")) {
        throw new Error(`Expected 'idle:process:before' in log: ${log}`);
    }
    if (!log.includes("working:process")) {
        throw new Error(`Expected 'working:process' in log: ${log}`);
    }
    if (log.includes("idle:process:after")) {
        throw new Error(`Should NOT have 'idle:process:after' in log: ${log}`);
    }

    console.log("PASS: Transition forward works correctly");
}

main();

