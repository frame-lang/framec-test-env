using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMSiblingTransitionsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMSiblingTransitionsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMSiblingTransitionsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMSiblingTransitionsFrameContext {
    public HSMSiblingTransitionsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMSiblingTransitionsFrameContext(HSMSiblingTransitionsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMSiblingTransitionsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMSiblingTransitionsFrameEvent forward_event;
    public HSMSiblingTransitionsCompartment parent_compartment;

    public HSMSiblingTransitionsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMSiblingTransitionsCompartment Copy() {
        HSMSiblingTransitionsCompartment c = new HSMSiblingTransitionsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMSiblingTransitions {
    private List<HSMSiblingTransitionsCompartment> _state_stack;
    private HSMSiblingTransitionsCompartment __compartment;
    private HSMSiblingTransitionsCompartment __next_compartment;
    private List<HSMSiblingTransitionsFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMSiblingTransitions() {
        _state_stack = new List<HSMSiblingTransitionsCompartment>();
        _context_stack = new List<HSMSiblingTransitionsFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMSiblingTransitionsCompartment("Parent");
        this.__compartment = new HSMSiblingTransitionsCompartment("ChildA");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMSiblingTransitionsFrameEvent __frame_event = new HSMSiblingTransitionsFrameEvent("$>");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMSiblingTransitionsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMSiblingTransitionsFrameEvent exit_event = new HSMSiblingTransitionsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMSiblingTransitionsFrameEvent enter_event = new HSMSiblingTransitionsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMSiblingTransitionsFrameEvent enter_event = new HSMSiblingTransitionsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMSiblingTransitionsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "ChildA") {
            _state_ChildA(__e);
        } else if (state_name == "ChildB") {
            _state_ChildB(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMSiblingTransitionsCompartment next) {
        __next_compartment = next;
    }

    public void go_to_b() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("go_to_b");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_to_a() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("go_to_a");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forward_action() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("forward_action");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("get_log");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("get_state");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_ChildB(HSMSiblingTransitionsFrameEvent __e) {
        if (__e._message == "<$") {
            this.log.Add("ChildB:exit");
        } else if (__e._message == "$>") {
            this.log.Add("ChildB:enter");
        } else if (__e._message == "forward_action") {
            this.log.Add("ChildB:forward");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "ChildB";
            return;
        } else if (__e._message == "go_to_a") {
            this.log.Add("ChildB:go_to_a");
            { var __new_compartment = new HSMSiblingTransitionsCompartment("ChildA");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Parent(HSMSiblingTransitionsFrameEvent __e) {
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

    private void _state_ChildA(HSMSiblingTransitionsFrameEvent __e) {
        if (__e._message == "<$") {
            this.log.Add("ChildA:exit");
        } else if (__e._message == "$>") {
            this.log.Add("ChildA:enter");
        } else if (__e._message == "forward_action") {
            this.log.Add("ChildA:forward");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "ChildA";
            return;
        } else if (__e._message == "go_to_b") {
            this.log.Add("ChildA:go_to_b");
            { var __new_compartment = new HSMSiblingTransitionsCompartment("ChildB");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 44: HSM Sibling Transitions ===");
        var s = new HSMSiblingTransitions();

        // Initial state is ChildA with enter handler fired
        var log = (List<object>)s.get_log();
        if (!log.Contains("ChildA:enter")) {
            Console.WriteLine("FAIL: Expected ChildA:enter on init, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if ((string)s.get_state() != "ChildA") {
            Console.WriteLine("FAIL: Expected ChildA, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.4.0: Initial state ChildA with enter - PASS");

        // TC1.4.1: Transition from ChildA to ChildB
        s.go_to_b();
        if ((string)s.get_state() != "ChildB") {
            Console.WriteLine("FAIL: Expected ChildB, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.4.1: Transition A->B works - PASS");

        // TC1.4.2: Exit handler fired on source
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildA:exit")) {
            Console.WriteLine("FAIL: Expected ChildA:exit, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.4.2: Exit handler fires on source - PASS");

        // TC1.4.3: Enter handler fired on target
        if (!log.Contains("ChildB:enter")) {
            Console.WriteLine("FAIL: Expected ChildB:enter, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.4.3: Enter handler fires on target - PASS");

        // TC1.4.4: Parent relationship preserved - ChildB can forward
        s.forward_action();
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildB:forward")) {
            Console.WriteLine("FAIL: Expected ChildB:forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Parent:forward_action")) {
            Console.WriteLine("FAIL: Expected Parent handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.4.4: Parent relationship preserved - PASS");

        // TC1.4.5: Transition back to ChildA
        s.go_to_a();
        if ((string)s.get_state() != "ChildA") {
            Console.WriteLine("FAIL: Expected ChildA, got " + s.get_state());
            Environment.Exit(1);
        }
        log = (List<object>)s.get_log();
        int exitBCount = 0;
        int enterACount = 0;
        foreach (var item in log) {
            if (item.Equals("ChildB:exit")) exitBCount++;
            if (item.Equals("ChildA:enter")) enterACount++;
        }
        if (exitBCount != 1) {
            Console.WriteLine("FAIL: Expected ChildB:exit once, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (enterACount != 2) {
            Console.WriteLine("FAIL: Expected ChildA:enter twice, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.4.5: Transition B->A works with enter/exit - PASS");

        // TC1.4.6: ChildA can still forward after returning
        s.forward_action();
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildA:forward")) {
            Console.WriteLine("FAIL: Expected ChildA:forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        int parentCount = 0;
        foreach (var item in log) {
            if (item.Equals("Parent:forward_action")) parentCount++;
        }
        if (parentCount != 2) {
            Console.WriteLine("FAIL: Expected 2 Parent handlers, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.4.6: ChildA forwards after returning - PASS");

        Console.WriteLine("PASS: HSM sibling transitions work correctly");
    }
}
