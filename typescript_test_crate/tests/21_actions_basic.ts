class ActionsTest {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private log: string = "";

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.log = "";
        this._state = "Ready";
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

    public process(value: number): number {
        this._return_value = null
        this._dispatch_event("process", value)
        return this._return_value
    }

    public get_log(): string {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Ready_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Ready_process(value: number) {
        this.__log_event("start");
        this.__validate_positive(value);
        this.__log_event("valid");
        const result = value * 2;
        this.__log_event("done");
        this._return_value = result;
        return this._return_value;;
    }

    private __log_event(msg: string) {
                    this.log = this.log + msg + ";";
    }

    private __validate_positive(n: number) {
                    if (n < 0) {
                        throw new Error(`Value must be positive: ${n}`);
                    }
    }
}


function main(): void {
    console.log("=== Test 21: Actions Basic (TypeScript) ===");
    const s = new ActionsTest();

    // Test 1: Actions are called correctly
    const result = s.process(5);
    if (result !== 10) {
        throw new Error(`Expected 10, got ${result}`);
    }
    console.log(`1. process(5) = ${result}`);

    // Test 2: Log shows action calls
    const log = s.get_log();
    if (!log.includes("start")) {
        throw new Error(`Missing 'start' in log: ${log}`);
    }
    if (!log.includes("valid")) {
        throw new Error(`Missing 'valid' in log: ${log}`);
    }
    if (!log.includes("done")) {
        throw new Error(`Missing 'done' in log: ${log}`);
    }
    console.log(`2. Log: ${log}`);

    // Test 3: Action with validation
    try {
        s.process(-1);
        throw new Error("Should have thrown Error");
    } catch (e) {
        if (e instanceof Error && e.message.includes("positive")) {
            console.log(`3. Validation caught: ${e.message}`);
        } else {
            throw e;
        }
    }

    console.log("PASS: Actions basic works correctly");
}

main();

