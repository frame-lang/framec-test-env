using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// capability: @@:return header defaults and handler returns (C#).

class SystemReturnHeaderDefaultsCsharpFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SystemReturnHeaderDefaultsCsharpFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SystemReturnHeaderDefaultsCsharpFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnHeaderDefaultsCsharpFrameContext {
    public SystemReturnHeaderDefaultsCsharpFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SystemReturnHeaderDefaultsCsharpFrameContext(SystemReturnHeaderDefaultsCsharpFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SystemReturnHeaderDefaultsCsharpCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SystemReturnHeaderDefaultsCsharpFrameEvent forward_event;
    public SystemReturnHeaderDefaultsCsharpCompartment parent_compartment;

    public SystemReturnHeaderDefaultsCsharpCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SystemReturnHeaderDefaultsCsharpCompartment Copy() {
        SystemReturnHeaderDefaultsCsharpCompartment c = new SystemReturnHeaderDefaultsCsharpCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnHeaderDefaultsCsharp {
    private List<SystemReturnHeaderDefaultsCsharpCompartment> _state_stack;
    private SystemReturnHeaderDefaultsCsharpCompartment __compartment;
    private SystemReturnHeaderDefaultsCsharpCompartment __next_compartment;
    private List<SystemReturnHeaderDefaultsCsharpFrameContext> _context_stack;
    public int x = 3;

    public SystemReturnHeaderDefaultsCsharp() {
        _state_stack = new List<SystemReturnHeaderDefaultsCsharpCompartment>();
        _context_stack = new List<SystemReturnHeaderDefaultsCsharpFrameContext>();
        __compartment = new SystemReturnHeaderDefaultsCsharpCompartment("Idle");
        __next_compartment = null;
        SystemReturnHeaderDefaultsCsharpFrameEvent __frame_event = new SystemReturnHeaderDefaultsCsharpFrameEvent("$>");
        SystemReturnHeaderDefaultsCsharpFrameContext __ctx = new SystemReturnHeaderDefaultsCsharpFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(SystemReturnHeaderDefaultsCsharpFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnHeaderDefaultsCsharpFrameEvent exit_event = new SystemReturnHeaderDefaultsCsharpFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnHeaderDefaultsCsharpFrameEvent enter_event = new SystemReturnHeaderDefaultsCsharpFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    SystemReturnHeaderDefaultsCsharpFrameEvent enter_event = new SystemReturnHeaderDefaultsCsharpFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnHeaderDefaultsCsharpFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        }
    }

    private void __transition(SystemReturnHeaderDefaultsCsharpCompartment next) {
        __next_compartment = next;
    }

    public int a1() {
        SystemReturnHeaderDefaultsCsharpFrameEvent __e = new SystemReturnHeaderDefaultsCsharpFrameEvent("a1");
        SystemReturnHeaderDefaultsCsharpFrameContext __ctx = new SystemReturnHeaderDefaultsCsharpFrameContext(__e, 10);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int a2(int a) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        SystemReturnHeaderDefaultsCsharpFrameEvent __e = new SystemReturnHeaderDefaultsCsharpFrameEvent("a2", __params);
        SystemReturnHeaderDefaultsCsharpFrameContext __ctx = new SystemReturnHeaderDefaultsCsharpFrameContext(__e, a);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int a3(int a) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        SystemReturnHeaderDefaultsCsharpFrameEvent __e = new SystemReturnHeaderDefaultsCsharpFrameEvent("a3", __params);
        SystemReturnHeaderDefaultsCsharpFrameContext __ctx = new SystemReturnHeaderDefaultsCsharpFrameContext(__e, x + a);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Idle(SystemReturnHeaderDefaultsCsharpFrameEvent __e) {
        if (__e._message == "a1") {
            if (x < 5) {
                return;
            } else {
                _context_stack[_context_stack.Count - 1]._return = 0;
                return;
            }
        } else if (__e._message == "a2") {
            var a = (int) __e._parameters["a"];
            return;
        } else if (__e._message == "a3") {
            var a = (int) __e._parameters["a"];
            _context_stack[_context_stack.Count - 1]._return = a;
            return;
        }
    }

    private void bump_x(int delta) {
                    x = x + delta;
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..1");
        try {
            var s = new SystemReturnHeaderDefaultsCsharp();
            if ((int)s.a1() != 10) { Console.WriteLine("not ok 1 # a1 failed"); return; }
            if ((int)s.a2(42) != 42) { Console.WriteLine("not ok 1 # a2 failed"); return; }
            if ((int)s.a3(7) != 7) { Console.WriteLine("not ok 1 # a3 failed"); return; }
            Console.WriteLine("ok 1 - system_return_header_defaults");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - system_return_header_defaults # " + ex);
        }
    }
}
