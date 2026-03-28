using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class ContextBasicTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public ContextBasicTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public ContextBasicTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ContextBasicTestFrameContext {
    public ContextBasicTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public ContextBasicTestFrameContext(ContextBasicTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class ContextBasicTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public ContextBasicTestFrameEvent forward_event;
    public ContextBasicTestCompartment parent_compartment;

    public ContextBasicTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public ContextBasicTestCompartment Copy() {
        ContextBasicTestCompartment c = new ContextBasicTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ContextBasicTest {
    private List<ContextBasicTestCompartment> _state_stack;
    private ContextBasicTestCompartment __compartment;
    private ContextBasicTestCompartment __next_compartment;
    private List<ContextBasicTestFrameContext> _context_stack;

    public ContextBasicTest() {
        _state_stack = new List<ContextBasicTestCompartment>();
        _context_stack = new List<ContextBasicTestFrameContext>();
        __compartment = new ContextBasicTestCompartment("Ready");
        __next_compartment = null;
        ContextBasicTestFrameEvent __frame_event = new ContextBasicTestFrameEvent("$>");
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(ContextBasicTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ContextBasicTestFrameEvent exit_event = new ContextBasicTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ContextBasicTestFrameEvent enter_event = new ContextBasicTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    ContextBasicTestFrameEvent enter_event = new ContextBasicTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ContextBasicTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(ContextBasicTestCompartment next) {
        __next_compartment = next;
    }

    public int add(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        ContextBasicTestFrameEvent __e = new ContextBasicTestFrameEvent("add", __params);
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_event_name() {
        ContextBasicTestFrameEvent __e = new ContextBasicTestFrameEvent("get_event_name");
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string greet(string name) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["name"] = name;
        ContextBasicTestFrameEvent __e = new ContextBasicTestFrameEvent("greet", __params);
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Ready(ContextBasicTestFrameEvent __e) {
        if (__e._message == "add") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            // Access params via @@ shorthand
            _context_stack[_context_stack.Count - 1]._return = a + b;
        } else if (__e._message == "get_event_name") {
            // Access event name
            _context_stack[_context_stack.Count - 1]._return = _context_stack[_context_stack.Count - 1]._event._message;
        } else if (__e._message == "greet") {
            var name = (string) __e._parameters["name"];
            // Mix param access and return
            string result = "Hello, " + name + "!";
            _context_stack[_context_stack.Count - 1]._return = result;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 36: Context Basic ===");
        var s = new ContextBasicTest();

        // Test 1: @@.a and @@.b param access, @@:return
        var result1 = (int)s.add(3, 5);
        if (result1 != 8) {
            Console.WriteLine("FAIL: Expected 8, got " + result1);
            Environment.Exit(1);
        }
        Console.WriteLine("1. add(3, 5) = " + result1);

        // Test 2: @@:event access
        var eventName = (string)s.get_event_name();
        if (eventName != "get_event_name") {
            Console.WriteLine("FAIL: Expected 'get_event_name', got '" + eventName + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("2. @@:event = '" + eventName + "'");

        // Test 3: @@.name param access with string
        var greeting = (string)s.greet("World");
        if (greeting != "Hello, World!") {
            Console.WriteLine("FAIL: Expected 'Hello, World!', got '" + greeting + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("3. greet('World') = '" + greeting + "'");

        Console.WriteLine("PASS: Context basic access works correctly");
    }
}
