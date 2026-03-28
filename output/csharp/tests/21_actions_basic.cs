using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class ActionsTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public ActionsTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public ActionsTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ActionsTestFrameContext {
    public ActionsTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public ActionsTestFrameContext(ActionsTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class ActionsTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public ActionsTestFrameEvent forward_event;
    public ActionsTestCompartment parent_compartment;

    public ActionsTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public ActionsTestCompartment Copy() {
        ActionsTestCompartment c = new ActionsTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ActionsTest {
    private List<ActionsTestCompartment> _state_stack;
    private ActionsTestCompartment __compartment;
    private ActionsTestCompartment __next_compartment;
    private List<ActionsTestFrameContext> _context_stack;
    public string log = "";

    public ActionsTest() {
        _state_stack = new List<ActionsTestCompartment>();
        _context_stack = new List<ActionsTestFrameContext>();
        __compartment = new ActionsTestCompartment("Ready");
        __next_compartment = null;
        ActionsTestFrameEvent __frame_event = new ActionsTestFrameEvent("$>");
        ActionsTestFrameContext __ctx = new ActionsTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(ActionsTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ActionsTestFrameEvent exit_event = new ActionsTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ActionsTestFrameEvent enter_event = new ActionsTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    ActionsTestFrameEvent enter_event = new ActionsTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ActionsTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(ActionsTestCompartment next) {
        __next_compartment = next;
    }

    public int process(int value) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["value"] = value;
        ActionsTestFrameEvent __e = new ActionsTestFrameEvent("process", __params);
        ActionsTestFrameContext __ctx = new ActionsTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_log() {
        ActionsTestFrameEvent __e = new ActionsTestFrameEvent("get_log");
        ActionsTestFrameContext __ctx = new ActionsTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Ready(ActionsTestFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "process") {
            var value = (int) __e._parameters["value"];
            this.__log_event("start");
            this.__validate_positive(value);
            this.__log_event("valid");
            int result = value * 2;
            this.__log_event("done");
            _context_stack[_context_stack.Count - 1]._return = result;
            return;
        }
    }

    private void __log_event(string msg) {
                    this.log = this.log + msg + ";";
    }

    private void __validate_positive(int n) {
                    if (n < 0) {
                        throw new Exception("Value must be positive: " + n);
                    }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 21: Actions Basic (C#) ===");
        var s = new ActionsTest();

        // Test 1: Actions are called correctly
        var result = (int)s.process(5);
        if (result != 10) {
            Console.WriteLine("FAIL: Expected 10, got " + result);
            Environment.Exit(1);
        }
        Console.WriteLine("1. process(5) = " + result);

        // Test 2: Log shows action calls
        var log = (string)s.get_log();
        if (!log.Contains("start")) {
            Console.WriteLine("FAIL: Missing 'start' in log: " + log);
            Environment.Exit(1);
        }
        if (!log.Contains("valid")) {
            Console.WriteLine("FAIL: Missing 'valid' in log: " + log);
            Environment.Exit(1);
        }
        if (!log.Contains("done")) {
            Console.WriteLine("FAIL: Missing 'done' in log: " + log);
            Environment.Exit(1);
        }
        Console.WriteLine("2. Log: " + log);

        // Test 3: Action with validation
        try {
            s.process(-1);
            Console.WriteLine("FAIL: Should have thrown Exception");
            Environment.Exit(1);
        } catch (Exception e) {
            if (e.Message.Contains("positive")) {
                Console.WriteLine("3. Validation caught: " + e.Message);
            } else {
                throw;
            }
        }

        Console.WriteLine("PASS: Actions basic works correctly");
    }
}
