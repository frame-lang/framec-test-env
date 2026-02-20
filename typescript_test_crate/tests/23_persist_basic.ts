class PersistTest {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private value: number = 0;
    private name: string = "default";

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.value = 0;
        this.name = "default";
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

    public set_value(v: number) {
        this._dispatch_event("set_value", v);
    }

    public get_value(): number {
        this._return_value = null
        this._dispatch_event("get_value")
        return this._return_value
    }

    public go_active() {
        this._dispatch_event("go_active");
    }

    public go_idle() {
        this._dispatch_event("go_idle");
    }

    private _s_Idle_go_idle() {
        // Already idle
    }

    private _s_Idle_go_active() {
        this._transition("Active", null, null);
    }

    private _s_Idle_set_value(v: number) {
        this.value = v;
    }

    private _s_Idle_get_value() {
        this._return_value = this.value;
        return this._return_value;;
    }

    private _s_Active_set_value(v: number) {
        this.value = v * 2;
    }

    private _s_Active_get_value() {
        this._return_value = this.value;
        return this._return_value;;
    }

    private _s_Active_go_idle() {
        this._transition("Idle", null, null);
    }

    private _s_Active_go_active() {
        // Already active
    }

    public saveState(): any {
        return {
            _state: this._state,
            _state_context: { ...this._state_context },
            _state_stack: this._state_stack.map(e => ({state: e.state, context: {...e.context}})),
            value: this.value,
            name: this.name,
        };
    }

    public static restoreState(data: any): PersistTest {
        const instance = Object.create(PersistTest.prototype);
        instance._state = data._state;
        instance._state_context = { ...data._state_context };
        instance._state_stack = (data._state_stack || []).map((e: any) => ({state: e.state, context: {...e.context}}));
        instance._return_value = null;
        instance.value = data.value;
        instance.name = data.name;
        return instance;
    }
}


function main(): void {
    console.log("=== Test 23: Persist Basic (TypeScript) ===");

    // Test 1: Create and modify system
    const s1 = new PersistTest();
    s1.set_value(10);
    s1.go_active();
    s1.set_value(5);  // Should be doubled to 10 in Active state

    // Test 2: Save state
    const data = s1.saveState();
    if (data._state !== 'Active') {
        throw new Error(`Expected 'Active', got ${data._state}`);
    }
    if (data.value !== 10) {
        throw new Error(`Expected 10, got ${data.value}`);
    }
    console.log(`1. Saved state: ${JSON.stringify(data)}`);

    // Test 3: Restore state
    const s2 = PersistTest.restoreState(data);
    if (s2.get_value() !== 10) {
        throw new Error(`Expected 10, got ${s2.get_value()}`);
    }
    console.log(`2. Restored value: ${s2.get_value()}`);

    // Test 4: Verify state is preserved (Active state doubles)
    s2.set_value(3);  // Should be doubled to 6 in Active state
    if (s2.get_value() !== 6) {
        throw new Error(`Expected 6, got ${s2.get_value()}`);
    }
    console.log(`3. After set_value(3) in Active: ${s2.get_value()}`);

    // Test 5: Verify transitions work after restore
    s2.go_idle();
    s2.set_value(4);  // Should NOT be doubled in Idle state
    if (s2.get_value() !== 4) {
        throw new Error(`Expected 4, got ${s2.get_value()}`);
    }
    console.log(`4. After go_idle, set_value(4): ${s2.get_value()}`);

    console.log("PASS: Persist basic works correctly");
}

main();

