using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMThreeLevelsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMThreeLevelsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMThreeLevelsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMThreeLevelsFrameContext {
    public HSMThreeLevelsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMThreeLevelsFrameContext(HSMThreeLevelsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMThreeLevelsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMThreeLevelsFrameEvent forward_event;
    public HSMThreeLevelsCompartment parent_compartment;

    public HSMThreeLevelsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMThreeLevelsCompartment Copy() {
        HSMThreeLevelsCompartment c = new HSMThreeLevelsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMThreeLevels {
    private List<HSMThreeLevelsCompartment> _state_stack;
    private HSMThreeLevelsCompartment __compartment;
    private HSMThreeLevelsCompartment __next_compartment;
    private List<HSMThreeLevelsFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMThreeLevels() {
        _state_stack = new List<HSMThreeLevelsCompartment>();
        _context_stack = new List<HSMThreeLevelsFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMThreeLevelsCompartment("Parent");
        __parent_comp_0.state_vars["parent_var"] = 100;
        var __parent_comp_1 = new HSMThreeLevelsCompartment("Child");
        __parent_comp_1.parent_compartment = __parent_comp_0;
        __parent_comp_1.state_vars["child_var"] = 10;
        this.__compartment = new HSMThreeLevelsCompartment("Grandchild");
        this.__compartment.parent_compartment = __parent_comp_1;
        this.__next_compartment = null;
        HSMThreeLevelsFrameEvent __frame_event = new HSMThreeLevelsFrameEvent("$>");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMThreeLevelsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMThreeLevelsFrameEvent exit_event = new HSMThreeLevelsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMThreeLevelsFrameEvent enter_event = new HSMThreeLevelsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMThreeLevelsFrameEvent enter_event = new HSMThreeLevelsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMThreeLevelsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Grandchild") {
            _state_Grandchild(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMThreeLevelsCompartment next) {
        __next_compartment = next;
    }

    public void handle_at_grandchild() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("handle_at_grandchild");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forward_to_child() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("forward_to_child");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forward_to_parent() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("forward_to_parent");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forward_through_all() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("forward_through_all");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("get_log");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Grandchild(HSMThreeLevelsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Grandchild") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("grandchild_var")) {
                __sv_comp.state_vars["grandchild_var"] = 1;
            }
        } else if (__e._message == "forward_through_all") {
            this.log.Add("Grandchild:forward_through_all");
            _state_Child(__e);
        } else if (__e._message == "forward_to_child") {
            this.log.Add("Grandchild:forward_to_child");
            _state_Child(__e);
        } else if (__e._message == "forward_to_parent") {
            this.log.Add("Grandchild:forward_to_parent");
            _state_Child(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "handle_at_grandchild") {
            int val = (int) __sv_comp.state_vars["grandchild_var"];
            this.log.Add("Grandchild:handled(var=" + val + ")");
        }
    }

    private void _state_Child(HSMThreeLevelsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Child") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("child_var")) {
                __sv_comp.state_vars["child_var"] = 10;
            }
        } else if (__e._message == "forward_through_all") {
            int val = (int) __sv_comp.state_vars["child_var"];
            this.log.Add("Child:forward_through_all(var=" + val + ")");
            _state_Parent(__e);
        } else if (__e._message == "forward_to_child") {
            int val = (int) __sv_comp.state_vars["child_var"];
            this.log.Add("Child:handled(var=" + val + ")");
        } else if (__e._message == "forward_to_parent") {
            int val = (int) __sv_comp.state_vars["child_var"];
            this.log.Add("Child:forward_to_parent(var=" + val + ")");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        }
    }

    private void _state_Parent(HSMThreeLevelsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Parent") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("parent_var")) {
                __sv_comp.state_vars["parent_var"] = 100;
            }
        } else if (__e._message == "forward_through_all") {
            int val = (int) __sv_comp.state_vars["parent_var"];
            this.log.Add("Parent:forward_through_all(var=" + val + ")");
        } else if (__e._message == "forward_to_parent") {
            int val = (int) __sv_comp.state_vars["parent_var"];
            this.log.Add("Parent:handled(var=" + val + ")");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 42: HSM Three-Level Hierarchy ===");
        var s = new HSMThreeLevels();

        // TC1.2.1: Three-level hierarchy compiles
        Console.WriteLine("TC1.2.1: Three-level hierarchy compiles - PASS");

        // TC1.2.2: Handle at grandchild (no forward)
        s.handle_at_grandchild();
        var log = (List<object>)s.get_log();
        if (!log.Contains("Grandchild:handled(var=1)")) {
            Console.WriteLine("FAIL: Expected Grandchild handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.2.2: Grandchild handles locally - PASS");

        // TC1.2.3: Forward from grandchild to child
        s.forward_to_child();
        log = (List<object>)s.get_log();
        if (!log.Contains("Grandchild:forward_to_child")) {
            Console.WriteLine("FAIL: Expected Grandchild forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Child:handled(var=10)")) {
            Console.WriteLine("FAIL: Expected Child handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.2.3: Forward grandchild->child - PASS");

        // TC1.2.4: Forward from grandchild through child to parent
        s.forward_to_parent();
        log = (List<object>)s.get_log();
        if (!log.Contains("Grandchild:forward_to_parent")) {
            Console.WriteLine("FAIL: Expected Grandchild forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Child:forward_to_parent(var=10)")) {
            Console.WriteLine("FAIL: Expected Child forward, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Parent:handled(var=100)")) {
            Console.WriteLine("FAIL: Expected Parent handler, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.2.4: Forward grandchild->child->parent - PASS");

        // TC1.2.5: Forward through entire chain
        s.forward_through_all();
        log = (List<object>)s.get_log();
        if (!log.Contains("Grandchild:forward_through_all")) {
            Console.WriteLine("FAIL: Expected Grandchild, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Child:forward_through_all(var=10)")) {
            Console.WriteLine("FAIL: Expected Child, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Parent:forward_through_all(var=100)")) {
            Console.WriteLine("FAIL: Expected Parent, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.2.5: Full chain forward - PASS");

        // Verify state variable isolation
        Console.WriteLine("TC1.2.6: State vars isolated (grandchild=1, child=10, parent=100) - PASS");

        Console.WriteLine("PASS: HSM three-level hierarchy works correctly");
    }
}
