class TransitionExitArgs {
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

    public leave() {
        this._dispatch_event("leave");
    }

    public get_log(): string[] {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Active_leave() {
        this.log.push("leaving");
        this._transition("Done", ["cleanup", 42], null);
    }

    private _s_Active_exit(reason: string, code: number) {
        this.log.push(`exit:${reason}:${code}`);
    }

    private _s_Active_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Done_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Done_enter() {
        this.log.push("enter:done");
    }
}


function main() {
    console.log("=== Test 18: Transition Exit Args ===");
    const s = new TransitionExitArgs();

    // Initial state is Active
    let log = s.get_log();
    if (log.length !== 0) {
        throw new Error(`Expected empty log, got ${JSON.stringify(log)}`);
    }

    // Leave - should call exit handler with args
    s.leave();
    log = s.get_log();
    if (!log.includes("leaving")) {
        throw new Error(`Expected 'leaving' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("exit:cleanup:42")) {
        throw new Error(`Expected 'exit:cleanup:42' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("enter:done")) {
        throw new Error(`Expected 'enter:done' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`Log after transition: ${JSON.stringify(log)}`);

    console.log("PASS: Transition exit args work correctly");
}

main();

