class PersistRoundtrip {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private counter: number = 0;
    private history: string[] =     [];
    private mode: string = "normal";

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.counter = 0;
        this.history =         [];
        this.mode = "normal";
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

    public go_active() {
        this._dispatch_event("go_active");
    }

    public go_idle() {
        this._dispatch_event("go_idle");
    }

    public get_state(): string {
        this._return_value = null
        this._dispatch_event("get_state")
        return this._return_value
    }

    public set_counter(n: number) {
        this._dispatch_event("set_counter", n);
    }

    public get_counter(): number {
        this._return_value = null
        this._dispatch_event("get_counter")
        return this._return_value
    }

    public add_history(msg: string) {
        this._dispatch_event("add_history", msg);
    }

    public get_history(): string[] {
        this._return_value = null
        this._dispatch_event("get_history")
        return this._return_value
    }

    private _s_Idle_get_history() {
        this._return_value = this.history;
        return this._return_value;;
    }

    private _s_Idle_go_idle() {
        // already idle
    }

    private _s_Idle_add_history(msg: string) {
        this.history.push("idle:" + msg);
    }

    private _s_Idle_go_active() {
        this.history.push("idle->active");
        this._transition("Active", null, null);
    }

    private _s_Idle_get_state() {
        this._return_value = "idle";
        return this._return_value;;
    }

    private _s_Idle_set_counter(n: number) {
        this.counter = n;
    }

    private _s_Idle_get_counter() {
        this._return_value = this.counter;
        return this._return_value;;
    }

    private _s_Active_get_counter() {
        this._return_value = this.counter;
        return this._return_value;;
    }

    private _s_Active_get_history() {
        this._return_value = this.history;
        return this._return_value;;
    }

    private _s_Active_get_state() {
        this._return_value = "active";
        return this._return_value;;
    }

    private _s_Active_go_idle() {
        this.history.push("active->idle");
        this._transition("Idle", null, null);
    }

    private _s_Active_add_history(msg: string) {
        this.history.push("active:" + msg);
    }

    private _s_Active_go_active() {
        // already active
    }

    private _s_Active_set_counter(n: number) {
        this.counter = n * 2;
    }

    public saveState(): any {
        return {
            _state: this._state,
            _state_context: { ...this._state_context },
            _state_stack: this._state_stack.map(e => ({state: e.state, context: {...e.context}})),
            counter: this.counter,
            history: this.history,
            mode: this.mode,
        };
    }

    public static restoreState(data: any): PersistRoundtrip {
        const instance = Object.create(PersistRoundtrip.prototype);
        instance._state = data._state;
        instance._state_context = { ...data._state_context };
        instance._state_stack = (data._state_stack || []).map((e: any) => ({state: e.state, context: {...e.context}}));
        instance._return_value = null;
        instance.counter = data.counter;
        instance.history = data.history;
        instance.mode = data.mode;
        return instance;
    }
}


function main(): void {
    console.log("=== Test 24: Persist Roundtrip (TypeScript) ===");

    // Test 1: Create system and build up state
    const s1 = new PersistRoundtrip();
    s1.set_counter(5);
    s1.add_history("start");
    s1.go_active();
    s1.set_counter(3);  // Should be 6 in Active (doubled)
    s1.add_history("work");

    if (s1.get_state() !== "active") {
        throw new Error(`Expected active, got ${s1.get_state()}`);
    }
    if (s1.get_counter() !== 6) {
        throw new Error(`Expected 6, got ${s1.get_counter()}`);
    }
    console.log(`1. State before save: state=${s1.get_state()}, counter=${s1.get_counter()}`);
    console.log(`   History: ${JSON.stringify(s1.get_history())}`);

    // Test 2: Save state
    const data = s1.saveState();
    console.log(`2. Saved data keys: ${Object.keys(data)}`);
    if (data._state !== 'Active') {
        throw new Error("Expected Active state in save data");
    }
    if (data.counter !== 6) {
        throw new Error("Expected counter=6 in save data");
    }

    // Test 3: Restore to new instance
    const s2 = PersistRoundtrip.restoreState(data);

    if (s2.get_state() !== "active") {
        throw new Error(`Expected active, got ${s2.get_state()}`);
    }
    if (s2.get_counter() !== 6) {
        throw new Error(`Expected 6, got ${s2.get_counter()}`);
    }
    console.log(`3. Restored state: state=${s2.get_state()}, counter=${s2.get_counter()}`);

    // Test 4: State machine continues to work after restore
    s2.set_counter(2);  // Should be 4 in Active (doubled)
    if (s2.get_counter() !== 4) {
        throw new Error(`Expected 4, got ${s2.get_counter()}`);
    }
    console.log(`4. Counter after set_counter(2): ${s2.get_counter()}`);

    // Test 5: Verify history was preserved
    if (JSON.stringify(s2.get_history()) !== JSON.stringify(s1.get_history())) {
        throw new Error(`History mismatch: ${JSON.stringify(s2.get_history())} vs ${JSON.stringify(s1.get_history())}`);
    }
    console.log(`5. History preserved: ${JSON.stringify(s2.get_history())}`);

    // Test 6: Transitions work after restore
    s2.go_idle();
    if (s2.get_state() !== "idle") {
        throw new Error("Expected idle after go_idle");
    }
    s2.set_counter(10);  // Not doubled in Idle
    if (s2.get_counter() !== 10) {
        throw new Error(`Expected 10, got ${s2.get_counter()}`);
    }
    console.log(`6. After go_idle: state=${s2.get_state()}, counter=${s2.get_counter()}`);

    console.log("PASS: Persist roundtrip works correctly");
}

main();

