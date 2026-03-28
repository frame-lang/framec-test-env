using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HSMSingleParentFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMSingleParentFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMSingleParentFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMSingleParentFrameContext {
    public HSMSingleParentFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMSingleParentFrameContext(HSMSingleParentFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMSingleParentCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMSingleParentFrameEvent forward_event;
    public HSMSingleParentCompartment parent_compartment;

    public HSMSingleParentCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMSingleParentCompartment Copy() {
        HSMSingleParentCompartment c = new HSMSingleParentCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMSingleParent {
    private List<HSMSingleParentCompartment> _state_stack;
    private HSMSingleParentCompartment __compartment;
    private HSMSingleParentCompartment __next_compartment;
    private List<HSMSingleParentFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HSMSingleParent() {
        _state_stack = new List<HSMSingleParentCompartment>();
        _context_stack = new List<HSMSingleParentFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMSingleParentCompartment("Parent");
        this.__compartment = new HSMSingleParentCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMSingleParentFrameEvent __frame_event = new HSMSingleParentFrameEvent("$>");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMSingleParentFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMSingleParentFrameEvent exit_event = new HSMSingleParentFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMSingleParentFrameEvent enter_event = new HSMSingleParentFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMSingleParentFrameEvent enter_event = new HSMSingleParentFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMSingleParentFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMSingleParentCompartment next) {
        __next_compartment = next;
    }

    public void child_only() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("child_only");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void forward_to_parent() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("forward_to_parent");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("get_log");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("get_state");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Child(HSMSingleParentFrameEvent __e) {
        if (__e._message == "child_only") {
            this.log.Add("Child:child_only");
        } else if (__e._message == "forward_to_parent") {
            this.log.Add("Child:before_forward");
            _state_Parent(__e);
            this.log.Add("Child:after_forward");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Child";
            return;
        }
    }

    private void _state_Parent(HSMSingleParentFrameEvent __e) {
        if (__e._message == "forward_to_parent") {
            this.log.Add("Parent:forward_to_parent");
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
        Console.WriteLine("=== Test 41: HSM Single Parent ===");
        var s = new HSMSingleParent();

        // TC1.1.1: Child declares parent with `=> $Parent` syntax (verified by compilation)
        Console.WriteLine("TC1.1.1: Child-Parent relationship compiles - PASS");

        // TC1.1.2: Child can forward events to parent
        s.forward_to_parent();
        var log = (List<object>)s.get_log();
        if (!log.Contains("Child:before_forward")) {
            Console.WriteLine("FAIL: Expected Child:before_forward in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("Parent:forward_to_parent")) {
            Console.WriteLine("FAIL: Expected Parent:forward_to_parent in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.1.2: Child forwards to parent - PASS (log: [" + string.Join(", ", log) + "])");

        // TC1.1.3: Child remains the current state (no transition occurs on forward)
        var state = (string)s.get_state();
        if (state != "Child") {
            Console.WriteLine("FAIL: Expected state 'Child', got '" + state + "'");
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.1.3: Child remains current state after forward - PASS");

        // TC1.1.4: Parent handler executes and returns control
        if (!log.Contains("Child:after_forward")) {
            Console.WriteLine("FAIL: Expected Child:after_forward in log (after parent), got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        int idx_parent = log.IndexOf("Parent:forward_to_parent");
        int idx_after = log.IndexOf("Child:after_forward");
        if (idx_after <= idx_parent) {
            Console.WriteLine("FAIL: Expected Child:after_forward after Parent handler");
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.1.4: Parent executes and returns control - PASS");

        // TC1.1.5: Child-only event not forwarded
        s.child_only();
        log = (List<object>)s.get_log();
        int count = 0;
        foreach (var item in log) {
            if (item.Equals("Child:child_only")) count++;
        }
        if (count != 1) {
            Console.WriteLine("FAIL: Expected exactly 1 Child:child_only, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("TC1.1.5: Child-only event handled locally - PASS");

        Console.WriteLine("PASS: HSM single parent relationship works correctly");
    }
}
