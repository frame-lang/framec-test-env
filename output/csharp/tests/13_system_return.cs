using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class SystemReturnTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SystemReturnTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SystemReturnTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnTestFrameContext {
    public SystemReturnTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SystemReturnTestFrameContext(SystemReturnTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SystemReturnTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SystemReturnTestFrameEvent forward_event;
    public SystemReturnTestCompartment parent_compartment;

    public SystemReturnTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SystemReturnTestCompartment Copy() {
        SystemReturnTestCompartment c = new SystemReturnTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnTest {
    private List<SystemReturnTestCompartment> _state_stack;
    private SystemReturnTestCompartment __compartment;
    private SystemReturnTestCompartment __next_compartment;
    private List<SystemReturnTestFrameContext> _context_stack;

    public SystemReturnTest() {
        _state_stack = new List<SystemReturnTestCompartment>();
        _context_stack = new List<SystemReturnTestFrameContext>();
        __compartment = new SystemReturnTestCompartment("Calculator");
        __next_compartment = null;
        SystemReturnTestFrameEvent __frame_event = new SystemReturnTestFrameEvent("$>");
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(SystemReturnTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnTestFrameEvent exit_event = new SystemReturnTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnTestFrameEvent enter_event = new SystemReturnTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    SystemReturnTestFrameEvent enter_event = new SystemReturnTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Calculator") {
            _state_Calculator(__e);
        }
    }

    private void __transition(SystemReturnTestCompartment next) {
        __next_compartment = next;
    }

    public int add(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("add", __params);
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int multiply(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("multiply", __params);
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string greet(string name) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["name"] = name;
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("greet", __params);
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_value() {
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("get_value");
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Calculator(SystemReturnTestFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Calculator") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("value")) {
                __sv_comp.state_vars["value"] = 0;
            }
        } else if (__e._message == "add") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            _context_stack[_context_stack.Count - 1]._return = a + b;
            return;
        } else if (__e._message == "get_value") {
            __sv_comp.state_vars["value"] = 42;
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["value"];
            return;
        } else if (__e._message == "greet") {
            var name = (string) __e._parameters["name"];
            _context_stack[_context_stack.Count - 1]._return = "Hello, " + name + "!";
            return;
        } else if (__e._message == "multiply") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            _context_stack[_context_stack.Count - 1]._return = a * b;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 13: System Return ===");
        var calc = new SystemReturnTest();

        // Test return sugar
        var result = (int)calc.add(3, 5);
        if (result != 8) {
            throw new Exception("Expected 8, got " + result);
        }
        Console.WriteLine("add(3, 5) = " + result);

        // Test @@:return = expr
        result = (int)calc.multiply(4, 7);
        if (result != 28) {
            throw new Exception("Expected 28, got " + result);
        }
        Console.WriteLine("multiply(4, 7) = " + result);

        // Test string return
        var greeting = (string)calc.greet("World");
        if (greeting != "Hello, World!") {
            throw new Exception("Expected 'Hello, World!', got '" + greeting + "'");
        }
        Console.WriteLine("greet('World') = " + greeting);

        // Test return with state variable
        var value = (int)calc.get_value();
        if (value != 42) {
            throw new Exception("Expected 42, got " + value);
        }
        Console.WriteLine("get_value() = " + value);

        Console.WriteLine("PASS: System return works correctly");
    }
}
