using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class ForwardEnterFirstFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public ForwardEnterFirstFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public ForwardEnterFirstFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ForwardEnterFirstFrameContext {
    public ForwardEnterFirstFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public ForwardEnterFirstFrameContext(ForwardEnterFirstFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class ForwardEnterFirstCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public ForwardEnterFirstFrameEvent forward_event;
    public ForwardEnterFirstCompartment parent_compartment;

    public ForwardEnterFirstCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public ForwardEnterFirstCompartment Copy() {
        ForwardEnterFirstCompartment c = new ForwardEnterFirstCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ForwardEnterFirst {
    private List<ForwardEnterFirstCompartment> _state_stack;
    private ForwardEnterFirstCompartment __compartment;
    private ForwardEnterFirstCompartment __next_compartment;
    private List<ForwardEnterFirstFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public ForwardEnterFirst() {
        _state_stack = new List<ForwardEnterFirstCompartment>();
        _context_stack = new List<ForwardEnterFirstFrameContext>();
        __compartment = new ForwardEnterFirstCompartment("Idle");
        __next_compartment = null;
        ForwardEnterFirstFrameEvent __frame_event = new ForwardEnterFirstFrameEvent("$>");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(ForwardEnterFirstFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ForwardEnterFirstFrameEvent exit_event = new ForwardEnterFirstFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ForwardEnterFirstFrameEvent enter_event = new ForwardEnterFirstFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    ForwardEnterFirstFrameEvent enter_event = new ForwardEnterFirstFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ForwardEnterFirstFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Working") {
            _state_Working(__e);
        }
    }

    private void __transition(ForwardEnterFirstCompartment next) {
        __next_compartment = next;
    }

    public void process() {
        ForwardEnterFirstFrameEvent __e = new ForwardEnterFirstFrameEvent("process");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int get_counter() {
        ForwardEnterFirstFrameEvent __e = new ForwardEnterFirstFrameEvent("get_counter");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public List<object> get_log() {
        ForwardEnterFirstFrameEvent __e = new ForwardEnterFirstFrameEvent("get_log");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Working(ForwardEnterFirstFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Working") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("counter")) {
                __sv_comp.state_vars["counter"] = 100;
            }
            this.log.Add("Working:enter");
        } else if (__e._message == "get_counter") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["counter"];
            return;
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "process") {
            this.log.Add("Working:process:counter=" + (int) __sv_comp.state_vars["counter"]);
            __sv_comp.state_vars["counter"] = (int) __sv_comp.state_vars["counter"] + 1;
        }
    }

    private void _state_Idle(ForwardEnterFirstFrameEvent __e) {
        if (__e._message == "get_counter") {
            _context_stack[_context_stack.Count - 1]._return = -1;
            return;
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "process") {
            { var __new_compartment = new ForwardEnterFirstCompartment("Working");
            __new_compartment.parent_compartment = __compartment.Copy();
            __new_compartment.forward_event = __e;
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 29: Forward Enter First ===");
        var s = new ForwardEnterFirst();

        if ((int)s.get_counter() != -1) {
            Console.WriteLine("FAIL: Expected -1 in Idle");
            Environment.Exit(1);
        }

        s.process();

        var counter = (int)s.get_counter();
        var log = (List<object>)s.get_log();
        Console.WriteLine("Counter after forward: " + counter);
        Console.WriteLine("Log: [" + string.Join(", ", log) + "]");

        if (!log.Contains("Working:enter")) {
            Console.WriteLine("FAIL: Expected 'Working:enter' in log: " + string.Join(", ", log));
            Environment.Exit(1);
        }

        if (!log.Contains("Working:process:counter=100")) {
            Console.WriteLine("FAIL: Expected 'Working:process:counter=100' in log: " + string.Join(", ", log));
            Environment.Exit(1);
        }

        if (counter != 101) {
            Console.WriteLine("FAIL: Expected counter=101, got " + counter);
            Environment.Exit(1);
        }

        int enterIdx = log.IndexOf("Working:enter");
        int processIdx = log.IndexOf("Working:process:counter=100");
        if (enterIdx >= processIdx) {
            Console.WriteLine("FAIL: $> should run before process: " + string.Join(", ", log));
            Environment.Exit(1);
        }

        Console.WriteLine("PASS: Forward sends $> first for non-$> events");
    }
}
