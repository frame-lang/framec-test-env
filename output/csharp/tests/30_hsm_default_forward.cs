using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMDefaultForwardFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMDefaultForwardFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMDefaultForwardFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMDefaultForwardFrameContext {
    public HSMDefaultForwardFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMDefaultForwardFrameContext(HSMDefaultForwardFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMDefaultForwardCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMDefaultForwardFrameEvent forward_event;
    public HSMDefaultForwardCompartment parent_compartment;

    public HSMDefaultForwardCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMDefaultForwardCompartment Copy() {
        HSMDefaultForwardCompartment c = new HSMDefaultForwardCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMDefaultForward {
    private List<HSMDefaultForwardCompartment> _state_stack;
    private HSMDefaultForwardCompartment __compartment;
    private HSMDefaultForwardCompartment __next_compartment;
    private List<HSMDefaultForwardFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMDefaultForward() {
        _state_stack = new List<HSMDefaultForwardCompartment>();
        _context_stack = new List<HSMDefaultForwardFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMDefaultForwardCompartment("Parent");
        this.__compartment = new HSMDefaultForwardCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMDefaultForwardFrameEvent __frame_event = new HSMDefaultForwardFrameEvent("$>");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMDefaultForwardFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMDefaultForwardFrameEvent exit_event = new HSMDefaultForwardFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMDefaultForwardFrameEvent enter_event = new HSMDefaultForwardFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMDefaultForwardFrameEvent enter_event = new HSMDefaultForwardFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMDefaultForwardFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMDefaultForwardCompartment next) {
        __next_compartment = next;
    }

    public void handled_event() {
        HSMDefaultForwardFrameEvent __e = new HSMDefaultForwardFrameEvent("handled_event");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void unhandled_event() {
        HSMDefaultForwardFrameEvent __e = new HSMDefaultForwardFrameEvent("unhandled_event");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMDefaultForwardFrameEvent __e = new HSMDefaultForwardFrameEvent("get_log");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Parent(HSMDefaultForwardFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "handled_event") {
            this.log.Add("Parent:handled_event");
        } else if (__e._message == "unhandled_event") {
            this.log.Add("Parent:unhandled_event");
        }
    }

    private void _state_Child(HSMDefaultForwardFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "handled_event") {
            this.log.Add("Child:handled_event");
        } else {
            _state_Parent(__e);
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 30: HSM State-Level Default Forward ===");
        var s = new HSMDefaultForward();

        s.handled_event();
        var log = (List<object>)s.get_log();
        if (!log.Contains("Child:handled_event")) {
            Console.WriteLine("FAIL: Expected 'Child:handled_event' in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("After handled_event: [" + string.Join(", ", log) + "]");

        s.unhandled_event();
        log = (List<object>)s.get_log();
        if (!log.Contains("Parent:unhandled_event")) {
            Console.WriteLine("FAIL: Expected 'Parent:unhandled_event' in log (forwarded), got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("After unhandled_event (forwarded): [" + string.Join(", ", log) + "]");

        Console.WriteLine("PASS: HSM state-level default forward works correctly");
    }
}
