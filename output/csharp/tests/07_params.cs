using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class WithParamsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public WithParamsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public WithParamsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class WithParamsFrameContext {
    public WithParamsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public WithParamsFrameContext(WithParamsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class WithParamsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public WithParamsFrameEvent forward_event;
    public WithParamsCompartment parent_compartment;

    public WithParamsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public WithParamsCompartment Copy() {
        WithParamsCompartment c = new WithParamsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class WithParams {
    private List<WithParamsCompartment> _state_stack;
    private WithParamsCompartment __compartment;
    private WithParamsCompartment __next_compartment;
    private List<WithParamsFrameContext> _context_stack;
    public int total = 0;

    public WithParams() {
        _state_stack = new List<WithParamsCompartment>();
        _context_stack = new List<WithParamsFrameContext>();
        __compartment = new WithParamsCompartment("Idle");
        __next_compartment = null;
        WithParamsFrameEvent __frame_event = new WithParamsFrameEvent("$>");
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(WithParamsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            WithParamsFrameEvent exit_event = new WithParamsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                WithParamsFrameEvent enter_event = new WithParamsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    WithParamsFrameEvent enter_event = new WithParamsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(WithParamsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Running") {
            _state_Running(__e);
        }
    }

    private void __transition(WithParamsCompartment next) {
        __next_compartment = next;
    }

    public void start(int initial) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["initial"] = initial;
        WithParamsFrameEvent __e = new WithParamsFrameEvent("start", __params);
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void add(int value) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["value"] = value;
        WithParamsFrameEvent __e = new WithParamsFrameEvent("add", __params);
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int multiply(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        WithParamsFrameEvent __e = new WithParamsFrameEvent("multiply", __params);
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_total() {
        WithParamsFrameEvent __e = new WithParamsFrameEvent("get_total");
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Running(WithParamsFrameEvent __e) {
        if (__e._message == "add") {
            var value = (int) __e._parameters["value"];
            this.total += value;
            Console.WriteLine("Added " + value + ", total is now " + this.total);
        } else if (__e._message == "get_total") {
            _context_stack[_context_stack.Count - 1]._return = this.total;
            return;
        } else if (__e._message == "multiply") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            int result = a * b;
            this.total += result;
            Console.WriteLine("Multiplied " + a + " * " + b + " = " + result + ", total is now " + this.total);
            _context_stack[_context_stack.Count - 1]._return = result;
            return;
        } else if (__e._message == "start") {
            var initial = (int) __e._parameters["initial"];
            Console.WriteLine("Already running");
        }
    }

    private void _state_Idle(WithParamsFrameEvent __e) {
        if (__e._message == "add") {
            var value = (int) __e._parameters["value"];
            Console.WriteLine("Cannot add in Idle state");
        } else if (__e._message == "get_total") {
            _context_stack[_context_stack.Count - 1]._return = this.total;
            return;
        } else if (__e._message == "multiply") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            _context_stack[_context_stack.Count - 1]._return = 0;
            return;
        } else if (__e._message == "start") {
            var initial = (int) __e._parameters["initial"];
            this.total = initial;
            Console.WriteLine("Started with initial value: " + initial);
            { var __new_compartment = new WithParamsCompartment("Running");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 07: Handler Parameters ===");
        var s = new WithParams();

        // Initial total should be 0
        var total = (int)s.get_total();
        if (total != 0) {
            throw new Exception("Expected initial total=0, got " + total);
        }

        // Start with initial value
        s.start(100);
        total = (int)s.get_total();
        if (total != 100) {
            throw new Exception("Expected total=100, got " + total);
        }
        Console.WriteLine("After start(100): total = " + total);

        // Add value
        s.add(25);
        total = (int)s.get_total();
        if (total != 125) {
            throw new Exception("Expected total=125, got " + total);
        }
        Console.WriteLine("After add(25): total = " + total);

        // Multiply with two params
        var result = (int)s.multiply(3, 5);
        if (result != 15) {
            throw new Exception("Expected multiply result=15, got " + result);
        }
        total = (int)s.get_total();
        if (total != 140) {
            throw new Exception("Expected total=140, got " + total);
        }
        Console.WriteLine("After multiply(3,5): result = " + result + ", total = " + total);

        Console.WriteLine("PASS: Handler parameters work correctly");
    }
}
