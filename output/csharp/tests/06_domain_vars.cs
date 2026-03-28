using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class DomainVarsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public DomainVarsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public DomainVarsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class DomainVarsFrameContext {
    public DomainVarsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public DomainVarsFrameContext(DomainVarsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class DomainVarsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public DomainVarsFrameEvent forward_event;
    public DomainVarsCompartment parent_compartment;

    public DomainVarsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public DomainVarsCompartment Copy() {
        DomainVarsCompartment c = new DomainVarsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class DomainVars {
    private List<DomainVarsCompartment> _state_stack;
    private DomainVarsCompartment __compartment;
    private DomainVarsCompartment __next_compartment;
    private List<DomainVarsFrameContext> _context_stack;
    public int count = 0;
    public string name = "counter";

    public DomainVars() {
        _state_stack = new List<DomainVarsCompartment>();
        _context_stack = new List<DomainVarsFrameContext>();
        __compartment = new DomainVarsCompartment("Counting");
        __next_compartment = null;
        DomainVarsFrameEvent __frame_event = new DomainVarsFrameEvent("$>");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(DomainVarsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            DomainVarsFrameEvent exit_event = new DomainVarsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                DomainVarsFrameEvent enter_event = new DomainVarsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    DomainVarsFrameEvent enter_event = new DomainVarsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(DomainVarsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Counting") {
            _state_Counting(__e);
        }
    }

    private void __transition(DomainVarsCompartment next) {
        __next_compartment = next;
    }

    public void increment() {
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("increment");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void decrement() {
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("decrement");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int get_count() {
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("get_count");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void set_count(int value) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["value"] = value;
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("set_count", __params);
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Counting(DomainVarsFrameEvent __e) {
        if (__e._message == "decrement") {
            this.count -= 1;
            Console.WriteLine(this.name + ": decremented to " + this.count);
        } else if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = this.count;
            return;
        } else if (__e._message == "increment") {
            this.count += 1;
            Console.WriteLine(this.name + ": incremented to " + this.count);
        } else if (__e._message == "set_count") {
            var value = (int) __e._parameters["value"];
            this.count = value;
            Console.WriteLine(this.name + ": set to " + this.count);
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 06: Domain Variables ===");
        var s = new DomainVars();

        // Initial value should be 0
        var count = (int)s.get_count();
        if (count != 0) {
            throw new Exception("Expected initial count=0, got " + count);
        }
        Console.WriteLine("Initial count: " + count);

        // Increment
        s.increment();
        count = (int)s.get_count();
        if (count != 1) {
            throw new Exception("Expected count=1, got " + count);
        }

        s.increment();
        count = (int)s.get_count();
        if (count != 2) {
            throw new Exception("Expected count=2, got " + count);
        }

        // Decrement
        s.decrement();
        count = (int)s.get_count();
        if (count != 1) {
            throw new Exception("Expected count=1, got " + count);
        }

        // Set directly
        s.set_count(100);
        count = (int)s.get_count();
        if (count != 100) {
            throw new Exception("Expected count=100, got " + count);
        }

        Console.WriteLine("Final count: " + count);
        Console.WriteLine("PASS: Domain variables work correctly");
    }
}
