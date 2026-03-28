using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMParentStateVarsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMParentStateVarsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMParentStateVarsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMParentStateVarsFrameContext {
    public HSMParentStateVarsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMParentStateVarsFrameContext(HSMParentStateVarsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMParentStateVarsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMParentStateVarsFrameEvent forward_event;
    public HSMParentStateVarsCompartment parent_compartment;

    public HSMParentStateVarsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMParentStateVarsCompartment Copy() {
        HSMParentStateVarsCompartment c = new HSMParentStateVarsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMParentStateVars {
    private List<HSMParentStateVarsCompartment> _state_stack;
    private HSMParentStateVarsCompartment __compartment;
    private HSMParentStateVarsCompartment __next_compartment;
    private List<HSMParentStateVarsFrameContext> _context_stack;

    public HSMParentStateVars() {
        _state_stack = new List<HSMParentStateVarsCompartment>();
        _context_stack = new List<HSMParentStateVarsFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMParentStateVarsCompartment("Parent");
        __parent_comp_0.state_vars["parent_count"] = 100;
        this.__compartment = new HSMParentStateVarsCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMParentStateVarsFrameEvent __frame_event = new HSMParentStateVarsFrameEvent("$>");
        HSMParentStateVarsFrameContext __ctx = new HSMParentStateVarsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMParentStateVarsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMParentStateVarsFrameEvent exit_event = new HSMParentStateVarsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMParentStateVarsFrameEvent enter_event = new HSMParentStateVarsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMParentStateVarsFrameEvent enter_event = new HSMParentStateVarsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMParentStateVarsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMParentStateVarsCompartment next) {
        __next_compartment = next;
    }

    public int get_child_count() {
        HSMParentStateVarsFrameEvent __e = new HSMParentStateVarsFrameEvent("get_child_count");
        HSMParentStateVarsFrameContext __ctx = new HSMParentStateVarsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_parent_count() {
        HSMParentStateVarsFrameEvent __e = new HSMParentStateVarsFrameEvent("get_parent_count");
        HSMParentStateVarsFrameContext __ctx = new HSMParentStateVarsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Child(HSMParentStateVarsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Child") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("child_count")) {
                __sv_comp.state_vars["child_count"] = 0;
            }
        } else if (__e._message == "get_child_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["child_count"];
            return;
        } else if (__e._message == "get_parent_count") {
            _state_Parent(__e);
        }
    }

    private void _state_Parent(HSMParentStateVarsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Parent") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("parent_count")) {
                __sv_comp.state_vars["parent_count"] = 100;
            }
        } else if (__e._message == "get_parent_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["parent_count"];
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 40: HSM Parent State Variables ===");
        var s = new HSMParentStateVars();

        var childCount = (int)s.get_child_count();
        if (childCount != 0) {
            Console.WriteLine("FAIL: Expected child_count=0, got " + childCount);
            Environment.Exit(1);
        }
        Console.WriteLine("Child count: " + childCount);

        var parentCount = (int)s.get_parent_count();
        if (parentCount != 100) {
            Console.WriteLine("FAIL: Expected parent_count=100, got " + parentCount);
            Environment.Exit(1);
        }
        Console.WriteLine("Parent count: " + parentCount);

        Console.WriteLine("PASS: HSM parent state variables work correctly");
    }
}
