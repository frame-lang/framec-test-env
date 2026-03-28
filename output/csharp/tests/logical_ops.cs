using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// Test: Logical operators in Frame handlers
// Tests: &&, ||, !

class LogicalTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public LogicalTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public LogicalTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class LogicalTestFrameContext {
    public LogicalTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public LogicalTestFrameContext(LogicalTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class LogicalTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public LogicalTestFrameEvent forward_event;
    public LogicalTestCompartment parent_compartment;

    public LogicalTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public LogicalTestCompartment Copy() {
        LogicalTestCompartment c = new LogicalTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class LogicalTest {
    private List<LogicalTestCompartment> _state_stack;
    private LogicalTestCompartment __compartment;
    private LogicalTestCompartment __next_compartment;
    private List<LogicalTestFrameContext> _context_stack;
    public bool a = true;
    public bool b = false;

    public LogicalTest() {
        _state_stack = new List<LogicalTestCompartment>();
        _context_stack = new List<LogicalTestFrameContext>();
        __compartment = new LogicalTestCompartment("Ready");
        __next_compartment = null;
        LogicalTestFrameEvent __frame_event = new LogicalTestFrameEvent("$>");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(LogicalTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            LogicalTestFrameEvent exit_event = new LogicalTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                LogicalTestFrameEvent enter_event = new LogicalTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    LogicalTestFrameEvent enter_event = new LogicalTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(LogicalTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(LogicalTestCompartment next) {
        __next_compartment = next;
    }

    public bool test_and() {
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("test_and");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_or() {
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("test_or");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool test_not() {
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("test_not");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void set_values(bool x, bool y) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["x"] = x;
        __params["y"] = y;
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("set_values", __params);
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Ready(LogicalTestFrameEvent __e) {
        if (__e._message == "set_values") {
            var x = (bool) __e._parameters["x"];
            var y = (bool) __e._parameters["y"];
            this.a = x;
            this.b = y;
        } else if (__e._message == "test_and") {
            if (this.a && this.b) {
                _context_stack[_context_stack.Count - 1]._return = true;
            } else {
                _context_stack[_context_stack.Count - 1]._return = false;
            }
        } else if (__e._message == "test_not") {
            if (!this.a) {
                _context_stack[_context_stack.Count - 1]._return = true;
            } else {
                _context_stack[_context_stack.Count - 1]._return = false;
            }
        } else if (__e._message == "test_or") {
            if (this.a || this.b) {
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

        LogicalTest s = new LogicalTest();

        // a=true, b=false: true && false = false
        if (!(bool) s.test_and()) {
            Console.WriteLine("ok 1 - true && false is false");
        } else {
            Console.WriteLine("not ok 1 - true && false is false");
        }

        // a=true, b=false: true || false = true
        if ((bool) s.test_or()) {
            Console.WriteLine("ok 2 - true || false is true");
        } else {
            Console.WriteLine("not ok 2 - true || false is true");
        }

        // a=true: !true = false
        if (!(bool) s.test_not()) {
            Console.WriteLine("ok 3 - !true is false");
        } else {
            Console.WriteLine("not ok 3 - !true is false");
        }

        // Change values: a=true, b=true
        s.set_values(true, true);

        // true && true = true
        if ((bool) s.test_and()) {
            Console.WriteLine("ok 4 - true && true is true");
        } else {
            Console.WriteLine("not ok 4 - true && true is true");
        }

        // Change values: a=false, b=false
        s.set_values(false, false);

        // false || false = false
        if (!(bool) s.test_or()) {
            Console.WriteLine("ok 5 - false || false is false");
        } else {
            Console.WriteLine("not ok 5 - false || false is false");
        }

        // !false = true
        if ((bool) s.test_not()) {
            Console.WriteLine("ok 6 - !false is true");
        } else {
            Console.WriteLine("not ok 6 - !false is true");
        }
    }
}
