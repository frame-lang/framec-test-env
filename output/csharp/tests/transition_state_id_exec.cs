using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class SysXFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SysXFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SysXFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SysXFrameContext {
    public SysXFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SysXFrameContext(SysXFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SysXCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SysXFrameEvent forward_event;
    public SysXCompartment parent_compartment;

    public SysXCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SysXCompartment Copy() {
        SysXCompartment c = new SysXCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SysX {
    private List<SysXCompartment> _state_stack;
    private SysXCompartment __compartment;
    private SysXCompartment __next_compartment;
    private List<SysXFrameContext> _context_stack;

    public SysX() {
        _state_stack = new List<SysXCompartment>();
        _context_stack = new List<SysXFrameContext>();
        __compartment = new SysXCompartment("A");
        __next_compartment = null;
        SysXFrameEvent __frame_event = new SysXFrameEvent("$>");
        SysXFrameContext __ctx = new SysXFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(SysXFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SysXFrameEvent exit_event = new SysXFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SysXFrameEvent enter_event = new SysXFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    SysXFrameEvent enter_event = new SysXFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SysXFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        }
    }

    private void __transition(SysXCompartment next) {
        __next_compartment = next;
    }

    public void e() {
        SysXFrameEvent __e = new SysXFrameEvent("e");
        SysXFrameContext __ctx = new SysXFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_A(SysXFrameEvent __e) {
        if (__e._message == "e") {
            { var __new_compartment = new SysXCompartment("B");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_B(SysXFrameEvent __e) {

    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..1");
        try {
            SysX s = new SysX();
            s.e();
            Console.WriteLine("ok 1 - transition_state_id_exec");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - transition_state_id_exec # " + ex);
        }
    }
}
