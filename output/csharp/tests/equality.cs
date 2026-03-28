using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// Test: Equality operators in Frame handlers
// Tests: ==, !=

class EqualityTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public EqualityTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public EqualityTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class EqualityTestFrameContext {
    public EqualityTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public EqualityTestFrameContext(EqualityTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class EqualityTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public EqualityTestFrameEvent forward_event;
    public EqualityTestCompartment parent_compartment;

    public EqualityTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public EqualityTestCompartment Copy() {
        EqualityTestCompartment c = new EqualityTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class EqualityTest {
    private List<EqualityTestCompartment> _state_stack;
    private EqualityTestCompartment __compartment;
    private EqualityTestCompartment __next_compartment;
    private List<EqualityTestFrameContext> _context_stack;
    public int a = 5;
    public int b = 5;

    public EqualityTest() {
        _state_stack = new List<EqualityTestCompartment>();
        _context_stack = new List<EqualityTestFrameContext>();
        __compartment = new EqualityTestCompartment("Ready");
        __next_compartment = null;
        EqualityTestFrameEvent __frame_event = new EqualityTestFrameEvent("$>");
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(EqualityTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            EqualityTestFrameEvent exit_event = new EqualityTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                EqualityTestFrameEvent enter_event = new EqualityTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    EqualityTestFrameEvent enter_event = new EqualityTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(EqualityTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(EqualityTestCompartment next) {
        __next_compartment = next;
    }

    public bool test_equal() {
        EqualityTestFrameEvent __e = new EqualityTestFrameEvent("test_equal");
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_not_equal() {
        EqualityTestFrameEvent __e = new EqualityTestFrameEvent("test_not_equal");
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void set_values(int x, int y) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["x"] = x;
        __params["y"] = y;
        EqualityTestFrameEvent __e = new EqualityTestFrameEvent("set_values", __params);
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Ready(EqualityTestFrameEvent __e) {
        if (__e._message == "set_values") {
            var x = (int) __e._parameters["x"];
            var y = (int) __e._parameters["y"];
            this.a = x;
            this.b = y;
        } else if (__e._message == "test_equal") {
            if (this.a == this.b) {
                _context_stack[_context_stack.Count - 1]._return = true;
            } else {
                _context_stack[_context_stack.Count - 1]._return = false;
            }
        } else if (__e._message == "test_not_equal") {
            if (this.a != this.b) {
                _context_stack[_context_stack.Count - 1]._return = true;
            } else {
                _context_stack[_context_stack.Count - 1]._return = false;
            }
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..4");

        EqualityTest s = new EqualityTest();

        // a=5, b=5: 5 == 5 is true
        if ((bool) s.test_equal()) {
            Console.WriteLine("ok 1 - 5 == 5 is true");
        } else {
            Console.WriteLine("not ok 1 - 5 == 5 is true");
        }

        // a=5, b=5: 5 != 5 is false
        if (!(bool) s.test_not_equal()) {
            Console.WriteLine("ok 2 - 5 != 5 is false");
        } else {
            Console.WriteLine("not ok 2 - 5 != 5 is false");
        }

        // Change values: a=5, b=3
        s.set_values(5, 3);

        // a=5, b=3: 5 == 3 is false
        if (!(bool) s.test_equal()) {
            Console.WriteLine("ok 3 - 5 == 3 is false");
        } else {
            Console.WriteLine("not ok 3 - 5 == 3 is false");
        }

        // a=5, b=3: 5 != 3 is true
        if ((bool) s.test_not_equal()) {
            Console.WriteLine("ok 4 - 5 != 3 is true");
        } else {
            Console.WriteLine("not ok 4 - 5 != 3 is true");
        }
    }
}
