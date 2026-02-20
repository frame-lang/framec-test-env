class WithInterface {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private call_count: number = 0;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.call_count = 0;
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

    public greet(name: string): string {
        this._return_value = null
        this._dispatch_event("greet", name)
        return this._return_value
    }

    public get_count(): number {
        this._return_value = null
        this._dispatch_event("get_count")
        return this._return_value
    }

    private _s_Ready_get_count() {
        this._return_value = this.call_count;
        return this._return_value;;
    }

    private _s_Ready_greet(name: string) {
        this.call_count += 1;
        this._return_value = `Hello, ${name}!`;
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 02: Interface Methods ===");
    const s = new WithInterface();

    // Test interface method with parameter and return
    const result = s.greet("World");
    if (result !== "Hello, World!") {
        throw new Error(`Expected 'Hello, World!', got '${result}'`);
    }
    console.log(`greet('World') = ${result}`);

    // Test domain variable access through interface
    let count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }
    console.log(`get_count() = ${count}`);

    // Call again to verify state
    s.greet("Frame");
    const count2 = s.get_count();
    if (count2 !== 2) {
        throw new Error(`Expected count=2, got ${count2}`);
    }
    console.log(`After second call: get_count() = ${count2}`);

    console.log("PASS: Interface methods work correctly");
}

main();

