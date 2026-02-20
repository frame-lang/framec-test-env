class StackOps {
    private _state: string;
    private _state_stack: Array<any>;
    private _state_context: Record<string, any>;
    private _return_value: any;

    constructor() {
        this._state_stack = [];
        this._state_context = {  };
        this._return_value = null;
        this._state = "Main";
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

    public do_work(): string {
        this._return_value = null
        this._dispatch_event("do_work")
        return this._return_value
    }

    public get_state(): string {
        this._return_value = null
        this._dispatch_event("get_state")
        return this._return_value
    }

    private _s_Main_push_and_go() {
        console.log("Pushing Main to stack, going to Sub");
        this._state_stack.push({state: this._state, context: {...this._state_context}});
        this._transition("Sub", null, null);
    }

    private _s_Main_do_work() {
        this._return_value = "Working in Main";
        return this._return_value;;
    }

    private _s_Main_get_state() {
        this._return_value = "Main";
        return this._return_value;;
    }

    private _s_Main_pop_back() {
        console.log("Cannot pop - nothing on stack in Main");
    }

    private _s_Sub_pop_back() {
        console.log("Popping back to previous state");
        const __saved = this._state_stack.pop()!;
        this._exit();
        this._state = __saved.state;
        this._state_context = __saved.context;
        return;
    }

    private _s_Sub_get_state() {
        this._return_value = "Sub";
        return this._return_value;;
    }

    private _s_Sub_push_and_go() {
        console.log("Already in Sub");
    }

    private _s_Sub_do_work() {
        this._return_value = "Working in Sub";
        return this._return_value;;
    }
}


function main() {
    console.log("=== Test 09: Stack Push/Pop ===");
    const s = new StackOps();

    // Initial state should be Main
    let state = s.get_state();
    if (state !== "Main") {
        throw new Error(`Expected 'Main', got '${state}'`);
    }
    console.log(`Initial state: ${state}`);

    // Do work in Main
    let work = s.do_work();
    if (work !== "Working in Main") {
        throw new Error(`Expected 'Working in Main', got '${work}'`);
    }
    console.log(`do_work(): ${work}`);

    // Push and go to Sub
    s.push_and_go();
    state = s.get_state();
    if (state !== "Sub") {
        throw new Error(`Expected 'Sub', got '${state}'`);
    }
    console.log(`After push_and_go(): ${state}`);

    // Do work in Sub
    work = s.do_work();
    if (work !== "Working in Sub") {
        throw new Error(`Expected 'Working in Sub', got '${work}'`);
    }
    console.log(`do_work(): ${work}`);

    // Pop back to Main
    s.pop_back();
    state = s.get_state();
    if (state !== "Main") {
        throw new Error(`Expected 'Main' after pop, got '${state}'`);
    }
    console.log(`After pop_back(): ${state}`);

    console.log("PASS: Stack push/pop works correctly");
}

main();

