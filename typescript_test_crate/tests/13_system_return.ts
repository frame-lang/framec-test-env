class SystemReturnTest {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this._state = "Calculator";
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
        if (this._state === "Calculator") {
            this._state_context["value"] = 0;
        }
    }

    private _exit(...args: any[]) {
        // No exit handlers
    }

    public add(a: number, b: number): number {
        this._return_value = null
        this._dispatch_event("add", a, b)
        return this._return_value
    }

    public multiply(a: number, b: number): number {
        this._return_value = null
        this._dispatch_event("multiply", a, b)
        return this._return_value
    }

    public greet(name: string): string {
        this._return_value = null
        this._dispatch_event("greet", name)
        return this._return_value
    }

    public get_value(): number {
        this._return_value = null
        this._dispatch_event("get_value")
        return this._return_value
    }

    private _s_Calculator_get_value() {
        this._state_context["value"] = 42;
        this._return_value = this._state_context["value"];
        return this._return_value;;
    }

    private _s_Calculator_add(a: number, b: number) {
        this._return_value = a + b;
        return this._return_value;;
    }

    private _s_Calculator_multiply(a: number, b: number) {
        this._return_value = a * b;;
    }

    private _s_Calculator_greet(name: string) {
        this._return_value = "Hello, " + name + "!";
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 13: System Return ===");
    const calc = new SystemReturnTest();

    // Test return sugar
    let result = calc.add(3, 5);
    if (result !== 8) {
        throw new Error(`Expected 8, got ${result}`);
    }
    console.log(`add(3, 5) = ${result}`);

    // Test system.return = expr
    result = calc.multiply(4, 7);
    if (result !== 28) {
        throw new Error(`Expected 28, got ${result}`);
    }
    console.log(`multiply(4, 7) = ${result}`);

    // Test string return
    const greeting = calc.greet("World");
    if (greeting !== "Hello, World!") {
        throw new Error(`Expected 'Hello, World!', got '${greeting}'`);
    }
    console.log(`greet('World') = ${greeting}`);

    // Test return with state variable
    const value = calc.get_value();
    if (value !== 42) {
        throw new Error(`Expected 42, got ${value}`);
    }
    console.log(`get_value() = ${value}`);

    console.log("PASS: System return works correctly");
}

main();

