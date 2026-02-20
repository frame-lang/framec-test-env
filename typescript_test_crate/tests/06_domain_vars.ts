class DomainVars {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private count: number = 0;
    private name: string = "counter";

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.count = 0;
        this.name = "counter";
        this._state = "Counting";
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

    public increment() {
        this._dispatch_event("increment");
    }

    public decrement() {
        this._dispatch_event("decrement");
    }

    public get_count(): number {
        this._return_value = null
        this._dispatch_event("get_count")
        return this._return_value
    }

    public set_count(value: number) {
        this._dispatch_event("set_count", value);
    }

    private _s_Counting_increment() {
        this.count += 1;
        console.log(`${this.name}: incremented to ${this.count}`);
    }

    private _s_Counting_decrement() {
        this.count -= 1;
        console.log(`${this.name}: decremented to ${this.count}`);
    }

    private _s_Counting_get_count() {
        this._return_value = this.count;
        return this._return_value;;
    }

    private _s_Counting_set_count(value: number) {
        this.count = value;
        console.log(`${this.name}: set to ${this.count}`);
    }
}


function main() {
    console.log("=== Test 06: Domain Variables ===");
    const s = new DomainVars();

    // Initial value should be 0
    let count = s.get_count();
    if (count !== 0) {
        throw new Error(`Expected initial count=0, got ${count}`);
    }
    console.log(`Initial count: ${count}`);

    // Increment
    s.increment();
    count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }

    s.increment();
    count = s.get_count();
    if (count !== 2) {
        throw new Error(`Expected count=2, got ${count}`);
    }

    // Decrement
    s.decrement();
    count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }

    // Set directly
    s.set_count(100);
    count = s.get_count();
    if (count !== 100) {
        throw new Error(`Expected count=100, got ${count}`);
    }

    console.log(`Final count: ${count}`);
    console.log("PASS: Domain variables work correctly");
}

main();

