using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class StateVarPushPopFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public StateVarPushPopFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public StateVarPushPopFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateVarPushPopFrameContext {
    public StateVarPushPopFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public StateVarPushPopFrameContext(StateVarPushPopFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class StateVarPushPopCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public StateVarPushPopFrameEvent forward_event;
    public StateVarPushPopCompartment parent_compartment;

    public StateVarPushPopCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public StateVarPushPopCompartment Copy() {
        StateVarPushPopCompartment c = new StateVarPushPopCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateVarPushPop {
    private List<StateVarPushPopCompartment> _state_stack;
    private StateVarPushPopCompartment __compartment;
    private StateVarPushPopCompartment __next_compartment;
    private List<StateVarPushPopFrameContext> _context_stack;

    public StateVarPushPop() {
        _state_stack = new List<StateVarPushPopCompartment>();
        _context_stack = new List<StateVarPushPopFrameContext>();
        __compartment = new StateVarPushPopCompartment("Counter");
        __next_compartment = null;
        StateVarPushPopFrameEvent __frame_event = new StateVarPushPopFrameEvent("$>");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(StateVarPushPopFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateVarPushPopFrameEvent exit_event = new StateVarPushPopFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateVarPushPopFrameEvent enter_event = new StateVarPushPopFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    StateVarPushPopFrameEvent enter_event = new StateVarPushPopFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateVarPushPopFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Counter") {
            _state_Counter(__e);
        } else if (state_name == "Other") {
            _state_Other(__e);
        }
    }

    private void __transition(StateVarPushPopCompartment next) {
        __next_compartment = next;
    }

    public int increment() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("increment");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_count() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("get_count");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void save_and_go() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("save_and_go");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void restore() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("restore");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Other(StateVarPushPopFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Other") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("other_count")) {
                __sv_comp.state_vars["other_count"] = 100;
            }
        } else if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["other_count"];
            return;
        } else if (__e._message == "increment") {
            __sv_comp.state_vars["other_count"] = (int) __sv_comp.state_vars["other_count"] + 1;
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["other_count"];
            return;
        } else if (__e._message == "restore") {
            var __popped = _state_stack[_state_stack.Count - 1]; _state_stack.RemoveAt(_state_stack.Count - 1);
            __transition(__popped);
            return;
        }
    }

    private void _state_Counter(StateVarPushPopFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Counter") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("count")) {
                __sv_comp.state_vars["count"] = 0;
            }
        } else if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["count"];
            return;
        } else if (__e._message == "increment") {
            __sv_comp.state_vars["count"] = (int) __sv_comp.state_vars["count"] + 1;
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["count"];
            return;
        } else if (__e._message == "save_and_go") {
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new StateVarPushPopCompartment("Other");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 12: State Variable Push/Pop ===");
        var s = new StateVarPushPop();

        // Increment counter to 3
        s.increment();
        s.increment();
        s.increment();
        var count = (int)s.get_count();
        if (count != 3) {
            throw new Exception("Expected 3, got " + count);
        }
        Console.WriteLine("Counter before push: " + count);

        // Push and go to Other state
        s.save_and_go();
        Console.WriteLine("Pushed and transitioned to Other");

        // In Other state, count should be 100 (Other's state var)
        count = (int)s.get_count();
        if (count != 100) {
            throw new Exception("Expected 100 in Other state, got " + count);
        }
        Console.WriteLine("Other state count: " + count);

        // Increment in Other
        s.increment();
        count = (int)s.get_count();
        if (count != 101) {
            throw new Exception("Expected 101 after increment, got " + count);
        }
        Console.WriteLine("Other state after increment: " + count);

        // Pop back - should restore Counter with count=3
        s.restore();
        Console.WriteLine("Popped back to Counter");

        count = (int)s.get_count();
        if (count != 3) {
            throw new Exception("Expected 3 after pop (preserved), got " + count);
        }
        Console.WriteLine("Counter after pop: " + count);

        // Increment to verify it works
        s.increment();
        count = (int)s.get_count();
        if (count != 4) {
            throw new Exception("Expected 4, got " + count);
        }
        Console.WriteLine("Counter after increment: " + count);

        Console.WriteLine("PASS: State variables preserved across push/pop");
    }
}
