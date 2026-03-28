using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class SFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SFrameContext {
    public SFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SFrameContext(SFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SFrameEvent forward_event;
    public SCompartment parent_compartment;

    public SCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SCompartment Copy() {
        SCompartment c = new SCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class S {
    private List<SCompartment> _state_stack;
    private SCompartment __compartment;
    private SCompartment __next_compartment;
    private List<SFrameContext> _context_stack;

    public S() {
        _state_stack = new List<SCompartment>();
        _context_stack = new List<SFrameContext>();
        __compartment = new SCompartment("A");
        __next_compartment = null;
        SFrameEvent __frame_event = new SFrameEvent("$>");
        SFrameContext __ctx = new SFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(SFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SFrameEvent exit_event = new SFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SFrameEvent enter_event = new SFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    SFrameEvent enter_event = new SFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        }
    }

    private void __transition(SCompartment next) {
        __next_compartment = next;
    }

    public void g(object x) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["x"] = x;
        SFrameEvent __e = new SFrameEvent("g", __params);
        SFrameContext __ctx = new SFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void e(object p, object q) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["p"] = p;
        __params["q"] = q;
        SFrameEvent __e = new SFrameEvent("e", __params);
        SFrameContext __ctx = new SFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_B(SFrameEvent __e) {
        if (__e._message == "e") {
        }
    }

    private void _state_A(SFrameEvent __e) {
        if (__e._message == "e") {
            var p = (object) __e._parameters["p"];
            var q = (object) __e._parameters["q"];
            { var __new_compartment = new SCompartment("B");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "g") {
            var x = (object) __e._parameters["x"];
            ;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..1");
        try {
            S s = new S();
            s.e(0, 0);
            Console.WriteLine("ok 1 - multi_handler_manifest");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - multi_handler_manifest # " + ex);
        }
    }
}
