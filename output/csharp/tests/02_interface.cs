using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class WithInterfaceFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public WithInterfaceFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public WithInterfaceFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class WithInterfaceFrameContext {
    public WithInterfaceFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public WithInterfaceFrameContext(WithInterfaceFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class WithInterfaceCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public WithInterfaceFrameEvent forward_event;
    public WithInterfaceCompartment parent_compartment;

    public WithInterfaceCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public WithInterfaceCompartment Copy() {
        WithInterfaceCompartment c = new WithInterfaceCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class WithInterface {
    private List<WithInterfaceCompartment> _state_stack;
    private WithInterfaceCompartment __compartment;
    private WithInterfaceCompartment __next_compartment;
    private List<WithInterfaceFrameContext> _context_stack;
    public int call_count = 0;

    public WithInterface() {
        _state_stack = new List<WithInterfaceCompartment>();
        _context_stack = new List<WithInterfaceFrameContext>();
        __compartment = new WithInterfaceCompartment("Ready");
        __next_compartment = null;
        WithInterfaceFrameEvent __frame_event = new WithInterfaceFrameEvent("$>");
        WithInterfaceFrameContext __ctx = new WithInterfaceFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(WithInterfaceFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            WithInterfaceFrameEvent exit_event = new WithInterfaceFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                WithInterfaceFrameEvent enter_event = new WithInterfaceFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    WithInterfaceFrameEvent enter_event = new WithInterfaceFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(WithInterfaceFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(WithInterfaceCompartment next) {
        __next_compartment = next;
    }

    public string greet(string name) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["name"] = name;
        WithInterfaceFrameEvent __e = new WithInterfaceFrameEvent("greet", __params);
        WithInterfaceFrameContext __ctx = new WithInterfaceFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_count() {
        WithInterfaceFrameEvent __e = new WithInterfaceFrameEvent("get_count");
        WithInterfaceFrameContext __ctx = new WithInterfaceFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Ready(WithInterfaceFrameEvent __e) {
        if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = this.call_count;
            return;
        } else if (__e._message == "greet") {
            var name = (string) __e._parameters["name"];
            this.call_count += 1;
            _context_stack[_context_stack.Count - 1]._return = "Hello, " + name + "!";
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 02: Interface Methods ===");
        var s = new WithInterface();

        // Test interface method with parameter and return
        var result = (string)s.greet("World");
        if (result != "Hello, World!") {
            throw new Exception("Expected 'Hello, World!', got '" + result + "'");
        }
        Console.WriteLine("greet('World') = " + result);

        // Test domain variable access through interface
        var count = (int)s.get_count();
        if (count != 1) {
            throw new Exception("Expected count=1, got " + count);
        }
        Console.WriteLine("get_count() = " + count);

        // Call again to verify state
        s.greet("Frame");
        var count2 = (int)s.get_count();
        if (count2 != 2) {
            throw new Exception("Expected count=2, got " + count2);
        }
        Console.WriteLine("After second call: get_count() = " + count2);

        Console.WriteLine("PASS: Interface methods work correctly");
    }
}
