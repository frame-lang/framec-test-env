
export class PersistStackFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class PersistStackFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class PersistStackCompartment {
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
        const c = new PersistStackCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class PersistStack {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    depth = 0;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new PersistStackCompartment("Start");
        this.__next_compartment = null;
        const __frame_event = new PersistStackFrameEvent("$>", null);
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
            const exit_event = new PersistStackFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new PersistStackFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new PersistStackFrameEvent("$>", this.__compartment.enter_args);
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

    push_and_go() {
        const __e = new PersistStackFrameEvent("push_and_go", null);
        const __ctx = new PersistStackFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    pop_back() {
        const __e = new PersistStackFrameEvent("pop_back", null);
        const __ctx = new PersistStackFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_state() {
        const __e = new PersistStackFrameEvent("get_state", null);
        const __ctx = new PersistStackFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_depth() {
        const __e = new PersistStackFrameEvent("get_depth", null);
        const __ctx = new PersistStackFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_End(__e) {
        if (__e._message === "get_depth") {
            this._context_stack[this._context_stack.length - 1]._return = this.depth;
            return;;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "end";
            return;;
        } else if (__e._message === "pop_back") {
            this.depth = this.depth - 1;
            this.__transition(this._state_stack.pop());
            return;
        } else if (__e._message === "push_and_go") {
            // cannot go further
        }
    }

    _state_Start(__e) {
        if (__e._message === "get_depth") {
            this._context_stack[this._context_stack.length - 1]._return = this.depth;
            return;;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "start";
            return;;
        } else if (__e._message === "pop_back") {
            // nothing to pop
        } else if (__e._message === "push_and_go") {
            this.depth = this.depth + 1;
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new PersistStackCompartment("Middle", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Middle(__e) {
        if (__e._message === "get_depth") {
            this._context_stack[this._context_stack.length - 1]._return = this.depth;
            return;;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "middle";
            return;;
        } else if (__e._message === "pop_back") {
            this.depth = this.depth - 1;
            this.__transition(this._state_stack.pop());
            return;
        } else if (__e._message === "push_and_go") {
            this.depth = this.depth + 1;
            this._state_stack.push(this.__compartment.copy());
            const __compartment = new PersistStackCompartment("End", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    saveState() {
        const serializeComp = (c) => {
            if (!c) return null;
            return {
                state: c.state,
                state_args: {...c.state_args},
                state_vars: {...c.state_vars},
                enter_args: {...c.enter_args},
                exit_args: {...c.exit_args},
                forward_event: c.forward_event,
                parent_compartment: serializeComp(c.parent_compartment),
            };
        };
        return JSON.stringify({
            _compartment: serializeComp(this.__compartment),
            _state_stack: this._state_stack.map((c) => serializeComp(c)),
            depth: this.depth,
        });
    }

    static restoreState(json) {
        const deserializeComp = (data) => {
            if (!data) return null;
            const comp = new PersistStackCompartment(data.state);
            comp.state_args = {...(data.state_args || {})};
            comp.state_vars = {...(data.state_vars || {})};
            comp.enter_args = {...(data.enter_args || {})};
            comp.exit_args = {...(data.exit_args || {})};
            comp.forward_event = data.forward_event;
            comp.parent_compartment = deserializeComp(data.parent_compartment);
            return comp;
        };
        const data = JSON.parse(json);
        const instance = Object.create(PersistStack.prototype);
        instance.__compartment = deserializeComp(data._compartment);
        instance.__next_compartment = null;
        instance._state_stack = (data._state_stack || []).map((c) => deserializeComp(c));
        instance._context_stack = [];
        instance.depth = data.depth;
        return instance;
    }
}

function main() {
    console.log("=== Test 25: Persist Stack (JavaScript) ===");

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
    const json = s1.saveState();
    const data = JSON.parse(json);
    console.log(`2. Saved data: ${json}`);
    console.assert(data._compartment.state === 'End', `Expected End state`);
    console.assert(data._state_stack !== undefined, "Expected _state_stack in saved data");
    console.assert(data._state_stack.length === 2, `Expected 2 items in stack, got ${data._state_stack.length}`);

    // Test 3: Restore and verify stack works
    const s2 = PersistStack.restoreState(json);
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
