
// Tests that system.return follows "last writer wins" across transition lifecycle


class SystemReturnChainTestFrameEvent {
    public _message: string;
    public _parameters: Record<string, any> | null;

    constructor(message: string, parameters: Record<string, any> | null) {
        this._message = message;
        this._parameters = parameters;
    }
}


class SystemReturnChainTestFrameContext {
    public event: SystemReturnChainTestFrameEvent;
    public _return: any;
    public _data: Record<string, any>;

    constructor(event: SystemReturnChainTestFrameEvent, default_return: any) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


class SystemReturnChainTestCompartment {
    public state: string;
    public state_args: Record<string, any>;
    public state_vars: Record<string, any>;
    public enter_args: Record<string, any>;
    public exit_args: Record<string, any>;
    public forward_event: any;
    public parent_compartment: SystemReturnChainTestCompartment | null;

    constructor(state: string, parent_compartment: SystemReturnChainTestCompartment | null = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    public copy(): SystemReturnChainTestCompartment {
        const c = new SystemReturnChainTestCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


class SystemReturnChainTest {
    private _state_stack: Array<any>;
    private __compartment: SystemReturnChainTestCompartment;
    private __next_compartment: SystemReturnChainTestCompartment | null;
    private _context_stack: Array<any>;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new SystemReturnChainTestCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new SystemReturnChainTestFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    private __kernel(__e: SystemReturnChainTestFrameEvent) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new SystemReturnChainTestFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new SystemReturnChainTestFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new SystemReturnChainTestFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    private __router(__e: SystemReturnChainTestFrameEvent) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = (this as any)[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    private __transition(next_compartment: SystemReturnChainTestCompartment) {
        this.__next_compartment = next_compartment;
    }

    public test_enter_sets(): string {
        const __e = new SystemReturnChainTestFrameEvent("test_enter_sets", null);
        const __ctx = new SystemReturnChainTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public test_exit_then_enter(): string {
        const __e = new SystemReturnChainTestFrameEvent("test_exit_then_enter", null);
        const __ctx = new SystemReturnChainTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    public get_state(): string {
        const __e = new SystemReturnChainTestFrameEvent("get_state", null);
        const __ctx = new SystemReturnChainTestFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()!._return;
    }

    private _state_EnterSetter(__e: SystemReturnChainTestFrameEvent) {
        if (__e._message === "$>") {
            // Enter handler sets return value
            this._context_stack[this._context_stack.length - 1]._return = "from_enter";;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "EnterSetter";
            return;;
        }
    }

    private _state_BothSet(__e: SystemReturnChainTestFrameEvent) {
        if (__e._message === "$>") {
            // Enter handler sets return - should overwrite exit's value
            this._context_stack[this._context_stack.length - 1]._return = "enter_wins";;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "BothSet";
            return;;
        }
    }

    private _state_Start(__e: SystemReturnChainTestFrameEvent) {
        if (__e._message === "<$") {
            // Exit handler sets initial value
            this._context_stack[this._context_stack.length - 1]._return = "from_exit";;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Start";
            return;;
        } else if (__e._message === "test_enter_sets") {
            const __compartment = new SystemReturnChainTestCompartment("EnterSetter", this.__compartment.copy());
            this.__transition(__compartment);
        } else if (__e._message === "test_exit_then_enter") {
            const __compartment = new SystemReturnChainTestCompartment("BothSet", this.__compartment.copy());
            this.__transition(__compartment);
        }
    }
}


function main() {
    console.log("=== Test 15: System Return Chain (Last Writer Wins) ===");

    // Test 1: Start exit + EnterSetter enter
    // Start's exit sets "from_exit", EnterSetter's enter sets "from_enter"
    // Enter should win (last writer)
    const s1 = new SystemReturnChainTest();
    const result1 = s1.test_enter_sets();
    if (result1 !== "from_enter") {
        throw new Error(`Expected 'from_enter', got '${result1}'`);
    }
    if (s1.get_state() !== "EnterSetter") {
        throw new Error(`Expected state 'EnterSetter'`);
    }
    console.log(`1. Exit set then enter set - enter wins: '${result1}'`);

    // Test 2: Both handlers set, enter wins
    const s2 = new SystemReturnChainTest();
    const result2 = s2.test_exit_then_enter();
    if (result2 !== "enter_wins") {
        throw new Error(`Expected 'enter_wins', got '${result2}'`);
    }
    if (s2.get_state() !== "BothSet") {
        throw new Error(`Expected state 'BothSet'`);
    }
    console.log(`2. Both set - enter wins: '${result2}'`);

    console.log("PASS: System return chain (last writer wins) works correctly");
}

main();
