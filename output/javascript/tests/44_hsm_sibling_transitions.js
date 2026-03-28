
// Test 44: HSM Sibling Transitions
//
// Tests transitions between states sharing the same parent:
// - Exit handler fires on source sibling
// - Enter handler fires on target sibling
// - Parent relationship preserved after transition

export class HSMSiblingTransitionsFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class HSMSiblingTransitionsFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class HSMSiblingTransitionsCompartment {
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
        const c = new HSMSiblingTransitionsCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class HSMSiblingTransitions {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    log = [];

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        // HSM: Create parent compartment chain
        const __parent_comp_0 = new HSMSiblingTransitionsCompartment("Parent", null);
        this.__compartment = new HSMSiblingTransitionsCompartment("ChildA", __parent_comp_0);
        this.__next_compartment = null;
        const __frame_event = new HSMSiblingTransitionsFrameEvent("$>", null);
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
            const exit_event = new HSMSiblingTransitionsFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new HSMSiblingTransitionsFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new HSMSiblingTransitionsFrameEvent("$>", this.__compartment.enter_args);
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

    go_to_b() {
        const __e = new HSMSiblingTransitionsFrameEvent("go_to_b", null);
        const __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    go_to_a() {
        const __e = new HSMSiblingTransitionsFrameEvent("go_to_a", null);
        const __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    forward_action() {
        const __e = new HSMSiblingTransitionsFrameEvent("forward_action", null);
        const __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_log() {
        const __e = new HSMSiblingTransitionsFrameEvent("get_log", null);
        const __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_state() {
        const __e = new HSMSiblingTransitionsFrameEvent("get_state", null);
        const __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_ChildB(__e) {
        if (__e._message === "<$") {
            this.log.push("ChildB:exit")
        } else if (__e._message === "$>") {
            this.log.push("ChildB:enter")
        } else if (__e._message === "forward_action") {
            this.log.push("ChildB:forward")
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "ChildB";
            return;
        } else if (__e._message === "go_to_a") {
            this.log.push("ChildB:go_to_a")
            const __compartment = new HSMSiblingTransitionsCompartment("ChildA", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
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
        if (__e._message === "<$") {
            this.log.push("ChildA:exit")
        } else if (__e._message === "$>") {
            this.log.push("ChildA:enter")
        } else if (__e._message === "forward_action") {
            this.log.push("ChildA:forward")
            this._state_Parent(__e);
        } else if (__e._message === "get_log") {
            this._context_stack[this._context_stack.length - 1]._return = this.log;
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "ChildA";
            return;
        } else if (__e._message === "go_to_b") {
            this.log.push("ChildA:go_to_b")
            const __compartment = new HSMSiblingTransitionsCompartment("ChildB", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }
}

function main() {
    console.log("=== Test 44: HSM Sibling Transitions ===");
    const s = new HSMSiblingTransitions();

    // Initial state is ChildA with enter handler fired
    let log = s.get_log();
    if (!log.includes("ChildA:enter")) throw new Error(`Expected ChildA:enter on init, got ${JSON.stringify(log)}`);
    if (s.get_state() !== "ChildA") throw new Error(`Expected ChildA, got ${s.get_state()}`);
    console.log("TC1.4.0: Initial state ChildA with enter - PASS");

    // TC1.4.1: Transition from ChildA to ChildB
    s.go_to_b();
    if (s.get_state() !== "ChildB") throw new Error(`Expected ChildB, got ${s.get_state()}`);
    console.log("TC1.4.1: Transition A->B works - PASS");

    // TC1.4.2: Exit handler fired on source
    log = s.get_log();
    if (!log.includes("ChildA:exit")) throw new Error(`Expected ChildA:exit, got ${JSON.stringify(log)}`);
    console.log("TC1.4.2: Exit handler fires on source - PASS");

    // TC1.4.3: Enter handler fired on target
    if (!log.includes("ChildB:enter")) throw new Error(`Expected ChildB:enter, got ${JSON.stringify(log)}`);
    console.log("TC1.4.3: Enter handler fires on target - PASS");

    // TC1.4.4: Parent relationship preserved - ChildB can forward
    s.forward_action();
    log = s.get_log();
    if (!log.includes("ChildB:forward")) throw new Error(`Expected ChildB:forward, got ${JSON.stringify(log)}`);
    if (!log.includes("Parent:forward_action")) throw new Error(`Expected Parent handler, got ${JSON.stringify(log)}`);
    console.log("TC1.4.4: Parent relationship preserved - PASS");

    // TC1.4.5: Transition back to ChildA
    s.go_to_a();
    if (s.get_state() !== "ChildA") throw new Error(`Expected ChildA, got ${s.get_state()}`);
    log = s.get_log();
    const exitBCount = log.filter(x => x === "ChildB:exit").length;
    const enterACount = log.filter(x => x === "ChildA:enter").length;
    if (exitBCount !== 1) throw new Error(`Expected ChildB:exit once, got ${JSON.stringify(log)}`);
    if (enterACount !== 2) throw new Error(`Expected ChildA:enter twice, got ${JSON.stringify(log)}`);
    console.log("TC1.4.5: Transition B->A works with enter/exit - PASS");

    // TC1.4.6: ChildA can still forward after returning
    s.forward_action();
    log = s.get_log();
    if (!log.includes("ChildA:forward")) throw new Error(`Expected ChildA:forward, got ${JSON.stringify(log)}`);
    const parentCount = log.filter(x => x === "Parent:forward_action").length;
    if (parentCount !== 2) throw new Error(`Expected 2 Parent handlers, got ${JSON.stringify(log)}`);
    console.log("TC1.4.6: ChildA forwards after returning - PASS");

    console.log("PASS: HSM sibling transitions work correctly");
}

main();
