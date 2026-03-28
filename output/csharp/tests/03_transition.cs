using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class WithTransitionFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public WithTransitionFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public WithTransitionFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class WithTransitionFrameContext {
    public WithTransitionFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public WithTransitionFrameContext(WithTransitionFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class WithTransitionCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public WithTransitionFrameEvent forward_event;
    public WithTransitionCompartment parent_compartment;

    public WithTransitionCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public WithTransitionCompartment Copy() {
        WithTransitionCompartment c = new WithTransitionCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class WithTransition {
    private List<WithTransitionCompartment> _state_stack;
    private WithTransitionCompartment __compartment;
    private WithTransitionCompartment __next_compartment;
    private List<WithTransitionFrameContext> _context_stack;

    public WithTransition() {
        _state_stack = new List<WithTransitionCompartment>();
        _context_stack = new List<WithTransitionFrameContext>();
        __compartment = new WithTransitionCompartment("First");
        __next_compartment = null;
        WithTransitionFrameEvent __frame_event = new WithTransitionFrameEvent("$>");
        WithTransitionFrameContext __ctx = new WithTransitionFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(WithTransitionFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            WithTransitionFrameEvent exit_event = new WithTransitionFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                WithTransitionFrameEvent enter_event = new WithTransitionFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    WithTransitionFrameEvent enter_event = new WithTransitionFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(WithTransitionFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "First") {
            _state_First(__e);
        } else if (state_name == "Second") {
            _state_Second(__e);
        }
    }

    private void __transition(WithTransitionCompartment next) {
        __next_compartment = next;
    }

    public void next() {
        WithTransitionFrameEvent __e = new WithTransitionFrameEvent("next");
        WithTransitionFrameContext __ctx = new WithTransitionFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        WithTransitionFrameEvent __e = new WithTransitionFrameEvent("get_state");
        WithTransitionFrameContext __ctx = new WithTransitionFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Second(WithTransitionFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Second";
            return;
        } else if (__e._message == "next") {
            { var __new_compartment = new WithTransitionCompartment("First");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_First(WithTransitionFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "First";
            return;
        } else if (__e._message == "next") {
            { var __new_compartment = new WithTransitionCompartment("Second");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 03: State Transitions ===");
        var s = new WithTransition();

        var state = s.get_state();
        if (state != "First") {
            Console.WriteLine($"FAIL: Expected 'First', got '{state}'");
            Environment.Exit(1);
        }
        Console.WriteLine($"Initial state: {state}");

        s.next();
        state = s.get_state();
        if (state != "Second") {
            Console.WriteLine($"FAIL: Expected 'Second', got '{state}'");
            Environment.Exit(1);
        }
        Console.WriteLine($"After first next(): {state}");

        s.next();
        state = s.get_state();
        if (state != "First") {
            Console.WriteLine($"FAIL: Expected 'First', got '{state}'");
            Environment.Exit(1);
        }
        Console.WriteLine($"After second next(): {state}");

        Console.WriteLine("PASS: State transitions work correctly");
    }
}
