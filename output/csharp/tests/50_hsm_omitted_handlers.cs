using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMOmittedHandlersFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMOmittedHandlersFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMOmittedHandlersFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMOmittedHandlersFrameContext {
    public HSMOmittedHandlersFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMOmittedHandlersFrameContext(HSMOmittedHandlersFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMOmittedHandlersCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMOmittedHandlersFrameEvent forward_event;
    public HSMOmittedHandlersCompartment parent_compartment;

    public HSMOmittedHandlersCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMOmittedHandlersCompartment Copy() {
        HSMOmittedHandlersCompartment c = new HSMOmittedHandlersCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMOmittedHandlers {
    private List<HSMOmittedHandlersCompartment> _state_stack;
    private HSMOmittedHandlersCompartment __compartment;
    private HSMOmittedHandlersCompartment __next_compartment;
    private List<HSMOmittedHandlersFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMOmittedHandlers() {
        _state_stack = new List<HSMOmittedHandlersCompartment>();
        _context_stack = new List<HSMOmittedHandlersFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMOmittedHandlersCompartment("Parent");
        this.__compartment = new HSMOmittedHandlersCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMOmittedHandlersFrameEvent __frame_event = new HSMOmittedHandlersFrameEvent("$>");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMOmittedHandlersFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMOmittedHandlersFrameEvent exit_event = new HSMOmittedHandlersFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMOmittedHandlersFrameEvent enter_event = new HSMOmittedHandlersFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMOmittedHandlersFrameEvent enter_event = new HSMOmittedHandlersFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMOmittedHandlersFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMOmittedHandlersCompartment next) {
        __next_compartment = next;
    }

    public void handled_by_child() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("handled_by_child");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forwarded_explicitly() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("forwarded_explicitly");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void unhandled_no_forward() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("unhandled_no_forward");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("get_log");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("get_state");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Parent(HSMOmittedHandlersFrameEvent __e) {
        if (__e._message == "forwarded_explicitly") {
            this.log.Add("Parent:forwarded_explicitly");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Parent";
            return;
        } else if (__e._message == "handled_by_child") {
            this.log.Add("Parent:handled_by_child");
        } else if (__e._message == "unhandled_no_forward") {
            this.log.Add("Parent:unhandled_no_forward");
        }
    }

    private void _state_Child(HSMOmittedHandlersFrameEvent __e) {
        if (__e._message == "forwarded_explicitly") {
            this.log.Add("Child:before_forward");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Child";
            return;
        } else if (__e._message == "handled_by_child") {
            this.log.Add("Child:handled_by_child");
        }
    }
}

class HSMDefaultForward2FrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMDefaultForward2FrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMDefaultForward2FrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMDefaultForward2FrameContext {
    public HSMDefaultForward2FrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMDefaultForward2FrameContext(HSMDefaultForward2FrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMDefaultForward2Compartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMDefaultForward2FrameEvent forward_event;
    public HSMDefaultForward2Compartment parent_compartment;

    public HSMDefaultForward2Compartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMDefaultForward2Compartment Copy() {
        HSMDefaultForward2Compartment c = new HSMDefaultForward2Compartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMDefaultForward2 {
    private List<HSMDefaultForward2Compartment> _state_stack;
    private HSMDefaultForward2Compartment __compartment;
    private HSMDefaultForward2Compartment __next_compartment;
    private List<HSMDefaultForward2FrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMDefaultForward2() {
        _state_stack = new List<HSMDefaultForward2Compartment>();
        _context_stack = new List<HSMDefaultForward2FrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMDefaultForward2Compartment("Parent");
        this.__compartment = new HSMDefaultForward2Compartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMDefaultForward2FrameEvent __frame_event = new HSMDefaultForward2FrameEvent("$>");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMDefaultForward2FrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMDefaultForward2FrameEvent exit_event = new HSMDefaultForward2FrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMDefaultForward2FrameEvent enter_event = new HSMDefaultForward2FrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMDefaultForward2FrameEvent enter_event = new HSMDefaultForward2FrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMDefaultForward2FrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMDefaultForward2Compartment next) {
        __next_compartment = next;
    }

    public void child_handled() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("child_handled");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void parent_handled() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("parent_handled");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void both_respond() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("both_respond");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("get_log");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Child(HSMDefaultForward2FrameEvent __e) {
        if (__e._message == "child_handled") {
            this.log.Add("Child:child_handled");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else {
            _state_Parent(__e);
        }
    }

    private void _state_Parent(HSMDefaultForward2FrameEvent __e) {
        if (__e._message == "both_respond") {
            this.log.Add("Parent:both_respond");
        } else if (__e._message == "child_handled") {
            this.log.Add("Parent:child_handled");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "parent_handled") {
            this.log.Add("Parent:parent_handled");
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 50: HSM Omitted Handlers ===");

        // Part 1: Explicit forwarding vs no forwarding
        var s1 = new HSMOmittedHandlers();

        // TC2.6.1: Event handled by child only
        s1.handled_by_child();
        var log = (List<object>)s1.get_log();
        if (!log.Contains("Child:handled_by_child")) {
            Console.WriteLine("FAIL: Expected Child handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (log.Contains("Parent:handled_by_child")) {
            Console.WriteLine("FAIL: Parent should NOT be called, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.6.1: Handled by child, not forwarded - PASS");

        // TC2.6.2: Event explicitly forwarded to parent
        s1.forwarded_explicitly();
        log = (List<object>)s1.get_log();
        if (!log.Contains("Child:before_forward")) {
            Console.WriteLine("FAIL: Expected Child forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Parent:forwarded_explicitly")) {
            Console.WriteLine("FAIL: Expected Parent handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.6.2: Explicitly forwarded to parent - PASS");

        // TC2.6.3: Unhandled event with no forward - silently ignored
        s1.unhandled_no_forward();
        log = (List<object>)s1.get_log();
        if (log.Contains("Parent:unhandled_no_forward")) {
            Console.WriteLine("FAIL: Unhandled should be ignored, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.6.3: Unhandled (no forward) is silently ignored - PASS");

        // Part 2: State-level default forward
        var s2 = new HSMDefaultForward2();

        // TC2.6.4: Event handled by child (no forward despite => $^)
        s2.child_handled();
        log = (List<object>)s2.get_log();
        if (!log.Contains("Child:child_handled")) {
            Console.WriteLine("FAIL: Expected Child handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (log.Contains("Parent:child_handled")) {
            Console.WriteLine("FAIL: Handled by child, not forwarded, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.6.4: Child handles, not forwarded - PASS");

        // TC2.6.5: Unhandled event forwarded via => $^
        s2.parent_handled();
        log = (List<object>)s2.get_log();
        if (!log.Contains("Parent:parent_handled")) {
            Console.WriteLine("FAIL: Expected Parent handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.6.5: Unhandled forwarded via state-level => $^ - PASS");

        // TC2.6.6: Another unhandled event forwarded
        s2.both_respond();
        log = (List<object>)s2.get_log();
        if (!log.Contains("Parent:both_respond")) {
            Console.WriteLine("FAIL: Expected Parent handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.6.6: Default forward works for multiple events - PASS");

        Console.WriteLine("PASS: HSM omitted handlers work correctly");
    }
}
