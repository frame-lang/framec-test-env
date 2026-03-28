using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMEnterExitParamsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMEnterExitParamsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMEnterExitParamsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterExitParamsFrameContext {
    public HSMEnterExitParamsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMEnterExitParamsFrameContext(HSMEnterExitParamsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMEnterExitParamsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMEnterExitParamsFrameEvent forward_event;
    public HSMEnterExitParamsCompartment parent_compartment;

    public HSMEnterExitParamsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMEnterExitParamsCompartment Copy() {
        HSMEnterExitParamsCompartment c = new HSMEnterExitParamsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterExitParams {
    private List<HSMEnterExitParamsCompartment> _state_stack;
    private HSMEnterExitParamsCompartment __compartment;
    private HSMEnterExitParamsCompartment __next_compartment;
    private List<HSMEnterExitParamsFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMEnterExitParams() {
        _state_stack = new List<HSMEnterExitParamsCompartment>();
        _context_stack = new List<HSMEnterExitParamsFrameContext>();
        __compartment = new HSMEnterExitParamsCompartment("Start");
        __next_compartment = null;
        HSMEnterExitParamsFrameEvent __frame_event = new HSMEnterExitParamsFrameEvent("$>");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMEnterExitParamsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterExitParamsFrameEvent exit_event = new HSMEnterExitParamsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterExitParamsFrameEvent enter_event = new HSMEnterExitParamsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMEnterExitParamsFrameEvent enter_event = new HSMEnterExitParamsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterExitParamsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "ChildA") {
            _state_ChildA(__e);
        } else if (state_name == "ChildB") {
            _state_ChildB(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterExitParamsCompartment next) {
        __next_compartment = next;
    }

    public void go_to_a() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("go_to_a");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_to_sibling() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("go_to_sibling");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_back() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("go_back");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("get_log");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("get_state");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_ChildA(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message == "<$") {
            var reason = (string) __compartment.exit_args["0"];
            this.log.Add("ChildA:exit(" + reason + ")");
        } else if (__e._message == "$>") {
            var msg = (string) __compartment.enter_args["0"];
            this.log.Add("ChildA:enter(" + msg + ")");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "ChildA";
            return;
        } else if (__e._message == "go_to_sibling") {
            __compartment.exit_args["0"] = "leaving_A";
            { var __new_compartment = new HSMEnterExitParamsCompartment("ChildB");
            __new_compartment.parent_compartment = __compartment.Copy();
            __new_compartment.enter_args["0"] = "arriving_B";
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Parent(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Parent";
            return;
        }
    }

    private void _state_ChildB(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message == "<$") {
            var reason = (string) __compartment.exit_args["0"];
            this.log.Add("ChildB:exit(" + reason + ")");
        } else if (__e._message == "$>") {
            var msg = (string) __compartment.enter_args["0"];
            this.log.Add("ChildB:enter(" + msg + ")");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "ChildB";
            return;
        } else if (__e._message == "go_back") {
            __compartment.exit_args["0"] = "leaving_B";
            { var __new_compartment = new HSMEnterExitParamsCompartment("ChildA");
            __new_compartment.parent_compartment = __compartment.Copy();
            __new_compartment.enter_args["0"] = "returning_A";
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Start(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Start";
            return;
        } else if (__e._message == "go_to_a") {
            { var __new_compartment = new HSMEnterExitParamsCompartment("ChildA");
            __new_compartment.parent_compartment = __compartment.Copy();
            __new_compartment.enter_args["0"] = "starting";
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 49: HSM Enter/Exit with Params ===");
        var s = new HSMEnterExitParams();

        // First go to ChildA with enter params
        s.go_to_a();
        var log = (List<object>)s.get_log();
        if (!log.Contains("ChildA:enter(starting)")) {
            Console.WriteLine("FAIL: Expected ChildA:enter(starting), got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.5.0: Initial transition with enter params - PASS");

        // TC2.5.1: Exit params passed correctly
        s.go_to_sibling();
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildA:exit(leaving_A)")) {
            Console.WriteLine("FAIL: Expected exit with param, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.5.1: Exit params passed correctly - PASS");

        // TC2.5.2: Enter params passed to target state
        if (!log.Contains("ChildB:enter(arriving_B)")) {
            Console.WriteLine("FAIL: Expected enter with param, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if ((string)s.get_state() != "ChildB") {
            Console.WriteLine("FAIL: Expected ChildB, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.5.2: Enter params passed to target - PASS");

        // TC2.5.3: Return transition with different params
        s.go_back();
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildB:exit(leaving_B)")) {
            Console.WriteLine("FAIL: Expected ChildB exit, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("ChildA:enter(returning_A)")) {
            Console.WriteLine("FAIL: Expected ChildA enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.5.3: Return transition with params - PASS");

        Console.WriteLine("PASS: HSM enter/exit with params works correctly");
    }
}
