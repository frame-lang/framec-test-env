using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class SimpleDockerFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SimpleDockerFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SimpleDockerFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SimpleDockerFrameContext {
    public SimpleDockerFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SimpleDockerFrameContext(SimpleDockerFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SimpleDockerCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SimpleDockerFrameEvent forward_event;
    public SimpleDockerCompartment parent_compartment;

    public SimpleDockerCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SimpleDockerCompartment Copy() {
        SimpleDockerCompartment c = new SimpleDockerCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SimpleDocker {
    private List<SimpleDockerCompartment> _state_stack;
    private SimpleDockerCompartment __compartment;
    private SimpleDockerCompartment __next_compartment;
    private List<SimpleDockerFrameContext> _context_stack;

    public SimpleDocker() {
        _state_stack = new List<SimpleDockerCompartment>();
        _context_stack = new List<SimpleDockerFrameContext>();
        __compartment = new SimpleDockerCompartment("Start");
        __next_compartment = null;
        SimpleDockerFrameEvent __frame_event = new SimpleDockerFrameEvent("$>");
        SimpleDockerFrameContext __ctx = new SimpleDockerFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(SimpleDockerFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SimpleDockerFrameEvent exit_event = new SimpleDockerFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SimpleDockerFrameEvent enter_event = new SimpleDockerFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    SimpleDockerFrameEvent enter_event = new SimpleDockerFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SimpleDockerFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "End") {
            _state_End(__e);
        }
    }

    private void __transition(SimpleDockerCompartment next) {
        __next_compartment = next;
    }

    public void run() {
        SimpleDockerFrameEvent __e = new SimpleDockerFrameEvent("run");
        SimpleDockerFrameContext __ctx = new SimpleDockerFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Start(SimpleDockerFrameEvent __e) {
        if (__e._message == "run") {
            Console.WriteLine("SUCCESS: Hello from Docker");
            { var __new_compartment = new SimpleDockerCompartment("End");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_End(SimpleDockerFrameEvent __e) {

    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..1");
        try {
            SimpleDocker s = new SimpleDocker();
            Console.WriteLine("ok 1 - simple_test");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - simple_test # " + ex);
        }
    }
}
