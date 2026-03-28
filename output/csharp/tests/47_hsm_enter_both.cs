using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMEnterBothFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMEnterBothFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMEnterBothFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterBothFrameContext {
    public HSMEnterBothFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMEnterBothFrameContext(HSMEnterBothFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMEnterBothCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMEnterBothFrameEvent forward_event;
    public HSMEnterBothCompartment parent_compartment;

    public HSMEnterBothCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMEnterBothCompartment Copy() {
        HSMEnterBothCompartment c = new HSMEnterBothCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterBoth {
    private List<HSMEnterBothCompartment> _state_stack;
    private HSMEnterBothCompartment __compartment;
    private HSMEnterBothCompartment __next_compartment;
    private List<HSMEnterBothFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMEnterBoth() {
        _state_stack = new List<HSMEnterBothCompartment>();
        _context_stack = new List<HSMEnterBothFrameContext>();
        __compartment = new HSMEnterBothCompartment("Start");
        __next_compartment = null;
        HSMEnterBothFrameEvent __frame_event = new HSMEnterBothFrameEvent("$>");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMEnterBothFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterBothFrameEvent exit_event = new HSMEnterBothFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterBothFrameEvent enter_event = new HSMEnterBothFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMEnterBothFrameEvent enter_event = new HSMEnterBothFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterBothFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterBothCompartment next) {
        __next_compartment = next;
    }

    public void go_to_child() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("go_to_child");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_to_parent() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("go_to_parent");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("get_log");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("get_state");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Start(HSMEnterBothFrameEvent __e) {
        if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Start";
            return;
        } else if (__e._message == "go_to_child") {
            { var __new_compartment = new HSMEnterBothCompartment("Child");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "go_to_parent") {
            { var __new_compartment = new HSMEnterBothCompartment("Parent");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Parent(HSMEnterBothFrameEvent __e) {
        if (__e._message == "$>") {
            this.log.Add("Parent:enter");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Parent";
            return;
        } else if (__e._message == "go_to_child") {
            { var __new_compartment = new HSMEnterBothCompartment("Child");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Child(HSMEnterBothFrameEvent __e) {
        if (__e._message == "$>") {
            this.log.Add("Child:enter");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Child";
            return;
        } else if (__e._message == "go_to_parent") {
            { var __new_compartment = new HSMEnterBothCompartment("Parent");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 47: HSM Enter in Both ===");
        var s = new HSMEnterBoth();

        // TC2.3.1: Only child's enter fires when entering child
        s.go_to_child();
        var log = (List<object>)s.get_log();
        if (!log.Contains("Child:enter")) {
            Console.WriteLine("FAIL: Expected Child:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (log.Contains("Parent:enter")) {
            Console.WriteLine("FAIL: Parent:enter should NOT fire when entering child, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if ((string)s.get_state() != "Child") {
            Console.WriteLine("FAIL: Expected Child, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.3.1: Only child's enter fires when entering child - PASS");

        // TC2.3.2: Parent's enter fires only when transitioning to parent
        s.go_to_parent();
        log = (List<object>)s.get_log();
        if (!log.Contains("Parent:enter")) {
            Console.WriteLine("FAIL: Expected Parent:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if ((string)s.get_state() != "Parent") {
            Console.WriteLine("FAIL: Expected Parent, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.3.2: Parent's enter fires when transitioning to parent - PASS");

        // TC2.3.3: No implicit cascading - counts should be exactly 1 each
        int childCount = 0;
        int parentCount = 0;
        foreach (var item in log) {
            if (item.Equals("Child:enter")) childCount++;
            if (item.Equals("Parent:enter")) parentCount++;
        }
        if (childCount != 1) {
            Console.WriteLine("FAIL: Expected exactly 1 Child:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (parentCount != 1) {
            Console.WriteLine("FAIL: Expected exactly 1 Parent:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.3.3: No implicit cascading of enter handlers - PASS");

        // TC2.3.4: Going back to child fires child enter again
        s.go_to_child();
        log = (List<object>)s.get_log();
        int childCount2 = 0;
        int parentCount2 = 0;
        foreach (var item in log) {
            if (item.Equals("Child:enter")) childCount2++;
            if (item.Equals("Parent:enter")) parentCount2++;
        }
        if (childCount2 != 2) {
            Console.WriteLine("FAIL: Expected 2 Child:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (parentCount2 != 1) {
            Console.WriteLine("FAIL: Expected still 1 Parent:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC2.3.4: Re-entering child fires child enter again - PASS");

        Console.WriteLine("PASS: HSM enter in both works correctly");
    }
}
