using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class SystemReturnReentrantTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SystemReturnReentrantTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SystemReturnReentrantTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnReentrantTestFrameContext {
    public SystemReturnReentrantTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SystemReturnReentrantTestFrameContext(SystemReturnReentrantTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SystemReturnReentrantTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SystemReturnReentrantTestFrameEvent forward_event;
    public SystemReturnReentrantTestCompartment parent_compartment;

    public SystemReturnReentrantTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SystemReturnReentrantTestCompartment Copy() {
        SystemReturnReentrantTestCompartment c = new SystemReturnReentrantTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnReentrantTest {
    private List<SystemReturnReentrantTestCompartment> _state_stack;
    private SystemReturnReentrantTestCompartment __compartment;
    private SystemReturnReentrantTestCompartment __next_compartment;
    private List<SystemReturnReentrantTestFrameContext> _context_stack;

    public SystemReturnReentrantTest() {
        _state_stack = new List<SystemReturnReentrantTestCompartment>();
        _context_stack = new List<SystemReturnReentrantTestFrameContext>();
        __compartment = new SystemReturnReentrantTestCompartment("Start");
        __next_compartment = null;
        SystemReturnReentrantTestFrameEvent __frame_event = new SystemReturnReentrantTestFrameEvent("$>");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(SystemReturnReentrantTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnReentrantTestFrameEvent exit_event = new SystemReturnReentrantTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnReentrantTestFrameEvent enter_event = new SystemReturnReentrantTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    SystemReturnReentrantTestFrameEvent enter_event = new SystemReturnReentrantTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnReentrantTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    private void __transition(SystemReturnReentrantTestCompartment next) {
        __next_compartment = next;
    }

    public string outer_call() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("outer_call");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string inner_call() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("inner_call");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string nested_call() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("nested_call");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_log() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("get_log");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Start(SystemReturnReentrantTestFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Start") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("log")) {
                __sv_comp.state_vars["log"] = "";
            }
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = (string) __sv_comp.state_vars["log"];
            return;
        } else if (__e._message == "inner_call") {
            __sv_comp.state_vars["log"] = (string) __sv_comp.state_vars["log"] + "inner,";
            _context_stack[_context_stack.Count - 1]._return = "inner_result";
            return;
        } else if (__e._message == "nested_call") {
            __sv_comp.state_vars["log"] = (string) __sv_comp.state_vars["log"] + "nested_start,";
            // Two levels of nesting
            string result1 = this.inner_call();
            string result2 = this.outer_call();
            __sv_comp.state_vars["log"] = (string) __sv_comp.state_vars["log"] + "nested_end,";
            _context_stack[_context_stack.Count - 1]._return = "nested:" + result1 + "+" + result2;
            return;
        } else if (__e._message == "outer_call") {
            __sv_comp.state_vars["log"] = (string) __sv_comp.state_vars["log"] + "outer_start,";
            // Call inner method - this creates nested return context
            string inner_result = this.inner_call();
            __sv_comp.state_vars["log"] = (string) __sv_comp.state_vars["log"] + "outer_after_inner,";
            // Our return should be independent of inner's return
            _context_stack[_context_stack.Count - 1]._return = "outer_result:" + inner_result;
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 16: System Return Reentrant (Nested Calls) ===");

        // Test 1: Simple inner call
        var s1 = new SystemReturnReentrantTest();
        var result1 = (string)s1.inner_call();
        if (result1 != "inner_result") {
            Console.WriteLine("FAIL: Expected 'inner_result', got '" + result1 + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("1. inner_call() = '" + result1 + "'");

        // Test 2: Outer calls inner - return contexts should be separate
        var s2 = new SystemReturnReentrantTest();
        var result2 = (string)s2.outer_call();
        if (result2 != "outer_result:inner_result") {
            Console.WriteLine("FAIL: Expected 'outer_result:inner_result', got '" + result2 + "'");
            Environment.Exit(1);
        }
        var log2 = (string)s2.get_log();
        if (!log2.Contains("outer_start")) {
            Console.WriteLine("FAIL: Missing outer_start in log: " + log2);
            Environment.Exit(1);
        }
        if (!log2.Contains("inner")) {
            Console.WriteLine("FAIL: Missing inner in log: " + log2);
            Environment.Exit(1);
        }
        if (!log2.Contains("outer_after_inner")) {
            Console.WriteLine("FAIL: Missing outer_after_inner in log: " + log2);
            Environment.Exit(1);
        }
        Console.WriteLine("2. outer_call() = '" + result2 + "'");
        Console.WriteLine("   Log: '" + log2 + "'");

        // Test 3: Deeply nested calls
        var s3 = new SystemReturnReentrantTest();
        var result3 = (string)s3.nested_call();
        var expected = "nested:inner_result+outer_result:inner_result";
        if (result3 != expected) {
            Console.WriteLine("FAIL: Expected '" + expected + "', got '" + result3 + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("3. nested_call() = '" + result3 + "'");

        Console.WriteLine("PASS: System return reentrant (nested calls) works correctly");
    }
}
