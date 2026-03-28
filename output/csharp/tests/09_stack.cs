using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class StackOpsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public StackOpsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public StackOpsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StackOpsFrameContext {
    public StackOpsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public StackOpsFrameContext(StackOpsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class StackOpsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public StackOpsFrameEvent forward_event;
    public StackOpsCompartment parent_compartment;

    public StackOpsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public StackOpsCompartment Copy() {
        StackOpsCompartment c = new StackOpsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StackOps {
    private List<StackOpsCompartment> _state_stack;
    private StackOpsCompartment __compartment;
    private StackOpsCompartment __next_compartment;
    private List<StackOpsFrameContext> _context_stack;

    public StackOps() {
        _state_stack = new List<StackOpsCompartment>();
        _context_stack = new List<StackOpsFrameContext>();
        __compartment = new StackOpsCompartment("Main");
        __next_compartment = null;
        StackOpsFrameEvent __frame_event = new StackOpsFrameEvent("$>");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(StackOpsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StackOpsFrameEvent exit_event = new StackOpsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StackOpsFrameEvent enter_event = new StackOpsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    StackOpsFrameEvent enter_event = new StackOpsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StackOpsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Main") {
            _state_Main(__e);
        } else if (state_name == "Sub") {
            _state_Sub(__e);
        }
    }

    private void __transition(StackOpsCompartment next) {
        __next_compartment = next;
    }

    public void push_and_go() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("push_and_go");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void pop_back() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("pop_back");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string do_work() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("do_work");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("get_state");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Main(StackOpsFrameEvent __e) {
        if (__e._message == "do_work") {
            _context_stack[_context_stack.Count - 1]._return = "Working in Main";
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Main";
            return;
        } else if (__e._message == "pop_back") {
            Console.WriteLine("Cannot pop - nothing on stack in Main");
        } else if (__e._message == "push_and_go") {
            Console.WriteLine("Pushing Main to stack, going to Sub");
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new StackOpsCompartment("Sub");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Sub(StackOpsFrameEvent __e) {
        if (__e._message == "do_work") {
            _context_stack[_context_stack.Count - 1]._return = "Working in Sub";
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Sub";
            return;
        } else if (__e._message == "pop_back") {
            Console.WriteLine("Popping back to previous state");
            var __popped = _state_stack[_state_stack.Count - 1]; _state_stack.RemoveAt(_state_stack.Count - 1);
            __transition(__popped);
            return;
        } else if (__e._message == "push_and_go") {
            Console.WriteLine("Already in Sub");
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 09: Stack Push/Pop ===");
        var s = new StackOps();

        // Initial state should be Main
        var state = (string)s.get_state();
        if (state != "Main") {
            throw new Exception("Expected 'Main', got '" + state + "'");
        }
        Console.WriteLine("Initial state: " + state);

        // Do work in Main
        var work = (string)s.do_work();
        if (work != "Working in Main") {
            throw new Exception("Expected 'Working in Main', got '" + work + "'");
        }
        Console.WriteLine("do_work(): " + work);

        // Push and go to Sub
        s.push_and_go();
        state = (string)s.get_state();
        if (state != "Sub") {
            throw new Exception("Expected 'Sub', got '" + state + "'");
        }
        Console.WriteLine("After push_and_go(): " + state);

        // Do work in Sub
        work = (string)s.do_work();
        if (work != "Working in Sub") {
            throw new Exception("Expected 'Working in Sub', got '" + work + "'");
        }
        Console.WriteLine("do_work(): " + work);

        // Pop back to Main
        s.pop_back();
        state = (string)s.get_state();
        if (state != "Main") {
            throw new Exception("Expected 'Main' after pop, got '" + state + "'");
        }
        Console.WriteLine("After pop_back(): " + state);

        Console.WriteLine("PASS: Stack push/pop works correctly");
    }
}
