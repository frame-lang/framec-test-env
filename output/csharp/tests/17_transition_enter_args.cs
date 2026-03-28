using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class TransitionEnterArgsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public TransitionEnterArgsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public TransitionEnterArgsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TransitionEnterArgsFrameContext {
    public TransitionEnterArgsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public TransitionEnterArgsFrameContext(TransitionEnterArgsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class TransitionEnterArgsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public TransitionEnterArgsFrameEvent forward_event;
    public TransitionEnterArgsCompartment parent_compartment;

    public TransitionEnterArgsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public TransitionEnterArgsCompartment Copy() {
        TransitionEnterArgsCompartment c = new TransitionEnterArgsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TransitionEnterArgs {
    private List<TransitionEnterArgsCompartment> _state_stack;
    private TransitionEnterArgsCompartment __compartment;
    private TransitionEnterArgsCompartment __next_compartment;
    private List<TransitionEnterArgsFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public TransitionEnterArgs() {
        _state_stack = new List<TransitionEnterArgsCompartment>();
        _context_stack = new List<TransitionEnterArgsFrameContext>();
        __compartment = new TransitionEnterArgsCompartment("Idle");
        __next_compartment = null;
        TransitionEnterArgsFrameEvent __frame_event = new TransitionEnterArgsFrameEvent("$>");
        TransitionEnterArgsFrameContext __ctx = new TransitionEnterArgsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(TransitionEnterArgsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TransitionEnterArgsFrameEvent exit_event = new TransitionEnterArgsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TransitionEnterArgsFrameEvent enter_event = new TransitionEnterArgsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    TransitionEnterArgsFrameEvent enter_event = new TransitionEnterArgsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TransitionEnterArgsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    private void __transition(TransitionEnterArgsCompartment next) {
        __next_compartment = next;
    }

    public void start() {
        TransitionEnterArgsFrameEvent __e = new TransitionEnterArgsFrameEvent("start");
        TransitionEnterArgsFrameContext __ctx = new TransitionEnterArgsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        TransitionEnterArgsFrameEvent __e = new TransitionEnterArgsFrameEvent("get_log");
        TransitionEnterArgsFrameContext __ctx = new TransitionEnterArgsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Active(TransitionEnterArgsFrameEvent __e) {
        if (__e._message == "$>") {
            var source = (string) __compartment.enter_args["0"];
            var value = (int) __compartment.enter_args["1"];
            this.log.Add("active:enter:" + source + ":" + value);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "start") {
            this.log.Add("active:start");
        }
    }

    private void _state_Idle(TransitionEnterArgsFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "start") {
            this.log.Add("idle:start");
            { var __new_compartment = new TransitionEnterArgsCompartment("Active");
            __new_compartment.parent_compartment = __compartment.Copy();
            __new_compartment.enter_args["0"] = "from_idle";
            __new_compartment.enter_args["1"] = 42;
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 17: Transition Enter Args ===");
        var s = new TransitionEnterArgs();

        // Initial state is Idle
        var log = (List<object>)s.get_log();
        if (log.Count != 0) {
            Console.WriteLine("FAIL: Expected empty log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }

        // Transition to Active with args
        s.start();
        log = (List<object>)s.get_log();
        if (!log.Contains("idle:start")) {
            Console.WriteLine("FAIL: Expected 'idle:start' in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("active:enter:from_idle:42")) {
            Console.WriteLine("FAIL: Expected 'active:enter:from_idle:42' in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("Log after transition: [" + string.Join(", ", log) + "]");

        Console.WriteLine("PASS: Transition enter args work correctly");
    }
}
