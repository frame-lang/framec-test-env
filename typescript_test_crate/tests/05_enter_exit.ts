class EnterExit {
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
        this._state = "Off";
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

    public toggle() {
        this._dispatch_event("toggle");
    }

    public get_log(): string[] {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Off_exit() {
        this.log.push("exit:Off");
        console.log("Exiting Off state");
    }

    private _s_Off_enter() {
        this.log.push("enter:Off");
        console.log("Entered Off state");
    }

    private _s_Off_toggle() {
        this._transition("On", null, null);
    }

    private _s_Off_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_On_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_On_toggle() {
        this._transition("Off", null, null);
    }

    private _s_On_exit() {
        this.log.push("exit:On");
        console.log("Exiting On state");
    }

    private _s_On_enter() {
        this.log.push("enter:On");
        console.log("Entered On state");
    }
}


function main() {
    console.log("=== Test 05: Enter/Exit Handlers ===");
    const s = new EnterExit();

    // Initial enter should have been called
    let log = s.get_log();
    if (!log.includes("enter:Off")) {
        throw new Error(`Expected 'enter:Off' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After construction: ${JSON.stringify(log)}`);

    // Toggle to On - should exit Off, enter On
    s.toggle();
    log = s.get_log();
    if (!log.includes("exit:Off")) {
        throw new Error(`Expected 'exit:Off' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("enter:On")) {
        throw new Error(`Expected 'enter:On' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After toggle to On: ${JSON.stringify(log)}`);

    // Toggle back to Off - should exit On, enter Off
    s.toggle();
    log = s.get_log();
    const enterOffCount = log.filter(x => x === "enter:Off").length;
    if (enterOffCount !== 2) {
        throw new Error(`Expected 2 'enter:Off' entries, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("exit:On")) {
        throw new Error(`Expected 'exit:On' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After toggle to Off: ${JSON.stringify(log)}`);

    console.log("PASS: Enter/Exit handlers work correctly");
}

main();

