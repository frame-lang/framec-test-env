class PersistStack {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;
    private depth: number = 0;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this.depth = 0;
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

    public push_and_go() {
        this._dispatch_event("push_and_go");
    }

    public pop_back() {
        this._dispatch_event("pop_back");
    }

    public get_state(): string {
        this._return_value = null
        this._dispatch_event("get_state")
        return this._return_value
    }

    public get_depth(): number {
        this._return_value = null
        this._dispatch_event("get_depth")
        return this._return_value
    }

    private _s_Start_get_state() {
        this._return_value = "start";
        return this._return_value;;
    }

    private _s_Start_pop_back() {
        // nothing to pop
    }

    private _s_Start_get_depth() {
        this._return_value = this.depth;
        return this._return_value;;
    }

    private _s_Start_push_and_go() {
        this.depth = this.depth + 1;
        this._state_stack.push({state: this._state, context: {...this._state_context}});
        this._transition("Middle", null, null);
    }

    private _s_End_push_and_go() {
        // can't go further
    }

    private _s_End_pop_back() {
        this.depth = this.depth - 1;
        const __saved = this._state_stack.pop()!;
        this._exit();
        this._state = __saved.state;
        this._state_context = __saved.context;
        return;
    }

    private _s_End_get_depth() {
        this._return_value = this.depth;
        return this._return_value;;
    }

    private _s_End_get_state() {
        this._return_value = "end";
        return this._return_value;;
    }

    private _s_Middle_get_state() {
        this._return_value = "middle";
        return this._return_value;;
    }

    private _s_Middle_push_and_go() {
        this.depth = this.depth + 1;
        this._state_stack.push({state: this._state, context: {...this._state_context}});
        this._transition("End", null, null);
    }

    private _s_Middle_pop_back() {
        this.depth = this.depth - 1;
        const __saved = this._state_stack.pop()!;
        this._exit();
        this._state = __saved.state;
        this._state_context = __saved.context;
        return;
    }

    private _s_Middle_get_depth() {
        this._return_value = this.depth;
        return this._return_value;;
    }

    public saveState(): any {
        return {
            _state: this._state,
            _state_context: { ...this._state_context },
            _state_stack: this._state_stack.map(e => ({state: e.state, context: {...e.context}})),
            depth: this.depth,
        };
    }

    public static restoreState(data: any): PersistStack {
        const instance = Object.create(PersistStack.prototype);
        instance._state = data._state;
        instance._state_context = { ...data._state_context };
        instance._state_stack = (data._state_stack || []).map((e: any) => ({state: e.state, context: {...e.context}}));
        instance._return_value = null;
        instance.depth = data.depth;
        return instance;
    }
}


function main(): void {
    console.log("=== Test 25: Persist Stack (TypeScript) ===");

    // Test 1: Build up a stack
    const s1 = new PersistStack();
    console.assert(s1.get_state() === "start", `Expected start, got ${s1.get_state()}`);

    s1.push_and_go();  // Start -> Middle (push Start)
    console.assert(s1.get_state() === "middle", `Expected middle, got ${s1.get_state()}`);
    console.assert(s1.get_depth() === 1, `Expected depth 1, got ${s1.get_depth()}`);

    s1.push_and_go();  // Middle -> End (push Middle)
    console.assert(s1.get_state() === "end", `Expected end, got ${s1.get_state()}`);
    console.assert(s1.get_depth() === 2, `Expected depth 2, got ${s1.get_depth()}`);

    console.log(`1. Built stack: state=${s1.get_state()}, depth=${s1.get_depth()}`);

    // Test 2: Save state (should include stack)
    const data = s1.saveState();
    console.log(`2. Saved data: ${JSON.stringify(data)}`);
    console.assert(data._state === 'End', `Expected End state`);
    console.assert(data._state_stack !== undefined, "Expected _state_stack in saved data");
    console.assert(data._state_stack.length === 2, `Expected 2 items in stack, got ${data._state_stack.length}`);

    // Test 3: Restore and verify stack works
    const s2 = PersistStack.restoreState(data);
    console.assert(s2.get_state() === "end", `Restored: expected end, got ${s2.get_state()}`);
    console.assert(s2.get_depth() === 2, `Restored: expected depth 2, got ${s2.get_depth()}`);
    console.log(`3. Restored: state=${s2.get_state()}, depth=${s2.get_depth()}`);

    // Test 4: Pop should work after restore
    s2.pop_back();  // End -> Middle (pop)
    console.assert(s2.get_state() === "middle", `After pop: expected middle, got ${s2.get_state()}`);
    console.assert(s2.get_depth() === 1, `After pop: expected depth 1, got ${s2.get_depth()}`);
    console.log(`4. After pop: state=${s2.get_state()}, depth=${s2.get_depth()}`);

    // Test 5: Pop again
    s2.pop_back();  // Middle -> Start (pop)
    console.assert(s2.get_state() === "start", `After 2nd pop: expected start, got ${s2.get_state()}`);
    console.assert(s2.get_depth() === 0, `After 2nd pop: expected depth 0, got ${s2.get_depth()}`);
    console.log(`5. After 2nd pop: state=${s2.get_state()}, depth=${s2.get_depth()}`);

    console.log("PASS: Persist stack works correctly");
}

main();

