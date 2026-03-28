using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class Helper {
    public static int helper_function(int x) {
        // Native helper function defined before system
        return x * 2;
    }
}

class NativeCodeFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public NativeCodeFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public NativeCodeFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class NativeCodeFrameContext {
    public NativeCodeFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public NativeCodeFrameContext(NativeCodeFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class NativeCodeCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public NativeCodeFrameEvent forward_event;
    public NativeCodeCompartment parent_compartment;

    public NativeCodeCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public NativeCodeCompartment Copy() {
        NativeCodeCompartment c = new NativeCodeCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class NativeCode {
    private List<NativeCodeCompartment> _state_stack;
    private NativeCodeCompartment __compartment;
    private NativeCodeCompartment __next_compartment;
    private List<NativeCodeFrameContext> _context_stack;

    public NativeCode() {
        _state_stack = new List<NativeCodeCompartment>();
        _context_stack = new List<NativeCodeFrameContext>();
        __compartment = new NativeCodeCompartment("Active");
        __next_compartment = null;
        NativeCodeFrameEvent __frame_event = new NativeCodeFrameEvent("$>");
        NativeCodeFrameContext __ctx = new NativeCodeFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(NativeCodeFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            NativeCodeFrameEvent exit_event = new NativeCodeFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                NativeCodeFrameEvent enter_event = new NativeCodeFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    NativeCodeFrameEvent enter_event = new NativeCodeFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(NativeCodeFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    private void __transition(NativeCodeCompartment next) {
        __next_compartment = next;
    }

    public int compute(int value) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["value"] = value;
        NativeCodeFrameEvent __e = new NativeCodeFrameEvent("compute", __params);
        NativeCodeFrameContext __ctx = new NativeCodeFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public double use_math() {
        NativeCodeFrameEvent __e = new NativeCodeFrameEvent("use_math");
        NativeCodeFrameContext __ctx = new NativeCodeFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (double) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Active(NativeCodeFrameEvent __e) {
        if (__e._message == "compute") {
            var value = (int) __e._parameters["value"];
            // Native code with local variables
            int temp = value + 10;
            int result = Helper.helper_function(temp);
            Console.WriteLine("Computed: " + value + " -> " + result);
            _context_stack[_context_stack.Count - 1]._return = result;
            return;
        } else if (__e._message == "use_math") {
            // Using Math module
            double result = Math.Sqrt(16) + Math.PI;
            Console.WriteLine("Math result: " + result);
            _context_stack[_context_stack.Count - 1]._return = result;
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 04: Native Code Preservation ===");
        var s = new NativeCode();

        // Test native code in handler with helper function
        var result = (int)s.compute(5);
        int expected = (5 + 10) * 2;  // 30
        if (result != expected) {
            throw new Exception("Expected " + expected + ", got " + result);
        }
        Console.WriteLine("compute(5) = " + result);

        // Test Math module usage
        var mathResult = (double)s.use_math();
        double expectedMath = Math.Sqrt(16) + Math.PI;
        if (Math.Abs(mathResult - expectedMath) >= 0.001) {
            throw new Exception("Expected ~" + expectedMath + ", got " + mathResult);
        }
        Console.WriteLine("use_math() = " + mathResult);

        Console.WriteLine("PASS: Native code preservation works correctly");
    }
}
