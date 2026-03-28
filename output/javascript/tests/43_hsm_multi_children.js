
// Test 43: HSM Multiple Children of Same Parent
//
// Tests multiple states sharing the same parent:
// - $ChildA => $Parent
// - $ChildB => $Parent
// - $ChildC => $Parent
// Each child can forward to the shared parent

export class HSMMultiChildrenFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMMultiChildrenFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMMultiChildrenCompartment {
    state;
    state_args;
    state_vars;
    enter_args;
    exit_args;
    forward_event;
    parent_compartment;

    constructor(state, parent_compartment = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    copy() {
        const c = new HSMMultiChildrenCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMMultiChildren {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMMultiChildrenCompartment("Parent", null);
        this.__compartment = new HSMMultiChildrenCompartment("ChildA", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMMultiChildrenFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    __kernel(__e) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new HSMMultiChildrenFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMMultiChildrenFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMMultiChildrenFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    __router(__e) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = this[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    __transition(next_compartment) {
        this.__next_compartment = next_compartment;
    }

    start_a() {
        const __e = new HSMMultiChildrenFrameEvent("start_a", null);
        const __ctx = new HSMMultiChildrenFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    start_b() {
        const __e = new HSMMultiChildrenFrameEvent("start_b", null);
        const __ctx = new HSMMultiChildrenFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    start_c() {
        const __e = new HSMMultiChildrenFrameEvent("start_c", null);
        const __ctx = new HSMMultiChildrenFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    do_action() {
        const __e = new HSMMultiChildrenFrameEvent("do_action", null);
        const __ctx = new HSMMultiChildrenFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forward_action() {
        const __e = new HSMMultiChildrenFrameEvent("forward_action", null);
        const __ctx = new HSMMultiChildrenFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMMultiChildrenFrameEvent("get_log", null);
        const __ctx = new HSMMultiChildrenFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMMultiChildrenFrameEvent("get_state", null);
        const __ctx = new HSMMultiChildrenFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Parent(__e) {
        if (__e._message === "forward_action") {
            this.log.push("Parent:forward_action")
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Parent";
            return;
        }
    }

    _state_ChildA(__e) {
        if (__e._message === "do_action") {
            this.log.push("ChildA:do_action")
        } else if (__e._message === "forward_action") {
            this.log.push("ChildA:forward_action")
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "ChildA";
            return;
        } else if (__e._message === "start_a") {
            // stay
        } else if (__e._message === "start_b") {
            const __compartment = new HSMMultiChildrenCompartment("ChildB", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "start_c") {
            const __compartment = new HSMMultiChildrenCompartment("ChildC", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_ChildB(__e) {
        if (__e._message === "do_action") {
            this.log.push("ChildB:do_action")
        } else if (__e._message === "forward_action") {
            this.log.push("ChildB:forward_action")
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "ChildB";
            return;
        } else if (__e._message === "start_a") {
            const __compartment = new HSMMultiChildrenCompartment("ChildA", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "start_b") {
            // stay
        } else if (__e._message === "start_c") {
            const __compartment = new HSMMultiChildrenCompartment("ChildC", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_ChildC(__e) {
        if (__e._message === "do_action") {
            this.log.push("ChildC:do_action")
        } else if (__e._message === "forward_action") {
            this.log.push("ChildC:forward_action")
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "ChildC";
            return;
        } else if (__e._message === "start_a") {
            const __compartment = new HSMMultiChildrenCompartment("ChildA", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "start_b") {
            const __compartment = new HSMMultiChildrenCompartment("ChildB", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "start_c") {
            // stay
        }
    }
}

function main() {
    console.log("=== Test 43: HSM Multiple Children ===");
    const s = new HSMMultiChildren();

    // TC1.3.1: Multiple children declare same parent (verified by compilation)
    console.log("TC1.3.1: Multiple children with same parent compiles - PASS");

    // Start in ChildA
    if (s.get_state() !== "ChildA") throw new Error(`Expected ChildA, got ${s.get_state()}`);

    // TC1.3.2: ChildA can forward to shared parent
    s.forward_action();
    let log = s.get_log();
    if (!log.includes("ChildA:forward_action")) throw new Error(`Expected ChildA forward, got ${JSON.stringify(log)}`);
    if (!log.includes("Parent:forward_action")) throw new Error(`Expected Parent handler, got ${JSON.stringify(log)}`);
    console.log("TC1.3.2: ChildA forwards to parent - PASS");

    // TC1.3.3: Transition to sibling
    s.start_b();
    if (s.get_state() !== "ChildB") throw new Error(`Expected ChildB after transition, got ${s.get_state()}`);
    console.log("TC1.3.3: Transition A->B works - PASS");

    // TC1.3.4: ChildB can also forward to same parent
    s.forward_action();
    log = s.get_log();
    if (!log.includes("ChildB:forward_action")) throw new Error(`Expected ChildB forward, got ${JSON.stringify(log)}`);
    const parentCount = log.filter(x => x === "Parent:forward_action").length;
    if (parentCount !== 2) throw new Error(`Expected 2 Parent forwards, got ${JSON.stringify(log)}`);
    console.log("TC1.3.4: ChildB forwards to same parent - PASS");

    // TC1.3.5: Transition to ChildC
    s.start_c();
    if (s.get_state() !== "ChildC") throw new Error(`Expected ChildC, got ${s.get_state()}`);
    s.forward_action();
    log = s.get_log();
    if (!log.includes("ChildC:forward_action")) throw new Error(`Expected ChildC forward, got ${JSON.stringify(log)}`);
    const parentCount2 = log.filter(x => x === "Parent:forward_action").length;
    if (parentCount2 !== 3) throw new Error(`Expected 3 Parent forwards, got ${JSON.stringify(log)}`);
    console.log("TC1.3.5: ChildC forwards to same parent - PASS");

    // TC1.3.6: Each sibling maintains independent actions
    s.start_a();
    s.do_action();
    s.start_b();
    s.do_action();
    s.start_c();
    s.do_action();
    log = s.get_log();
    if (!log.includes("ChildA:do_action")) throw new Error("Expected ChildA action");
    if (!log.includes("ChildB:do_action")) throw new Error("Expected ChildB action");
    if (!log.includes("ChildC:do_action")) throw new Error("Expected ChildC action");
    console.log("TC1.3.6: Each sibling has independent handlers - PASS");

    console.log("PASS: HSM multiple children work correctly");
}

main();
