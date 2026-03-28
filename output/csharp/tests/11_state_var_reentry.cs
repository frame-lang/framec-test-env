using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class StateVarReentryFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public StateVarReentryFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public StateVarReentryFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateVarReentryFrameContext {
    public StateVarReentryFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public StateVarReentryFrameContext(StateVarReentryFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class StateVarReentryCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public StateVarReentryFrameEvent forward_event;
    public StateVarReentryCompartment parent_compartment;

    public StateVarReentryCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public StateVarReentryCompartment Copy() {
        StateVarReentryCompartment c = new StateVarReentryCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateVarReentry {
    private List<StateVarReentryCompartment> _state_stack;
    private StateVarReentryCompartment __compartment;
    private StateVarReentryCompartment __next_compartment;
    private List<StateVarReentryFrameContext> _context_stack;

    public StateVarReentry() {
        _state_stack = new List<StateVarReentryCompartment>();
        _context_stack = new List<StateVarReentryFrameContext>();
        __compartment = new StateVarReentryCompartment("Counter");
        __next_compartment = null;
        StateVarReentryFrameEvent __frame_event = new StateVarReentryFrameEvent("$>");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(StateVarReentryFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateVarReentryFrameEvent exit_event = new StateVarReentryFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateVarReentryFrameEvent enter_event = new StateVarReentryFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    StateVarReentryFrameEvent enter_event = new StateVarReentryFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateVarReentryFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Counter") {
            _state_Counter(__e);
        } else if (state_name == "Other") {
            _state_Other(__e);
        }
    }

    private void __transition(StateVarReentryCompartment next) {
        __next_compartment = next;
    }

    public int increment() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("increment");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_count() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("get_count");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void go_other() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("go_other");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void come_back() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("come_back");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Other(StateVarReentryFrameEvent __e) {
        if (__e._message == "come_back") {
            { var __new_compartment = new StateVarReentryCompartment("Counter");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = -1;
            return;
        } else if (__e._message == "increment") {
            _context_stack[_context_stack.Count - 1]._return = -1;
            return;
        }
    }

    private void _state_Counter(StateVarReentryFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Counter") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("count")) {
                __sv_comp.state_vars["count"] = 0;
            }
        } else if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["count"];
            return;
        } else if (__e._message == "go_other") {
            { var __new_compartment = new StateVarReentryCompartment("Other");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "increment") {
            __sv_comp.state_vars["count"] = (int) __sv_comp.state_vars["count"] + 1;
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["count"];
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 11: State Variable Reentry ===");
        var s = new StateVarReentry();

        // Increment a few times
        s.increment();
        s.increment();
        var count = (int)s.get_count();
        if (count != 2) {
            throw new Exception("Expected 2 after two increments, got " + count);
        }
        Console.WriteLine("Count before leaving: " + count);

        // Leave the state
        s.go_other();
        Console.WriteLine("Transitioned to Other state");

        // Come back - state var should be reinitialized to 0
        s.come_back();
        count = (int)s.get_count();
        if (count != 0) {
            throw new Exception("Expected 0 after re-entering Counter (state var reinit), got " + count);
        }
        Console.WriteLine("Count after re-entering Counter: " + count);

        // Increment again to verify it works
        var result = (int)s.increment();
        if (result != 1) {
            throw new Exception("Expected 1 after increment, got " + result);
        }
        Console.WriteLine("After increment: " + result);

        Console.WriteLine("PASS: State variables reinitialize on state reentry");
    }
}
