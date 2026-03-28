using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMEnterParentOnlyFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMEnterParentOnlyFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMEnterParentOnlyFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterParentOnlyFrameContext {
    public HSMEnterParentOnlyFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMEnterParentOnlyFrameContext(HSMEnterParentOnlyFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMEnterParentOnlyCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMEnterParentOnlyFrameEvent forward_event;
    public HSMEnterParentOnlyCompartment parent_compartment;

    public HSMEnterParentOnlyCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMEnterParentOnlyCompartment Copy() {
        HSMEnterParentOnlyCompartment c = new HSMEnterParentOnlyCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterParentOnly {
    private List<HSMEnterParentOnlyCompartment> _state_stack;
    private HSMEnterParentOnlyCompartment __compartment;
    private HSMEnterParentOnlyCompartment __next_compartment;
    private List<HSMEnterParentOnlyFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMEnterParentOnly() {
        _state_stack = new List<HSMEnterParentOnlyCompartment>();
        _context_stack = new List<HSMEnterParentOnlyFrameContext>();
        __compartment = new HSMEnterParentOnlyCompartment("Start");
        __next_compartment = null;
        HSMEnterParentOnlyFrameEvent __frame_event = new HSMEnterParentOnlyFrameEvent("$>");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMEnterParentOnlyFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterParentOnlyFrameEvent exit_event = new HSMEnterParentOnlyFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterParentOnlyFrameEvent enter_event = new HSMEnterParentOnlyFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMEnterParentOnlyFrameEvent enter_event = new HSMEnterParentOnlyFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterParentOnlyFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterParentOnlyCompartment next) {
        __next_compartment = next;
    }

    public void go_to_child() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("go_to_child");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_to_parent() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("go_to_parent");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("get_log");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("get_state");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Start(HSMEnterParentOnlyFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Start";
            return;
        } else if (__e._message == "go_to_child") {
            { var __new_compartment = new HSMEnterParentOnlyCompartment("Child");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "go_to_parent") {
            { var __new_compartment = new HSMEnterParentOnlyCompartment("Parent");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Parent(HSMEnterParentOnlyFrameEvent __e) {
        if (__e._message == "$>") {
            this.log.Add("Parent:enter");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Parent";
            return;
        } else if (__e._message == "go_to_child") {
            { var __new_compartment = new HSMEnterParentOnlyCompartment("Child");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Child(HSMEnterParentOnlyFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Child";
            return;
        } else if (__e._message == "go_to_parent") {
            { var __new_compartment = new HSMEnterParentOnlyCompartment("Parent");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 46: HSM Enter in Parent Only ===");
        var s = new HSMEnterParentOnly();

        // TC2.2.1: Child enters without error (no enter handler)
        s.go_to_child();
        if ((string)s.get_state() != "Child") {
            Console.WriteLine("FAIL: Expected Child, got " + s.get_state());
            Environment.Exit(1);
        }
        var log = (List<object>)s.get_log();
        Console.WriteLine("TC2.2.1: Child enters without error (log: [" + string.Join(", ", log) + "]) - PASS");

        // TC2.2.2: Parent's enter does NOT auto-fire when child is entered
        if (log.Contains("Parent:enter")) {
            Console.WriteLine("FAIL: Parent:enter should NOT fire for child entry, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.2.2: Parent enter NOT auto-fired for child - PASS");

        // TC2.2.3: Parent enter only fires when transitioning directly TO parent
        s.go_to_parent();
        if ((string)s.get_state() != "Parent") {
            Console.WriteLine("FAIL: Expected Parent, got " + s.get_state());
            Environment.Exit(1);
        }
        log = (List<object>)s.get_log();
        if (!log.Contains("Parent:enter")) {
            Console.WriteLine("FAIL: Expected Parent:enter when transitioning to Parent, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.2.3: Parent enter fires when transitioning to Parent - PASS");

        // TC2.2.4: Going back to child from parent
        s.go_to_child();
        if ((string)s.get_state() != "Child") {
            Console.WriteLine("FAIL: Expected Child, got " + s.get_state());
            Environment.Exit(1);
        }
        log = (List<object>)s.get_log();
        int count = 0;
        foreach (var item in log) {
            if (item.Equals("Parent:enter")) count++;
        }
        if (count != 1) {
            Console.WriteLine("FAIL: Expected exactly 1 Parent:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.2.4: Return to child, parent enter count unchanged - PASS");

        Console.WriteLine("PASS: HSM enter in parent only works correctly");
    }
}
