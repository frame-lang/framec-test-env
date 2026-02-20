class TransitionEnterArgs {
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
        const handler_name = `_s_${this._state}_enter`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, ...args);
        }
    }

    private _exit(...args: any[]) {
        // No exit handlers
    }

    public start() {
        this._dispatch_event("start");
    }

    public get_log(): string[] {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Active_start() {
        this.log.push("active:start");
    }

    private _s_Active_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Active_enter(source: string, value: number) {
        this.log.push(`active:enter:${source}:${value}`);
    }

    private _s_Idle_start() {
        this.log.push("idle:start");
        this._transition("Active", null, ["from_idle", 42]);
    }

    private _s_Idle_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 17: Transition Enter Args ===");
    const s = new TransitionEnterArgs();

    // Initial state is Idle
    let log = s.get_log();
    if (log.length !== 0) {
        throw new Error(`Expected empty log, got ${JSON.stringify(log)}`);
    }

    // Transition to Active with args
    s.start();
    log = s.get_log();
    if (!log.includes("idle:start")) {
        throw new Error(`Expected 'idle:start' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("active:enter:from_idle:42")) {
        throw new Error(`Expected 'active:enter:from_idle:42' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`Log after transition: ${JSON.stringify(log)}`);

    console.log("PASS: Transition enter args work correctly");
}

main();

