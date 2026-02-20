class WithParams {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private total: number = 0;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.total = 0;
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

    public start(initial: number) {
        this._dispatch_event("start", initial);
    }

    public add(value: number) {
        this._dispatch_event("add", value);
    }

    public multiply(a: number, b: number): number {
        this._return_value = null
        this._dispatch_event("multiply", a, b)
        return this._return_value
    }

    public get_total(): number {
        this._return_value = null
        this._dispatch_event("get_total")
        return this._return_value
    }

    private _s_Idle_multiply(a: number, b: number) {
        this._return_value = 0;
        return this._return_value;;
    }

    private _s_Idle_add(value: number) {
        console.log("Cannot add in Idle state");
    }

    private _s_Idle_start(initial: number) {
        this.total = initial;
        console.log(`Started with initial value: ${initial}`);
        this._transition("Running", null, null);
    }

    private _s_Idle_get_total() {
        this._return_value = this.total;
        return this._return_value;;
    }

    private _s_Running_get_total() {
        this._return_value = this.total;
        return this._return_value;;
    }

    private _s_Running_add(value: number) {
        this.total += value;
        console.log(`Added ${value}, total is now ${this.total}`);
    }

    private _s_Running_multiply(a: number, b: number) {
        const result = a * b;
        this.total += result;
        console.log(`Multiplied ${a} * ${b} = ${result}, total is now ${this.total}`);
        this._return_value = result;
        return this._return_value;;
    }

    private _s_Running_start(initial: number) {
        console.log("Already running");
    }
}


function main() {
    console.log("=== Test 07: Handler Parameters ===");
    const s = new WithParams();

    // Initial total should be 0
    let total = s.get_total();
    if (total !== 0) {
        throw new Error(`Expected initial total=0, got ${total}`);
    }

    // Start with initial value
    s.start(100);
    total = s.get_total();
    if (total !== 100) {
        throw new Error(`Expected total=100, got ${total}`);
    }
    console.log(`After start(100): total = ${total}`);

    // Add value
    s.add(25);
    total = s.get_total();
    if (total !== 125) {
        throw new Error(`Expected total=125, got ${total}`);
    }
    console.log(`After add(25): total = ${total}`);

    // Multiply with two params
    const result = s.multiply(3, 5);
    if (result !== 15) {
        throw new Error(`Expected multiply result=15, got ${result}`);
    }
    total = s.get_total();
    if (total !== 140) {
        throw new Error(`Expected total=140, got ${total}`);
    }
    console.log(`After multiply(3,5): result = ${result}, total = ${total}`);

    console.log("PASS: Handler parameters work correctly");
}

main();

