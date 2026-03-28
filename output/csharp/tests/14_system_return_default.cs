using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// NOTE: Default return value syntax (method(): type = default) not yet implemented.
// This test validates behavior when handler doesn't set @@:return.

class SystemReturnDefaultTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SystemReturnDefaultTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SystemReturnDefaultTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnDefaultTestFrameContext {
    public SystemReturnDefaultTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SystemReturnDefaultTestFrameContext(SystemReturnDefaultTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SystemReturnDefaultTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SystemReturnDefaultTestFrameEvent forward_event;
    public SystemReturnDefaultTestCompartment parent_compartment;

    public SystemReturnDefaultTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SystemReturnDefaultTestCompartment Copy() {
        SystemReturnDefaultTestCompartment c = new SystemReturnDefaultTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnDefaultTest {
    private List<SystemReturnDefaultTestCompartment> _state_stack;
    private SystemReturnDefaultTestCompartment __compartment;
    private SystemReturnDefaultTestCompartment __next_compartment;
    private List<SystemReturnDefaultTestFrameContext> _context_stack;

    public SystemReturnDefaultTest() {
        _state_stack = new List<SystemReturnDefaultTestCompartment>();
        _context_stack = new List<SystemReturnDefaultTestFrameContext>();
        __compartment = new SystemReturnDefaultTestCompartment("Start");
        __next_compartment = null;
        SystemReturnDefaultTestFrameEvent __frame_event = new SystemReturnDefaultTestFrameEvent("$>");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(SystemReturnDefaultTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnDefaultTestFrameEvent exit_event = new SystemReturnDefaultTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnDefaultTestFrameEvent enter_event = new SystemReturnDefaultTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    SystemReturnDefaultTestFrameEvent enter_event = new SystemReturnDefaultTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnDefaultTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    private void __transition(SystemReturnDefaultTestCompartment next) {
        __next_compartment = next;
    }

    public string handler_sets_value() {
        SystemReturnDefaultTestFrameEvent __e = new SystemReturnDefaultTestFrameEvent("handler_sets_value");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string handler_no_return() {
        SystemReturnDefaultTestFrameEvent __e = new SystemReturnDefaultTestFrameEvent("handler_no_return");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_count() {
        SystemReturnDefaultTestFrameEvent __e = new SystemReturnDefaultTestFrameEvent("get_count");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Start(SystemReturnDefaultTestFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Start") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("count")) {
                __sv_comp.state_vars["count"] = 0;
            }
        } else if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["count"];
            return;
        } else if (__e._message == "handler_no_return") {
            // Does not set return - should return null
            __sv_comp.state_vars["count"] = (int) __sv_comp.state_vars["count"] + 1;
        } else if (__e._message == "handler_sets_value") {
            _context_stack[_context_stack.Count - 1]._return = "set_by_handler";
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 14: System Return Default Behavior ===");
        var s = new SystemReturnDefaultTest();

        // Test 1: Handler explicitly sets return value
        var result1 = (string)s.handler_sets_value();
        if (result1 != "set_by_handler") {
            throw new Exception("Expected 'set_by_handler', got '" + result1 + "'");
        }
        Console.WriteLine("1. handler_sets_value() = '" + result1 + "'");

        // Test 2: Handler does NOT set return - should return null
        var result2 = (string)s.handler_no_return();
        if (result2 != null) {
            throw new Exception("Expected null, got '" + result2 + "'");
        }
        Console.WriteLine("2. handler_no_return() = " + result2);

        // Test 3: Verify handler was called (side effect check)
        var count = (int)s.get_count();
        if (count != 1) {
            throw new Exception("Expected count=1, got " + count);
        }
        Console.WriteLine("3. Handler was called, count = " + count);

        // Test 4: Call again to verify idempotence
        var result4 = (string)s.handler_no_return();
        if (result4 != null) {
            throw new Exception("Expected null again, got '" + result4 + "'");
        }
        count = (int)s.get_count();
        if (count != 2) {
            throw new Exception("Expected count=2, got " + count);
        }
        Console.WriteLine("4. Second call: result=" + result4 + ", count=" + count);

        Console.WriteLine("PASS: System return default behavior works correctly");
    }
}
