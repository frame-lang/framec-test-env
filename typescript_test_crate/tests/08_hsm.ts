class HSMForward {
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
        this._state = "Child";
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

    public event_a() {
        this._dispatch_event("event_a");
    }

    public event_b() {
        this._dispatch_event("event_b");
    }

    public get_log(): string[] {
        this._return_value = null
        this._dispatch_event("get_log")
        return this._return_value
    }

    private _s_Parent_event_b() {
        this.log.push("Parent:event_b");
    }

    private _s_Parent_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }

    private _s_Parent_event_a() {
        this.log.push("Parent:event_a");
    }

    private _s_Child_event_a() {
        this.log.push("Child:event_a");
    }

    private _s_Child_event_b() {
        this.log.push("Child:event_b_forward");
        this._s_Parent_event_b();
    }

    private _s_Child_get_log() {
        this._return_value = this.log;
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 08: HSM Forward ===");
    const s = new HSMForward();

    // event_a should be handled by Child (no forward)
    s.event_a();
    let log = s.get_log();
    if (!log.includes("Child:event_a")) {
        throw new Error(`Expected 'Child:event_a' in log, got ${JSON.stringify(log)}`);
    }
    console.log(`After event_a: ${JSON.stringify(log)}`);

    // event_b should forward to Parent
    s.event_b();
    log = s.get_log();
    if (!log.includes("Child:event_b_forward")) {
        throw new Error(`Expected 'Child:event_b_forward' in log, got ${JSON.stringify(log)}`);
    }
    if (!log.includes("Parent:event_b")) {
        throw new Error(`Expected 'Parent:event_b' in log (forwarded), got ${JSON.stringify(log)}`);
    }
    console.log(`After event_b (forwarded): ${JSON.stringify(log)}`);

    console.log("PASS: HSM forward works correctly");
}

main();

