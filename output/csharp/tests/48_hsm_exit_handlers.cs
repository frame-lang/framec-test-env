using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMExitHandlersFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMExitHandlersFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMExitHandlersFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMExitHandlersFrameContext {
    public HSMExitHandlersFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMExitHandlersFrameContext(HSMExitHandlersFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMExitHandlersCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMExitHandlersFrameEvent forward_event;
    public HSMExitHandlersCompartment parent_compartment;

    public HSMExitHandlersCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMExitHandlersCompartment Copy() {
        HSMExitHandlersCompartment c = new HSMExitHandlersCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMExitHandlers {
    private List<HSMExitHandlersCompartment> _state_stack;
    private HSMExitHandlersCompartment __compartment;
    private HSMExitHandlersCompartment __next_compartment;
    private List<HSMExitHandlersFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMExitHandlers() {
        _state_stack = new List<HSMExitHandlersCompartment>();
        _context_stack = new List<HSMExitHandlersFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMExitHandlersCompartment("Parent");
        this.__compartment = new HSMExitHandlersCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMExitHandlersFrameEvent __frame_event = new HSMExitHandlersFrameEvent("$>");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMExitHandlersFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMExitHandlersFrameEvent exit_event = new HSMExitHandlersFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMExitHandlersFrameEvent enter_event = new HSMExitHandlersFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMExitHandlersFrameEvent enter_event = new HSMExitHandlersFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMExitHandlersFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        } else if (state_name == "Other") {
            _state_Other(__e);
        }
    }

    private void __transition(HSMExitHandlersCompartment next) {
        __next_compartment = next;
    }

    public void go_to_other() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("go_to_other");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_to_parent() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("go_to_parent");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_to_child() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("go_to_child");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("get_log");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("get_state");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_child_var() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("get_child_var");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Other(HSMExitHandlersFrameEvent __e) {
        if (__e._message == "$>") {
            this.log.Add("Other:enter");
        } else if (__e._message == "get_child_var") {
            _context_stack[_context_stack.Count - 1]._return = -1;
            return;
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Other";
            return;
        } else if (__e._message == "go_to_child") {
            { var __new_compartment = new HSMExitHandlersCompartment("Child");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "go_to_parent") {
            { var __new_compartment = new HSMExitHandlersCompartment("Parent");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Child(HSMExitHandlersFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Child") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "<$") {
            int val = (int) __sv_comp.state_vars["child_var"];
            this.log.Add("Child:exit(var=" + val + ")");
        } else if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("child_var")) {
                __sv_comp.state_vars["child_var"] = 42;
            }
            this.log.Add("Child:enter");
        } else if (__e._message == "get_child_var") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["child_var"];
            return;
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Child";
            return;
        } else if (__e._message == "go_to_other") {
            { var __new_compartment = new HSMExitHandlersCompartment("Other");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "go_to_parent") {
            { var __new_compartment = new HSMExitHandlersCompartment("Parent");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Parent(HSMExitHandlersFrameEvent __e) {
        if (__e._message == "<$") {
            this.log.Add("Parent:exit");
        } else if (__e._message == "$>") {
            this.log.Add("Parent:enter");
        } else if (__e._message == "get_child_var") {
            _context_stack[_context_stack.Count - 1]._return = -1;
            return;
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Parent";
            return;
        } else if (__e._message == "go_to_child") {
            { var __new_compartment = new HSMExitHandlersCompartment("Child");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "go_to_other") {
            { var __new_compartment = new HSMExitHandlersCompartment("Other");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 48: HSM Exit Handlers ===");
        var s = new HSMExitHandlers();

        // Initial state is Child
        var log = (List<object>)s.get_log();
        if (!log.Contains("Child:enter")) {
            Console.WriteLine("FAIL: Expected Child:enter on init, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if ((string)s.get_state() != "Child") {
            Console.WriteLine("FAIL: Expected Child, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.4.0: Initial state is Child with enter - PASS");

        // TC2.4.1: Child exit fires when transitioning out of child
        s.go_to_other();
        log = (List<object>)s.get_log();
        if (!log.Contains("Child:exit(var=42)")) {
            Console.WriteLine("FAIL: Expected Child:exit, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Other:enter")) {
            Console.WriteLine("FAIL: Expected Other:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.4.1: Child exit fires when transitioning out - PASS");

        // TC2.4.2: Parent exit does NOT fire when transitioning out of child
        if (log.Contains("Parent:exit")) {
            Console.WriteLine("FAIL: Parent:exit should NOT fire for child exit, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.4.2: Parent exit NOT fired for child exit - PASS");

        // TC2.4.3: Exit handler can access child's state variables (verified by var=42 in log)
        Console.WriteLine("TC2.4.3: Exit handler accesses state var (var=42) - PASS");

        // TC2.4.4: Parent exit fires when transitioning out of Parent
        s.go_to_parent();
        log = (List<object>)s.get_log();
        if (!log.Contains("Parent:enter")) {
            Console.WriteLine("FAIL: Expected Parent:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }

        s.go_to_other();
        log = (List<object>)s.get_log();
        if (!log.Contains("Parent:exit")) {
            Console.WriteLine("FAIL: Expected Parent:exit, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.4.4: Parent exit fires when leaving parent - PASS");

        Console.WriteLine("PASS: HSM exit handlers work correctly");
    }
}
