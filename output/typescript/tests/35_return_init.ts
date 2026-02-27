
// Test: Interface method return_init
// Validates that interface methods can have default return values
// Syntax: method(): type = "default_value"


class ReturnInitTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class ReturnInitTestFrameContext {
    public event: ReturnInitTestFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: ReturnInitTestFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class ReturnInitTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: ReturnInitTestCompartment | null;

    constructor(state: string, parent_compartment: ReturnInitTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): ReturnInitTestCompartment {
        const c = new ReturnInitTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class ReturnInitTest {
    private _state_stack: Array<any>;
    private __compartment: ReturnInitTestCompartment;
    private __next_compartment: ReturnInitTestCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new ReturnInitTestCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new ReturnInitTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: ReturnInitTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new ReturnInitTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new ReturnInitTestFrameEvent("$>", this.__compartment.enter_args);
                this.__router(enter_event);
            } else {
                // Forward event to new state
                const forward_event = next_compartment.forward_event;
                next_compartment.forward_event = null;
                if (forward_event._message === "$>") {
                    // Forwarding enter event - just send it
                    this.__router(forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    const enter_event = new ReturnInitTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: ReturnInitTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: ReturnInitTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public get_status(): string {
        const __e = new ReturnInitTestFrameEvent("get_status", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_count(): number {
        const __e = new ReturnInitTestFrameEvent("get_count", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_flag(): boolean {
        const __e = new ReturnInitTestFrameEvent("get_flag", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public trigger() {
        const __e = new ReturnInitTestFrameEvent("trigger", null);
        const __ctx = new ReturnInitTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    private _state_Active(__e: ReturnInitTestFrameEvent) {
        if (__e._message === "$>") {
            // Active state enter (no-op)
        } else if (__e._message === "get_count") {
            this._context_stack[this._context_stack.length - 1]._return = 42;;
        } else if (__e._message === "get_flag") {
            this._context_stack[this._context_stack.length - 1]._return = true;;
        } else if (__e._message === "get_status") {
            this._context_stack[this._context_stack.length - 1]._return = "active";;
        } else if (__e._message === "trigger") {
            const __compartment = new ReturnInitTestCompartment("Start", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }

    private _state_Start(__e: ReturnInitTestFrameEvent) {
        if (__e._message === "$>") {
            // Start state enter (no-op)
        } else if (__e._message === "get_count") {
            // Don't set return - should use default 0
        } else if (__e._message === "get_flag") {
            // Don't set return - should use default false
        } else if (__e._message === "get_status") {
            // Don't set return - should use default "unknown"
        } else if (__e._message === "trigger") {
            const __compartment = new ReturnInitTestCompartment("Active", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }
}


function main() {
    console.log("TAP version 14");
    console.log("1..6");

    const s = new ReturnInitTest();

    // Test 1: Default string return
    if (s.get_status() === "unknown") {
        console.log("ok 1 - default string return is 'unknown'");
    } else {
        console.log(`not ok 1 - default string return is 'unknown' # got ${s.get_status()}`);
    }

    // Test 2: Default int return
    if (s.get_count() === 0) {
        console.log("ok 2 - default int return is 0");
    } else {
        console.log(`not ok 2 - default int return is 0 # got ${s.get_count()}`);
    }

    // Test 3: Default bool return
    if (s.get_flag() === false) {
        console.log("ok 3 - default bool return is false");
    } else {
        console.log(`not ok 3 - default bool return is false # got ${s.get_flag()}`);
    }

    // Transition to Active state
    s.trigger();

    // Test 4: Explicit string return overrides default
    if (s.get_status() === "active") {
        console.log("ok 4 - explicit return overrides default string");
    } else {
        console.log(`not ok 4 - explicit return overrides default string # got ${s.get_status()}`);
    }

    // Test 5: Explicit int return overrides default
    if (s.get_count() === 42) {
        console.log("ok 5 - explicit return overrides default int");
    } else {
        console.log(`not ok 5 - explicit return overrides default int # got ${s.get_count()}`);
    }

    // Test 6: Explicit bool return overrides default
    if (s.get_flag() === true) {
        console.log("ok 6 - explicit return overrides default bool");
    } else {
        console.log(`not ok 6 - explicit return overrides default bool # got ${s.get_flag()}`);
    }

    console.log("# PASS - return_init provides default return values");
}

main();
