class OperationsTest {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private last_result: number = 0;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.last_result = 0;
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

    public compute(a: number, b: number): number {
        this._return_value = null
        this._dispatch_event("compute", a, b)
        return this._return_value
    }

    public get_last_result(): number {
        this._return_value = null
        this._dispatch_event("get_last_result")
        return this._return_value
    }

    private _s_Ready_compute(a: number, b: number) {
        // Use instance operations
        const sum_val = this.add(a, b);
        const prod_val = this.multiply(a, b);
        const last_result = sum_val + prod_val;
        this._return_value = last_result;
        return this._return_value;;
    }

    private _s_Ready_get_last_result() {
        this._return_value = this.last_result;
        return this._return_value;;
    }

    public add(x: number, y: number): number {
                    return x + y;
    }

    public multiply(x: number, y: number): number {
                    return x * y;
    }

    public static factorial(n: number): number {
                    if (n <= 1) {
                        return 1;
                    }
                    return n * OperationsTest.factorial(n - 1);
    }

    public static is_even(n: number): boolean {
                    return n % 2 === 0;
    }
}


function main(): void {
    console.log("=== Test 22: Operations Basic (TypeScript) ===");
    const s = new OperationsTest();

    // Test 1: Instance operations
    let result = s.add(3, 4);
    if (result !== 7) {
        throw new Error(`Expected 7, got ${result}`);
    }
    console.log(`1. add(3, 4) = ${result}`);

    result = s.multiply(3, 4);
    if (result !== 12) {
        throw new Error(`Expected 12, got ${result}`);
    }
    console.log(`2. multiply(3, 4) = ${result}`);

    // Test 2: Operations used in handler
    result = s.compute(3, 4);
    // compute returns add(3,4) + multiply(3,4) = 7 + 12 = 19
    if (result !== 19) {
        throw new Error(`Expected 19, got ${result}`);
    }
    console.log(`3. compute(3, 4) = ${result}`);

    // Test 3: Static operations
    result = OperationsTest.factorial(5);
    if (result !== 120) {
        throw new Error(`Expected 120, got ${result}`);
    }
    console.log(`4. factorial(5) = ${result}`);

    let is_even = OperationsTest.is_even(4);
    if (is_even !== true) {
        throw new Error(`Expected true, got ${is_even}`);
    }
    console.log(`5. is_even(4) = ${is_even}`);

    is_even = OperationsTest.is_even(7);
    if (is_even !== false) {
        throw new Error(`Expected false, got ${is_even}`);
    }
    console.log(`6. is_even(7) = ${is_even}`);

    // Test 4: Static via class (TypeScript doesn't allow instance.static())
    result = OperationsTest.factorial(4);
    if (result !== 24) {
        throw new Error(`Expected 24, got ${result}`);
    }
    console.log(`7. OperationsTest.factorial(4) = ${result}`);

    console.log("PASS: Operations basic works correctly");
}

main();

