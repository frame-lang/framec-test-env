using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class CallMismatchFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public CallMismatchFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public CallMismatchFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class CallMismatchFrameContext {
    public CallMismatchFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public CallMismatchFrameContext(CallMismatchFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class CallMismatchCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public CallMismatchFrameEvent forward_event;
    public CallMismatchCompartment parent_compartment;

    public CallMismatchCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public CallMismatchCompartment Copy() {
        CallMismatchCompartment c = new CallMismatchCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class CallMismatch {
    private List<CallMismatchCompartment> _state_stack;
    private CallMismatchCompartment __compartment;
    private CallMismatchCompartment __next_compartment;
    private List<CallMismatchFrameContext> _context_stack;
    public string last = "";

    public CallMismatch() {
        _state_stack = new List<CallMismatchCompartment>();
        _context_stack = new List<CallMismatchFrameContext>();
        __compartment = new CallMismatchCompartment("S");
        __next_compartment = null;
        CallMismatchFrameEvent __frame_event = new CallMismatchFrameEvent("$>");
        CallMismatchFrameContext __ctx = new CallMismatchFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(CallMismatchFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            CallMismatchFrameEvent exit_event = new CallMismatchFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                CallMismatchFrameEvent enter_event = new CallMismatchFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    CallMismatchFrameEvent enter_event = new CallMismatchFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(CallMismatchFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "S") {
            _state_S(__e);
        }
    }

    private void __transition(CallMismatchCompartment next) {
        __next_compartment = next;
    }

    public void e() {
        CallMismatchFrameEvent __e = new CallMismatchFrameEvent("e");
        CallMismatchFrameContext __ctx = new CallMismatchFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_S(CallMismatchFrameEvent __e) {
        if (__e._message == "e") {
            this.handle();
        }
    }

    private void log(string message) {
                    // log sink
                    this.last = message;
    }

    private void handle() {
                    // Calls 'log' without _action_ prefix; wrappers should preserve FRM names
                    this.log("hello");
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..1");
        try {
            CallMismatch s = new CallMismatch();
            s.e();
            Console.WriteLine("ok 1 - actions_call_wrappers");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - actions_call_wrappers # " + ex);
        }
    }
}
