using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class StateParamsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public StateParamsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public StateParamsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateParamsFrameContext {
    public StateParamsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public StateParamsFrameContext(StateParamsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class StateParamsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public StateParamsFrameEvent forward_event;
    public StateParamsCompartment parent_compartment;

    public StateParamsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public StateParamsCompartment Copy() {
        StateParamsCompartment c = new StateParamsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateParams {
    private List<StateParamsCompartment> _state_stack;
    private StateParamsCompartment __compartment;
    private StateParamsCompartment __next_compartment;
    private List<StateParamsFrameContext> _context_stack;

    public StateParams() {
        _state_stack = new List<StateParamsCompartment>();
        _context_stack = new List<StateParamsFrameContext>();
        __compartment = new StateParamsCompartment("Idle");
        __next_compartment = null;
        StateParamsFrameEvent __frame_event = new StateParamsFrameEvent("$>");
        StateParamsFrameContext __ctx = new StateParamsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(StateParamsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateParamsFrameEvent exit_event = new StateParamsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateParamsFrameEvent enter_event = new StateParamsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    StateParamsFrameEvent enter_event = new StateParamsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateParamsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Counter") {
            _state_Counter(__e);
        }
    }

    private void __transition(StateParamsCompartment next) {
        __next_compartment = next;
    }

    public void start(int val) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["val"] = val;
        StateParamsFrameEvent __e = new StateParamsFrameEvent("start", __params);
        StateParamsFrameContext __ctx = new StateParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int get_value() {
        StateParamsFrameEvent __e = new StateParamsFrameEvent("get_value");
        StateParamsFrameContext __ctx = new StateParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Idle(StateParamsFrameEvent __e) {
        if (__e._message == "get_value") {
            _context_stack[_context_stack.Count - 1]._return = 0;
            return;
        } else if (__e._message == "start") {
            var val = (int) __e._parameters["val"];
            { var __new_compartment = new StateParamsCompartment("Counter");
            __new_compartment.parent_compartment = __compartment.Copy();
            __new_compartment.state_args["0"] = val;
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Counter(StateParamsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Counter") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("count")) {
                __sv_comp.state_vars["count"] = 0;
            }
            // Access state param via compartment - using string key "0"
            __sv_comp.state_vars["count"] = this.__compartment.state_args["0"];
            int count_val = (int) __sv_comp.state_vars["count"];
            Console.WriteLine("Counter entered with initial=" + count_val);
        } else if (__e._message == "get_value") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["count"];
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 26: State Parameters ===");
        var s = new StateParams();

        var val = (int)s.get_value();
        if (val != 0) {
            Console.WriteLine("FAIL: Expected 0 in Idle, got " + val);
            Environment.Exit(1);
        }
        Console.WriteLine("Initial value: " + val);

        s.start(42);
        val = (int)s.get_value();
        if (val != 42) {
            Console.WriteLine("FAIL: Expected 42 in Counter from state param, got " + val);
            Environment.Exit(1);
        }
        Console.WriteLine("Value after transition: " + val);

        Console.WriteLine("PASS: State parameters work correctly");
    }
}
