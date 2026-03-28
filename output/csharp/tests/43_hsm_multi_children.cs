using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMMultiChildrenFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMMultiChildrenFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMMultiChildrenFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMMultiChildrenFrameContext {
    public HSMMultiChildrenFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMMultiChildrenFrameContext(HSMMultiChildrenFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMMultiChildrenCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMMultiChildrenFrameEvent forward_event;
    public HSMMultiChildrenCompartment parent_compartment;

    public HSMMultiChildrenCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMMultiChildrenCompartment Copy() {
        HSMMultiChildrenCompartment c = new HSMMultiChildrenCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMMultiChildren {
    private List<HSMMultiChildrenCompartment> _state_stack;
    private HSMMultiChildrenCompartment __compartment;
    private HSMMultiChildrenCompartment __next_compartment;
    private List<HSMMultiChildrenFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMMultiChildren() {
        _state_stack = new List<HSMMultiChildrenCompartment>();
        _context_stack = new List<HSMMultiChildrenFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMMultiChildrenCompartment("Parent");
        this.__compartment = new HSMMultiChildrenCompartment("ChildA");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMMultiChildrenFrameEvent __frame_event = new HSMMultiChildrenFrameEvent("$>");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMMultiChildrenFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMMultiChildrenFrameEvent exit_event = new HSMMultiChildrenFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMMultiChildrenFrameEvent enter_event = new HSMMultiChildrenFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMMultiChildrenFrameEvent enter_event = new HSMMultiChildrenFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMMultiChildrenFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "ChildA") {
            _state_ChildA(__e);
        } else if (state_name == "ChildB") {
            _state_ChildB(__e);
        } else if (state_name == "ChildC") {
            _state_ChildC(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMMultiChildrenCompartment next) {
        __next_compartment = next;
    }

    public void start_a() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("start_a");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void start_b() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("start_b");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void start_c() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("start_c");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void do_action() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("do_action");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forward_action() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("forward_action");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("get_log");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("get_state");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Parent(HSMMultiChildrenFrameEvent __e) {
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

    private void _state_ChildB(HSMMultiChildrenFrameEvent __e) {
        if (__e._message == "do_action") {
            this.log.Add("ChildB:do_action");
        } else if (__e._message == "forward_action") {
            this.log.Add("ChildB:forward_action");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "ChildB";
            return;
        } else if (__e._message == "start_a") {
            { var __new_compartment = new HSMMultiChildrenCompartment("ChildA");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "start_b") {
            // stay
        } else if (__e._message == "start_c") {
            { var __new_compartment = new HSMMultiChildrenCompartment("ChildC");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_ChildC(HSMMultiChildrenFrameEvent __e) {
        if (__e._message == "do_action") {
            this.log.Add("ChildC:do_action");
        } else if (__e._message == "forward_action") {
            this.log.Add("ChildC:forward_action");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "ChildC";
            return;
        } else if (__e._message == "start_a") {
            { var __new_compartment = new HSMMultiChildrenCompartment("ChildA");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "start_b") {
            { var __new_compartment = new HSMMultiChildrenCompartment("ChildB");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "start_c") {
            // stay
        }
    }

    private void _state_ChildA(HSMMultiChildrenFrameEvent __e) {
        if (__e._message == "do_action") {
            this.log.Add("ChildA:do_action");
        } else if (__e._message == "forward_action") {
            this.log.Add("ChildA:forward_action");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "ChildA";
            return;
        } else if (__e._message == "start_a") {
            // stay
        } else if (__e._message == "start_b") {
            { var __new_compartment = new HSMMultiChildrenCompartment("ChildB");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "start_c") {
            { var __new_compartment = new HSMMultiChildrenCompartment("ChildC");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 43: HSM Multiple Children ===");
        var s = new HSMMultiChildren();

        // TC1.3.1: Multiple children declare same parent (verified by compilation)
        Console.WriteLine("TC1.3.1: Multiple children with same parent compiles - PASS");

        // Start in ChildA
        if ((string)s.get_state() != "ChildA") {
            Console.WriteLine("FAIL: Expected ChildA, got " + s.get_state());
            Environment.Exit(1);
        }

        // TC1.3.2: ChildA can forward to shared parent
        s.forward_action();
        var log = (List<object>)s.get_log();
        if (!log.Contains("ChildA:forward_action")) {
            Console.WriteLine("FAIL: Expected ChildA forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Parent:forward_action")) {
            Console.WriteLine("FAIL: Expected Parent handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.3.2: ChildA forwards to parent - PASS");

        // TC1.3.3: Transition to sibling
        s.start_b();
        if ((string)s.get_state() != "ChildB") {
            Console.WriteLine("FAIL: Expected ChildB after transition, got " + s.get_state());
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.3.3: Transition A->B works - PASS");

        // TC1.3.4: ChildB can also forward to same parent
        s.forward_action();
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildB:forward_action")) {
            Console.WriteLine("FAIL: Expected ChildB forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        int parentCount = 0;
        foreach (var item in log) {
            if (item.Equals("Parent:forward_action")) parentCount++;
        }
        if (parentCount != 2) {
            Console.WriteLine("FAIL: Expected 2 Parent forwards, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.3.4: ChildB forwards to same parent - PASS");

        // TC1.3.5: Transition to ChildC
        s.start_c();
        if ((string)s.get_state() != "ChildC") {
            Console.WriteLine("FAIL: Expected ChildC, got " + s.get_state());
            Environment.Exit(1);
        }
        s.forward_action();
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildC:forward_action")) {
            Console.WriteLine("FAIL: Expected ChildC forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        int parentCount2 = 0;
        foreach (var item in log) {
            if (item.Equals("Parent:forward_action")) parentCount2++;
        }
        if (parentCount2 != 3) {
            Console.WriteLine("FAIL: Expected 3 Parent forwards, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.3.5: ChildC forwards to same parent - PASS");

        // TC1.3.6: Each sibling maintains independent actions
        s.start_a();
        s.do_action();
        s.start_b();
        s.do_action();
        s.start_c();
        s.do_action();
        log = (List<object>)s.get_log();
        if (!log.Contains("ChildA:do_action")) {
            Console.WriteLine("FAIL: Expected ChildA action");
            Environment.Exit(1);
        }
        if (!log.Contains("ChildB:do_action")) {
            Console.WriteLine("FAIL: Expected ChildB action");
            Environment.Exit(1);
        }
        if (!log.Contains("ChildC:do_action")) {
            Console.WriteLine("FAIL: Expected ChildC action");
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.3.6: Each sibling has independent handlers - PASS");

        Console.WriteLine("PASS: HSM multiple children work correctly");
    }
}
