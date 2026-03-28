using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class StateVarBasicFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public StateVarBasicFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public StateVarBasicFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateVarBasicFrameContext {
    public StateVarBasicFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public StateVarBasicFrameContext(StateVarBasicFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class StateVarBasicCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public StateVarBasicFrameEvent forward_event;
    public StateVarBasicCompartment parent_compartment;

    public StateVarBasicCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public StateVarBasicCompartment Copy() {
        StateVarBasicCompartment c = new StateVarBasicCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateVarBasic {
    private List<StateVarBasicCompartment> _state_stack;
    private StateVarBasicCompartment __compartment;
    private StateVarBasicCompartment __next_compartment;
    private List<StateVarBasicFrameContext> _context_stack;

    public StateVarBasic() {
        _state_stack = new List<StateVarBasicCompartment>();
        _context_stack = new List<StateVarBasicFrameContext>();
        __compartment = new StateVarBasicCompartment("Counter");
        __next_compartment = null;
        StateVarBasicFrameEvent __frame_event = new StateVarBasicFrameEvent("$>");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(StateVarBasicFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateVarBasicFrameEvent exit_event = new StateVarBasicFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateVarBasicFrameEvent enter_event = new StateVarBasicFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    StateVarBasicFrameEvent enter_event = new StateVarBasicFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateVarBasicFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Counter") {
            _state_Counter(__e);
        }
    }

    private void __transition(StateVarBasicCompartment next) {
        __next_compartment = next;
    }

    public int increment() {
        StateVarBasicFrameEvent __e = new StateVarBasicFrameEvent("increment");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_count() {
        StateVarBasicFrameEvent __e = new StateVarBasicFrameEvent("get_count");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void reset() {
        StateVarBasicFrameEvent __e = new StateVarBasicFrameEvent("reset");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Counter(StateVarBasicFrameEvent __e) {
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
        } else if (__e._message == "reset") {
            __sv_comp.state_vars["count"] = 0;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 10: State Variable Basic ===");
        var s = new StateVarBasic();

        // Initial value should be 0
        var count = (int)s.get_count();
        if (count != 0) {
            throw new Exception("Expected 0, got " + count);
        }
        Console.WriteLine("Initial count: " + count);

        // Increment should return new value
        var result = (int)s.increment();
        if (result != 1) {
            throw new Exception("Expected 1 after first increment, got " + result);
        }
        Console.WriteLine("After first increment: " + result);

        // Second increment
        result = (int)s.increment();
        if (result != 2) {
            throw new Exception("Expected 2 after second increment, got " + result);
        }
        Console.WriteLine("After second increment: " + result);

        // Reset should set back to 0
        s.reset();
        count = (int)s.get_count();
        if (count != 0) {
            throw new Exception("Expected 0 after reset, got " + count);
        }
        Console.WriteLine("After reset: " + count);

        Console.WriteLine("PASS: State variable basic operations work correctly");
    }
}
