using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class TransitionPopTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public TransitionPopTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public TransitionPopTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TransitionPopTestFrameContext {
    public TransitionPopTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public TransitionPopTestFrameContext(TransitionPopTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class TransitionPopTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public TransitionPopTestFrameEvent forward_event;
    public TransitionPopTestCompartment parent_compartment;

    public TransitionPopTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public TransitionPopTestCompartment Copy() {
        TransitionPopTestCompartment c = new TransitionPopTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TransitionPopTest {
    private List<TransitionPopTestCompartment> _state_stack;
    private TransitionPopTestCompartment __compartment;
    private TransitionPopTestCompartment __next_compartment;
    private List<TransitionPopTestFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public TransitionPopTest() {
        _state_stack = new List<TransitionPopTestCompartment>();
        _context_stack = new List<TransitionPopTestFrameContext>();
        __compartment = new TransitionPopTestCompartment("Idle");
        __next_compartment = null;
        TransitionPopTestFrameEvent __frame_event = new TransitionPopTestFrameEvent("$>");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(TransitionPopTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TransitionPopTestFrameEvent exit_event = new TransitionPopTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TransitionPopTestFrameEvent enter_event = new TransitionPopTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    TransitionPopTestFrameEvent enter_event = new TransitionPopTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TransitionPopTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Working") {
            _state_Working(__e);
        }
    }

    private void __transition(TransitionPopTestCompartment next) {
        __next_compartment = next;
    }

    public void start() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("start");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void process() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("process");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("get_state");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public List<object> get_log() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("get_log");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Idle(TransitionPopTestFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Idle";
            return;
        } else if (__e._message == "process") {
            this.log.Add("idle:process");
        } else if (__e._message == "start") {
            this.log.Add("idle:start:push");
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new TransitionPopTestCompartment("Working");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Working(TransitionPopTestFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Working";
            return;
        } else if (__e._message == "process") {
            this.log.Add("working:process:before_pop");
            var __popped = _state_stack[_state_stack.Count - 1]; _state_stack.RemoveAt(_state_stack.Count - 1);
            __transition(__popped);
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 20: Transition Pop (C#) ===");
        var s = new TransitionPopTest();

        // Initial state should be Idle
        if ((string)s.get_state() != "Idle") {
            Console.WriteLine("FAIL: Expected 'Idle', got '" + s.get_state() + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("Initial state: " + s.get_state());

        // start() pushes Idle, transitions to Working
        s.start();
        if ((string)s.get_state() != "Working") {
            Console.WriteLine("FAIL: Expected 'Working', got '" + s.get_state() + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("After start(): " + s.get_state());

        // process() in Working does pop transition back to Idle
        s.process();
        if ((string)s.get_state() != "Idle") {
            Console.WriteLine("FAIL: Expected 'Idle' after pop, got '" + s.get_state() + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("After process() with pop: " + s.get_state());

        var log = (List<object>)s.get_log();
        Console.WriteLine("Log: [" + string.Join(", ", log) + "]");

        // Verify log contents
        if (!log.Contains("idle:start:push")) {
            Console.WriteLine("FAIL: Expected 'idle:start:push' in log");
            Environment.Exit(1);
        }
        if (!log.Contains("working:process:before_pop")) {
            Console.WriteLine("FAIL: Expected 'working:process:before_pop' in log");
            Environment.Exit(1);
        }
        if (log.Contains("working:process:after_pop")) {
            Console.WriteLine("FAIL: Should NOT have 'working:process:after_pop' in log");
            Environment.Exit(1);
        }

        Console.WriteLine("PASS: Transition pop works correctly");
    }
}
