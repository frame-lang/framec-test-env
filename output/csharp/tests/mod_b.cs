using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class S2FrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public S2FrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public S2FrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class S2FrameContext {
    public S2FrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public S2FrameContext(S2FrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class S2Compartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public S2FrameEvent forward_event;
    public S2Compartment parent_compartment;

    public S2Compartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public S2Compartment Copy() {
        S2Compartment c = new S2Compartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class S2 {
    private List<S2Compartment> _state_stack;
    private S2Compartment __compartment;
    private S2Compartment __next_compartment;
    private List<S2FrameContext> _context_stack;

    public S2() {
        _state_stack = new List<S2Compartment>();
        _context_stack = new List<S2FrameContext>();
        __compartment = new S2Compartment("A");
        __next_compartment = null;
        S2FrameEvent __frame_event = new S2FrameEvent("$>");
        S2FrameContext __ctx = new S2FrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(S2FrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            S2FrameEvent exit_event = new S2FrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                S2FrameEvent enter_event = new S2FrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    S2FrameEvent enter_event = new S2FrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(S2FrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "A") {
            _state_A(__e);
        }
    }

    private void __transition(S2Compartment next) {
        __next_compartment = next;
    }

    public void e() {
        S2FrameEvent __e = new S2FrameEvent("e");
        S2FrameContext __ctx = new S2FrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_A(S2FrameEvent __e) {
        if (__e._message == "e") {
            { var __new_compartment = new S2Compartment("A");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..1");
        try {
            S2 s = new S2();
            s.e();
            Console.WriteLine("ok 1 - mod_b");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - mod_b # " + ex);
        }
    }
}
