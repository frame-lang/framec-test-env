using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// Test: Ternary/conditional expressions in Frame handlers
// C# uses: cond ? a : b

class TernaryTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public TernaryTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public TernaryTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TernaryTestFrameContext {
    public TernaryTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public TernaryTestFrameContext(TernaryTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class TernaryTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public TernaryTestFrameEvent forward_event;
    public TernaryTestCompartment parent_compartment;

    public TernaryTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public TernaryTestCompartment Copy() {
        TernaryTestCompartment c = new TernaryTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TernaryTest {
    private List<TernaryTestCompartment> _state_stack;
    private TernaryTestCompartment __compartment;
    private TernaryTestCompartment __next_compartment;
    private List<TernaryTestFrameContext> _context_stack;
    public bool cond = true;

    public TernaryTest() {
        _state_stack = new List<TernaryTestCompartment>();
        _context_stack = new List<TernaryTestFrameContext>();
        __compartment = new TernaryTestCompartment("Ready");
        __next_compartment = null;
        TernaryTestFrameEvent __frame_event = new TernaryTestFrameEvent("$>");
        TernaryTestFrameContext __ctx = new TernaryTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(TernaryTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TernaryTestFrameEvent exit_event = new TernaryTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TernaryTestFrameEvent enter_event = new TernaryTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    TernaryTestFrameEvent enter_event = new TernaryTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TernaryTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(TernaryTestCompartment next) {
        __next_compartment = next;
    }

    public int get_value() {
        TernaryTestFrameEvent __e = new TernaryTestFrameEvent("get_value");
        TernaryTestFrameContext __ctx = new TernaryTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void set_condition(bool c) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["c"] = c;
        TernaryTestFrameEvent __e = new TernaryTestFrameEvent("set_condition", __params);
        TernaryTestFrameContext __ctx = new TernaryTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Ready(TernaryTestFrameEvent __e) {
        if (__e._message == "get_value") {
            int result = this.cond ? 100 : 200;
            _context_stack[_context_stack.Count - 1]._return = result;
        } else if (__e._message == "set_condition") {
            var c = (bool) __e._parameters["c"];
            this.cond = c;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..2");

        TernaryTest s = new TernaryTest();

        // cond=true: should return 100
        int v1 = (int) s.get_value();
        if (v1 == 100) {
            Console.WriteLine("ok 1 - cond=true returns 100");
        } else {
            Console.WriteLine("not ok 1 - cond=true returns 100 # got " + v1);
        }

        // cond=false: should return 200
        s.set_condition(false);
        int v2 = (int) s.get_value();
        if (v2 == 200) {
            Console.WriteLine("ok 2 - cond=false returns 200");
        } else {
            Console.WriteLine("not ok 2 - cond=false returns 200 # got " + v2);
        }
    }
}
