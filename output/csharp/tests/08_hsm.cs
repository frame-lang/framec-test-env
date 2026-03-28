using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMForwardFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMForwardFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMForwardFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMForwardFrameContext {
    public HSMForwardFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMForwardFrameContext(HSMForwardFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMForwardCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMForwardFrameEvent forward_event;
    public HSMForwardCompartment parent_compartment;

    public HSMForwardCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMForwardCompartment Copy() {
        HSMForwardCompartment c = new HSMForwardCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMForward {
    private List<HSMForwardCompartment> _state_stack;
    private HSMForwardCompartment __compartment;
    private HSMForwardCompartment __next_compartment;
    private List<HSMForwardFrameContext> _context_stack;
    public List<string> log = new List<string>();

    public HSMForward() {
        _state_stack = new List<HSMForwardCompartment>();
        _context_stack = new List<HSMForwardFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMForwardCompartment("Parent");
        this.__compartment = new HSMForwardCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMForwardFrameEvent __frame_event = new HSMForwardFrameEvent("$>");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMForwardFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMForwardFrameEvent exit_event = new HSMForwardFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMForwardFrameEvent enter_event = new HSMForwardFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMForwardFrameEvent enter_event = new HSMForwardFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMForwardFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMForwardCompartment next) {
        __next_compartment = next;
    }

    public void event_a() {
        HSMForwardFrameEvent __e = new HSMForwardFrameEvent("event_a");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void event_b() {
        HSMForwardFrameEvent __e = new HSMForwardFrameEvent("event_b");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<string> get_log() {
        HSMForwardFrameEvent __e = new HSMForwardFrameEvent("get_log");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<string>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Parent(HSMForwardFrameEvent __e) {
        if (__e._message == "event_a") {
            this.log.Add("Parent:event_a");
        } else if (__e._message == "event_b") {
            this.log.Add("Parent:event_b");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        }
    }

    private void _state_Child(HSMForwardFrameEvent __e) {
        if (__e._message == "event_a") {
            this.log.Add("Child:event_a");
        } else if (__e._message == "event_b") {
            this.log.Add("Child:event_b_forward");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 08: HSM Forward ===");
        var s = new HSMForward();

        // event_a should be handled by Child (no forward)
        s.event_a();
        var log = (List<string>)s.get_log();
        if (!log.Contains("Child:event_a")) {
            throw new Exception("Expected 'Child:event_a' in log, got " + string.Join(", ", log));
        }
        Console.WriteLine("After event_a: [" + string.Join(", ", log) + "]");

        // event_b should forward to Parent
        s.event_b();
        log = (List<string>)s.get_log();
        if (!log.Contains("Child:event_b_forward")) {
            throw new Exception("Expected 'Child:event_b_forward' in log, got " + string.Join(", ", log));
        }
        if (!log.Contains("Parent:event_b")) {
            throw new Exception("Expected 'Parent:event_b' in log (forwarded), got " + string.Join(", ", log));
        }
        Console.WriteLine("After event_b (forwarded): [" + string.Join(", ", log) + "]");

        Console.WriteLine("PASS: HSM forward works correctly");
    }
}
