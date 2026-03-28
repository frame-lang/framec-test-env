using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMEnterChildOnlyFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMEnterChildOnlyFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMEnterChildOnlyFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterChildOnlyFrameContext {
    public HSMEnterChildOnlyFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMEnterChildOnlyFrameContext(HSMEnterChildOnlyFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMEnterChildOnlyCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMEnterChildOnlyFrameEvent forward_event;
    public HSMEnterChildOnlyCompartment parent_compartment;

    public HSMEnterChildOnlyCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMEnterChildOnlyCompartment Copy() {
        HSMEnterChildOnlyCompartment c = new HSMEnterChildOnlyCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterChildOnly {
    private List<HSMEnterChildOnlyCompartment> _state_stack;
    private HSMEnterChildOnlyCompartment __compartment;
    private HSMEnterChildOnlyCompartment __next_compartment;
    private List<HSMEnterChildOnlyFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMEnterChildOnly() {
        _state_stack = new List<HSMEnterChildOnlyCompartment>();
        _context_stack = new List<HSMEnterChildOnlyFrameContext>();
        __compartment = new HSMEnterChildOnlyCompartment("Start");
        __next_compartment = null;
        HSMEnterChildOnlyFrameEvent __frame_event = new HSMEnterChildOnlyFrameEvent("$>");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMEnterChildOnlyFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterChildOnlyFrameEvent exit_event = new HSMEnterChildOnlyFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterChildOnlyFrameEvent enter_event = new HSMEnterChildOnlyFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMEnterChildOnlyFrameEvent enter_event = new HSMEnterChildOnlyFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterChildOnlyFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterChildOnlyCompartment next) {
        __next_compartment = next;
    }

    public void go_to_child() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("go_to_child");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forward_action() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("forward_action");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("get_log");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("get_state");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Child(HSMEnterChildOnlyFrameEvent __e) {
        if (__e._message == "$>") {
            this.log.Add("Child:enter");
        } else if (__e._message == "forward_action") {
            this.log.Add("Child:forward");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Child";
            return;
        }
    }

    private void _state_Start(HSMEnterChildOnlyFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Start";
            return;
        } else if (__e._message == "go_to_child") {
            { var __new_compartment = new HSMEnterChildOnlyCompartment("Child");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Parent(HSMEnterChildOnlyFrameEvent __e) {
        if (__e._message == "forward_action") {
            this.log.Add("Parent:forward_action");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Parent";
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 45: HSM Enter in Child Only ===");
        var s = new HSMEnterChildOnly();

        // Start state has no enter
        if ((string)s.get_state() != "Start") {
            Console.WriteLine("FAIL: Expected Start, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.1.0: Initial state is Start - PASS");

        // TC2.1.1: Child enter handler fires on entry
        s.go_to_child();
        var log = (List<object>)s.get_log();
        if (!log.Contains("Child:enter")) {
            Console.WriteLine("FAIL: Expected Child:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if ((string)s.get_state() != "Child") {
            Console.WriteLine("FAIL: Expected Child, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.1.1: Child enter handler fires - PASS");

        // TC2.1.2: No error when parent lacks enter (verified by compilation/execution)
        Console.WriteLine("TC2.1.2: No error when parent lacks enter - PASS");

        // TC2.1.3: Forward to parent works without parent having enter
        s.forward_action();
        log = (List<object>)s.get_log();
        if (!log.Contains("Child:forward")) {
            Console.WriteLine("FAIL: Expected Child:forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Parent:forward_action")) {
            Console.WriteLine("FAIL: Expected Parent handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.1.3: Forward works without parent enter - PASS");

        Console.WriteLine("PASS: HSM enter in child only works correctly");
    }
}
