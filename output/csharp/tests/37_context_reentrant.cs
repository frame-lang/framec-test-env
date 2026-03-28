using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class ContextReentrantTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public ContextReentrantTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public ContextReentrantTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ContextReentrantTestFrameContext {
    public ContextReentrantTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public ContextReentrantTestFrameContext(ContextReentrantTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class ContextReentrantTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public ContextReentrantTestFrameEvent forward_event;
    public ContextReentrantTestCompartment parent_compartment;

    public ContextReentrantTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public ContextReentrantTestCompartment Copy() {
        ContextReentrantTestCompartment c = new ContextReentrantTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ContextReentrantTest {
    private List<ContextReentrantTestCompartment> _state_stack;
    private ContextReentrantTestCompartment __compartment;
    private ContextReentrantTestCompartment __next_compartment;
    private List<ContextReentrantTestFrameContext> _context_stack;

    public ContextReentrantTest() {
        _state_stack = new List<ContextReentrantTestCompartment>();
        _context_stack = new List<ContextReentrantTestFrameContext>();
        __compartment = new ContextReentrantTestCompartment("Ready");
        __next_compartment = null;
        ContextReentrantTestFrameEvent __frame_event = new ContextReentrantTestFrameEvent("$>");
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(ContextReentrantTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ContextReentrantTestFrameEvent exit_event = new ContextReentrantTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ContextReentrantTestFrameEvent enter_event = new ContextReentrantTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    ContextReentrantTestFrameEvent enter_event = new ContextReentrantTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ContextReentrantTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(ContextReentrantTestCompartment next) {
        __next_compartment = next;
    }

    public string outer(int x) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["x"] = x;
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("outer", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string inner(int y) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["y"] = y;
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("inner", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string deeply_nested(int z) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["z"] = z;
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("deeply_nested", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_both(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("get_both", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Ready(ContextReentrantTestFrameEvent __e) {
        if (__e._message == "deeply_nested") {
            var z = (int) __e._parameters["z"];
            // 3 levels deep
            string outer_result = this.outer(z);
            _context_stack[_context_stack.Count - 1]._return = "deep:" + z + "," + outer_result;
        } else if (__e._message == "get_both") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            // Test that we can access multiple params
            string result_a = this.inner(a);
            string result_b = this.inner(b);
            // After both inner calls, @@.a and @@.b should still be our params
            _context_stack[_context_stack.Count - 1]._return = "a=" + a + ",b=" + b + ",results=" + result_a + "+" + result_b;
        } else if (__e._message == "inner") {
            var y = (int) __e._parameters["y"];
            // Inner has its own context
            // @@.y should be inner's param, not outer's
            _context_stack[_context_stack.Count - 1]._return = y.ToString();
        } else if (__e._message == "outer") {
            var x = (int) __e._parameters["x"];
            // Set our return before calling inner
            _context_stack[_context_stack.Count - 1]._return = "outer_initial";

            // Call inner - should NOT clobber our return
            string inner_result = this.inner(x * 10);

            // Our return should still be accessible
            // Update it with combined result
            _context_stack[_context_stack.Count - 1]._return = "outer:" + x + ",inner:" + inner_result;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 37: Context Reentrant ===");
        var s = new ContextReentrantTest();

        // Test 1: Simple nesting - outer calls inner
        var result = (string)s.outer(5);
        var expected = "outer:5,inner:50";
        if (result != expected) {
            Console.WriteLine("FAIL: Expected '" + expected + "', got '" + result + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("1. outer(5) = '" + result + "'");

        // Test 2: Inner alone
        result = (string)s.inner(42);
        if (result != "42") {
            Console.WriteLine("FAIL: Expected '42', got '" + result + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("2. inner(42) = '" + result + "'");

        // Test 3: Deep nesting (3 levels)
        result = (string)s.deeply_nested(3);
        expected = "deep:3,outer:3,inner:30";
        if (result != expected) {
            Console.WriteLine("FAIL: Expected '" + expected + "', got '" + result + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("3. deeply_nested(3) = '" + result + "'");

        // Test 4: Multiple inner calls, params preserved
        result = (string)s.get_both(10, 20);
        expected = "a=10,b=20,results=10+20";
        if (result != expected) {
            Console.WriteLine("FAIL: Expected '" + expected + "', got '" + result + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("4. get_both(10, 20) = '" + result + "'");

        Console.WriteLine("PASS: Context reentrant works correctly");
    }
}
