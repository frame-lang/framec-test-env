using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class EventForwardTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public EventForwardTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public EventForwardTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class EventForwardTestFrameContext {
    public EventForwardTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public EventForwardTestFrameContext(EventForwardTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class EventForwardTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public EventForwardTestFrameEvent forward_event;
    public EventForwardTestCompartment parent_compartment;

    public EventForwardTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public EventForwardTestCompartment Copy() {
        EventForwardTestCompartment c = new EventForwardTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class EventForwardTest {
    private List<EventForwardTestCompartment> _state_stack;
    private EventForwardTestCompartment __compartment;
    private EventForwardTestCompartment __next_compartment;
    private List<EventForwardTestFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public EventForwardTest() {
        _state_stack = new List<EventForwardTestCompartment>();
        _context_stack = new List<EventForwardTestFrameContext>();
        __compartment = new EventForwardTestCompartment("Idle");
        __next_compartment = null;
        EventForwardTestFrameEvent __frame_event = new EventForwardTestFrameEvent("$>");
        EventForwardTestFrameContext __ctx = new EventForwardTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(EventForwardTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            EventForwardTestFrameEvent exit_event = new EventForwardTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                EventForwardTestFrameEvent enter_event = new EventForwardTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    EventForwardTestFrameEvent enter_event = new EventForwardTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(EventForwardTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Working") {
            _state_Working(__e);
        }
    }

    private void __transition(EventForwardTestCompartment next) {
        __next_compartment = next;
    }

    public void process() {
        EventForwardTestFrameEvent __e = new EventForwardTestFrameEvent("process");
        EventForwardTestFrameContext __ctx = new EventForwardTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        EventForwardTestFrameEvent __e = new EventForwardTestFrameEvent("get_log");
        EventForwardTestFrameContext __ctx = new EventForwardTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Idle(EventForwardTestFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "process") {
            this.log.Add("idle:process:before");
            { var __new_compartment = new EventForwardTestCompartment("Working");
            __new_compartment.parent_compartment = __compartment.Copy();
            __new_compartment.forward_event = __e;
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Working(EventForwardTestFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "process") {
            this.log.Add("working:process");
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 19: Transition Forward (C#) ===");
        var s = new EventForwardTest();
        s.process();
        var log = (List<object>)s.get_log();
        Console.WriteLine("Log: [" + string.Join(", ", log) + "]");

        if (!log.Contains("idle:process:before")) {
            Console.WriteLine("FAIL: Expected 'idle:process:before' in log: " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("working:process")) {
            Console.WriteLine("FAIL: Expected 'working:process' in log: " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (log.Contains("idle:process:after")) {
            Console.WriteLine("FAIL: Should NOT have 'idle:process:after' in log: " + string.Join(", ", log));
            Environment.Exit(1);
        }

        Console.WriteLine("PASS: Transition forward works correctly");
    }
}
