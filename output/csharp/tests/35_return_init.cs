using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class ReturnInitTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public ReturnInitTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public ReturnInitTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ReturnInitTestFrameContext {
    public ReturnInitTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public ReturnInitTestFrameContext(ReturnInitTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class ReturnInitTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public ReturnInitTestFrameEvent forward_event;
    public ReturnInitTestCompartment parent_compartment;

    public ReturnInitTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public ReturnInitTestCompartment Copy() {
        ReturnInitTestCompartment c = new ReturnInitTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ReturnInitTest {
    private List<ReturnInitTestCompartment> _state_stack;
    private ReturnInitTestCompartment __compartment;
    private ReturnInitTestCompartment __next_compartment;
    private List<ReturnInitTestFrameContext> _context_stack;

    public ReturnInitTest() {
        _state_stack = new List<ReturnInitTestCompartment>();
        _context_stack = new List<ReturnInitTestFrameContext>();
        __compartment = new ReturnInitTestCompartment("Start");
        __next_compartment = null;
        ReturnInitTestFrameEvent __frame_event = new ReturnInitTestFrameEvent("$>");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(ReturnInitTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ReturnInitTestFrameEvent exit_event = new ReturnInitTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ReturnInitTestFrameEvent enter_event = new ReturnInitTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    ReturnInitTestFrameEvent enter_event = new ReturnInitTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ReturnInitTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    private void __transition(ReturnInitTestCompartment next) {
        __next_compartment = next;
    }

    public string get_status() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("get_status");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, "unknown");
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_count() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("get_count");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, 0);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool get_flag() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("get_flag");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, false);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void trigger() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("trigger");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Start(ReturnInitTestFrameEvent __e) {
        if (__e._message == "$>") {
            // Start state enter (no-op)
        } else if (__e._message == "get_count") {
            // Don't set return - should use default 0
        } else if (__e._message == "get_flag") {
            // Don't set return - should use default false
        } else if (__e._message == "get_status") {
            // Don't set return - should use default "unknown"
        } else if (__e._message == "trigger") {
            { var __new_compartment = new ReturnInitTestCompartment("Active");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Active(ReturnInitTestFrameEvent __e) {
        if (__e._message == "$>") {
            // Active state enter (no-op)
        } else if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = 42;
        } else if (__e._message == "get_flag") {
            _context_stack[_context_stack.Count - 1]._return = true;
        } else if (__e._message == "get_status") {
            _context_stack[_context_stack.Count - 1]._return = "active";
        } else if (__e._message == "trigger") {
            { var __new_compartment = new ReturnInitTestCompartment("Start");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..6");

        var s = new ReturnInitTest();

        // Test 1: Default string return
        if ((string)s.get_status() == "unknown") {
            Console.WriteLine("ok 1 - default string return is 'unknown'");
        } else {
            Console.WriteLine("not ok 1 - default string return is 'unknown' # got " + s.get_status());
        }

        // Test 2: Default int return
        if ((int)s.get_count() == 0) {
            Console.WriteLine("ok 2 - default int return is 0");
        } else {
            Console.WriteLine("not ok 2 - default int return is 0 # got " + s.get_count());
        }

        // Test 3: Default bool return
        if ((bool)s.get_flag() == false) {
            Console.WriteLine("ok 3 - default bool return is false");
        } else {
            Console.WriteLine("not ok 3 - default bool return is false # got " + s.get_flag());
        }

        // Transition to Active state
        s.trigger();

        // Test 4: Explicit string return overrides default
        if ((string)s.get_status() == "active") {
            Console.WriteLine("ok 4 - explicit return overrides default string");
        } else {
            Console.WriteLine("not ok 4 - explicit return overrides default string # got " + s.get_status());
        }

        // Test 5: Explicit int return overrides default
        if ((int)s.get_count() == 42) {
            Console.WriteLine("ok 5 - explicit return overrides default int");
        } else {
            Console.WriteLine("not ok 5 - explicit return overrides default int # got " + s.get_count());
        }

        // Test 6: Explicit bool return overrides default
        if ((bool)s.get_flag() == true) {
            Console.WriteLine("ok 6 - explicit return overrides default bool");
        } else {
            Console.WriteLine("not ok 6 - explicit return overrides default bool # got " + s.get_flag());
        }

        Console.WriteLine("# PASS - return_init provides default return values");
    }
}
