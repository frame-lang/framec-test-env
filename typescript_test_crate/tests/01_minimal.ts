class Minimal {
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
        // No enter handlers
    }

    private _exit(...args: any[]) {
        // No exit handlers
    }

    public is_alive(): boolean {
        this._return_value = null
        this._dispatch_event("is_alive")
        return this._return_value
    }

    private _s_Start_is_alive() {
        this._return_value = true;
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 01: Minimal System ===");
    const s = new Minimal();

    // Test that system instantiates and responds
    const result = s.is_alive();
    if (result !== true) {
        throw new Error(`Expected true, got ${result}`);
    }
    console.log(`is_alive() = ${result}`);

    console.log("PASS: Minimal system works correctly");
}

main();

