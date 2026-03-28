using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class PFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public PFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public PFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PFrameContext {
    public PFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public PFrameContext(PFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class PCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public PFrameEvent forward_event;
    public PCompartment parent_compartment;

    public PCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public PCompartment Copy() {
        PCompartment c = new PCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class P {
    private List<PCompartment> _state_stack;
    private PCompartment __compartment;
    private PCompartment __next_compartment;
    private List<PFrameContext> _context_stack;

    public P() {
        _state_stack = new List<PCompartment>();
        _context_stack = new List<PFrameContext>();
        __compartment = new PCompartment("A");
        __next_compartment = null;
        PFrameEvent __frame_event = new PFrameEvent("$>");
        PFrameContext __ctx = new PFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(PFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            PFrameEvent exit_event = new PFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                PFrameEvent enter_event = new PFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    PFrameEvent enter_event = new PFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(PFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        }
    }

    private void __transition(PCompartment next) {
        __next_compartment = next;
    }

    public void e() {
        PFrameEvent __e = new PFrameEvent("e");
        PFrameContext __ctx = new PFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_B(PFrameEvent __e) {
        if (__e._message == "e") {
            ;
        }
    }

    private void _state_A(PFrameEvent __e) {
        if (__e._message == "e") {
            { var __new_compartment = new PCompartment("B");
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
            P s = new P();
            s.e();
            Console.WriteLine("ok 1 - basic_project");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - basic_project # " + ex);
        }
    }
}
