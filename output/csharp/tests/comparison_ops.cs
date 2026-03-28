using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// Test: Comparison operators in Frame handlers
// Tests: >, <, >=, <=, ==, !=

class ComparisonTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public ComparisonTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public ComparisonTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ComparisonTestFrameContext {
    public ComparisonTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public ComparisonTestFrameContext(ComparisonTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class ComparisonTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public ComparisonTestFrameEvent forward_event;
    public ComparisonTestCompartment parent_compartment;

    public ComparisonTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public ComparisonTestCompartment Copy() {
        ComparisonTestCompartment c = new ComparisonTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ComparisonTest {
    private List<ComparisonTestCompartment> _state_stack;
    private ComparisonTestCompartment __compartment;
    private ComparisonTestCompartment __next_compartment;
    private List<ComparisonTestFrameContext> _context_stack;
    public int a = 5;
    public int b = 3;

    public ComparisonTest() {
        _state_stack = new List<ComparisonTestCompartment>();
        _context_stack = new List<ComparisonTestFrameContext>();
        __compartment = new ComparisonTestCompartment("Ready");
        __next_compartment = null;
        ComparisonTestFrameEvent __frame_event = new ComparisonTestFrameEvent("$>");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(ComparisonTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ComparisonTestFrameEvent exit_event = new ComparisonTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ComparisonTestFrameEvent enter_event = new ComparisonTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    ComparisonTestFrameEvent enter_event = new ComparisonTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ComparisonTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(ComparisonTestCompartment next) {
        __next_compartment = next;
    }

    public bool test_greater() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_greater");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_less() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_less");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_greater_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_greater_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_less_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_less_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_not_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_not_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
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
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("set_values", __params);
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Ready(ComparisonTestFrameEvent __e) {
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
        } else if (__e._message == "test_greater") {
            if (this.a > this.b) {
                _context_stack[_context_stack.Count - 1]._return = true;
            } else {
                _context_stack[_context_stack.Count - 1]._return = false;
            }
        } else if (__e._message == "test_greater_equal") {
            if (this.a >= this.b) {
                _context_stack[_context_stack.Count - 1]._return = true;
            } else {
                _context_stack[_context_stack.Count - 1]._return = false;
            }
        } else if (__e._message == "test_less") {
            if (this.a < this.b) {
                _context_stack[_context_stack.Count - 1]._return = true;
            } else {
                _context_stack[_context_stack.Count - 1]._return = false;
            }
        } else if (__e._message == "test_less_equal") {
            if (this.a <= this.b) {
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
        Console.WriteLine("1..6");

        ComparisonTest s = new ComparisonTest();

        // a=5, b=3: 5 > 3 is true
        if ((bool) s.test_greater()) {
            Console.WriteLine("ok 1 - 5 > 3 is true");
        } else {
            Console.WriteLine("not ok 1 - 5 > 3 is true");
        }

        // a=5, b=3: 5 < 3 is false
        if (!(bool) s.test_less()) {
            Console.WriteLine("ok 2 - 5 < 3 is false");
        } else {
            Console.WriteLine("not ok 2 - 5 < 3 is false");
        }

        // a=5, b=3: 5 >= 3 is true
        if ((bool) s.test_greater_equal()) {
            Console.WriteLine("ok 3 - 5 >= 3 is true");
        } else {
            Console.WriteLine("not ok 3 - 5 >= 3 is true");
        }

        // a=5, b=3: 5 <= 3 is false
        if (!(bool) s.test_less_equal()) {
            Console.WriteLine("ok 4 - 5 <= 3 is false");
        } else {
            Console.WriteLine("not ok 4 - 5 <= 3 is false");
        }

        // a=5, b=3: 5 == 3 is false
        if (!(bool) s.test_equal()) {
            Console.WriteLine("ok 5 - 5 == 3 is false");
        } else {
            Console.WriteLine("not ok 5 - 5 == 3 is false");
        }

        // a=5, b=3: 5 != 3 is true
        if ((bool) s.test_not_equal()) {
            Console.WriteLine("ok 6 - 5 != 3 is true");
        } else {
            Console.WriteLine("not ok 6 - 5 != 3 is true");
        }
    }
}
