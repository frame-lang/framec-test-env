using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class ContextDataTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public ContextDataTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public ContextDataTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ContextDataTestFrameContext {
    public ContextDataTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public ContextDataTestFrameContext(ContextDataTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class ContextDataTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public ContextDataTestFrameEvent forward_event;
    public ContextDataTestCompartment parent_compartment;

    public ContextDataTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public ContextDataTestCompartment Copy() {
        ContextDataTestCompartment c = new ContextDataTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ContextDataTest {
    private List<ContextDataTestCompartment> _state_stack;
    private ContextDataTestCompartment __compartment;
    private ContextDataTestCompartment __next_compartment;
    private List<ContextDataTestFrameContext> _context_stack;

    public ContextDataTest() {
        _state_stack = new List<ContextDataTestCompartment>();
        _context_stack = new List<ContextDataTestFrameContext>();
        __compartment = new ContextDataTestCompartment("Start");
        __next_compartment = null;
        ContextDataTestFrameEvent __frame_event = new ContextDataTestFrameEvent("$>");
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(ContextDataTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ContextDataTestFrameEvent exit_event = new ContextDataTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ContextDataTestFrameEvent enter_event = new ContextDataTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    ContextDataTestFrameEvent enter_event = new ContextDataTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ContextDataTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "End") {
            _state_End(__e);
        }
    }

    private void __transition(ContextDataTestCompartment next) {
        __next_compartment = next;
    }

    public string process_with_data(int value) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["value"] = value;
        ContextDataTestFrameEvent __e = new ContextDataTestFrameEvent("process_with_data", __params);
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string check_data_isolation() {
        ContextDataTestFrameEvent __e = new ContextDataTestFrameEvent("check_data_isolation");
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string transition_preserves_data(int x) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["x"] = x;
        ContextDataTestFrameEvent __e = new ContextDataTestFrameEvent("transition_preserves_data", __params);
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Start(ContextDataTestFrameEvent __e) {
        if (__e._message == "<$") {
            // Exit handler can access data set by event handler
            ((List<string>)_context_stack[_context_stack.Count - 1]._data["trace"]).Add("exit");
        } else if (__e._message == "check_data_isolation") {
            // Set data, call another method, verify our data preserved
            _context_stack[_context_stack.Count - 1]._data["outer"] = "outer_value";

            // This creates its own context with its own data
            string inner_result = this.process_with_data(99);

            // Our data should still be here
            _context_stack[_context_stack.Count - 1]._return = "outer_data=" + _context_stack[_context_stack.Count - 1]._data["outer"] + ",inner=" + inner_result;
        } else if (__e._message == "process_with_data") {
            var value = (int) __e._parameters["value"];
            // Set data in handler
            _context_stack[_context_stack.Count - 1]._data["input"] = value;
            _context_stack[_context_stack.Count - 1]._data["trace"] = new List<string>(new string[] {"handler"});

            _context_stack[_context_stack.Count - 1]._return = "processed:" + _context_stack[_context_stack.Count - 1]._data["input"];
        } else if (__e._message == "transition_preserves_data") {
            var x = (int) __e._parameters["x"];
            // Set data, transition, verify data available in lifecycle handlers
            _context_stack[_context_stack.Count - 1]._data["started_in"] = "Start";
            _context_stack[_context_stack.Count - 1]._data["value"] = x;
            _context_stack[_context_stack.Count - 1]._data["trace"] = new List<string>(new string[] {"handler"});
            { var __new_compartment = new ContextDataTestCompartment("End");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_End(ContextDataTestFrameEvent __e) {
        if (__e._message == "$>") {
            // Enter handler can access data set by previous handlers
            ((List<string>)_context_stack[_context_stack.Count - 1]._data["trace"]).Add("enter");
            _context_stack[_context_stack.Count - 1]._data["ended_in"] = "End";

            // Build final result from accumulated data
            var trace = (List<string>)_context_stack[_context_stack.Count - 1]._data["trace"];
            string trace_str = trace != null ? string.Join(",", trace) : "no_trace";
            _context_stack[_context_stack.Count - 1]._return = "from=" + _context_stack[_context_stack.Count - 1]._data["started_in"] + ",to=" + _context_stack[_context_stack.Count - 1]._data["ended_in"] + ",value=" + _context_stack[_context_stack.Count - 1]._data["value"] + ",trace=" + trace_str;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 38: Context Data ===");

        // Test 1: Basic data set/get
        var s1 = new ContextDataTest();
        var result = (string)s1.process_with_data(42);
        if (result != "processed:42") {
            Console.WriteLine("FAIL: Expected 'processed:42', got '" + result + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("1. process_with_data(42) = '" + result + "'");

        // Test 2: Data isolation between nested calls
        var s2 = new ContextDataTest();
        result = (string)s2.check_data_isolation();
        var expected = "outer_data=outer_value,inner=processed:99";
        if (result != expected) {
            Console.WriteLine("FAIL: Expected '" + expected + "', got '" + result + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("2. check_data_isolation() = '" + result + "'");

        // Test 3: Data preserved across transition (handler -> <$ -> $>)
        var s3 = new ContextDataTest();
        result = (string)s3.transition_preserves_data(100);
        // Data should flow: handler sets -> exit accesses -> enter accesses and returns
        if (!result.Contains("from=Start")) {
            Console.WriteLine("FAIL: Expected 'from=Start' in '" + result + "'");
            Environment.Exit(1);
        }
        if (!result.Contains("to=End")) {
            Console.WriteLine("FAIL: Expected 'to=End' in '" + result + "'");
            Environment.Exit(1);
        }
        if (!result.Contains("value=100")) {
            Console.WriteLine("FAIL: Expected 'value=100' in '" + result + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("3. transition_preserves_data(100) = '" + result + "'");

        Console.WriteLine("PASS: Context data works correctly");
    }
}
