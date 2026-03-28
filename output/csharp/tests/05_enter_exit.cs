using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class EnterExitFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public EnterExitFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public EnterExitFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class EnterExitFrameContext {
    public EnterExitFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public EnterExitFrameContext(EnterExitFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class EnterExitCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public EnterExitFrameEvent forward_event;
    public EnterExitCompartment parent_compartment;

    public EnterExitCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public EnterExitCompartment Copy() {
        EnterExitCompartment c = new EnterExitCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class EnterExit {
    private List<EnterExitCompartment> _state_stack;
    private EnterExitCompartment __compartment;
    private EnterExitCompartment __next_compartment;
    private List<EnterExitFrameContext> _context_stack;
    public List<string> log = new List<string>();

    public EnterExit() {
        _state_stack = new List<EnterExitCompartment>();
        _context_stack = new List<EnterExitFrameContext>();
        __compartment = new EnterExitCompartment("Off");
        __next_compartment = null;
        EnterExitFrameEvent __frame_event = new EnterExitFrameEvent("$>");
        EnterExitFrameContext __ctx = new EnterExitFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(EnterExitFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            EnterExitFrameEvent exit_event = new EnterExitFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                EnterExitFrameEvent enter_event = new EnterExitFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    EnterExitFrameEvent enter_event = new EnterExitFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(EnterExitFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Off") {
            _state_Off(__e);
        } else if (state_name == "On") {
            _state_On(__e);
        }
    }

    private void __transition(EnterExitCompartment next) {
        __next_compartment = next;
    }

    public void toggle() {
        EnterExitFrameEvent __e = new EnterExitFrameEvent("toggle");
        EnterExitFrameContext __ctx = new EnterExitFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<string> get_log() {
        EnterExitFrameEvent __e = new EnterExitFrameEvent("get_log");
        EnterExitFrameContext __ctx = new EnterExitFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<string>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_On(EnterExitFrameEvent __e) {
        if (__e._message == "<$") {
            this.log.Add("exit:On");
            Console.WriteLine("Exiting On state");
        } else if (__e._message == "$>") {
            this.log.Add("enter:On");
            Console.WriteLine("Entered On state");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "toggle") {
            { var __new_compartment = new EnterExitCompartment("Off");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Off(EnterExitFrameEvent __e) {
        if (__e._message == "<$") {
            this.log.Add("exit:Off");
            Console.WriteLine("Exiting Off state");
        } else if (__e._message == "$>") {
            this.log.Add("enter:Off");
            Console.WriteLine("Entered Off state");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "toggle") {
            { var __new_compartment = new EnterExitCompartment("On");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 05: Enter/Exit Handlers ===");
        var s = new EnterExit();

        // Initial enter should have been called
        var log = (List<string>)s.get_log();
        if (!log.Contains("enter:Off")) {
            throw new Exception("Expected 'enter:Off' in log, got " + string.Join(", ", log));
        }
        Console.WriteLine("After construction: [" + string.Join(", ", log) + "]");

        // Toggle to On - should exit Off, enter On
        s.toggle();
        log = (List<string>)s.get_log();
        if (!log.Contains("exit:Off")) {
            throw new Exception("Expected 'exit:Off' in log, got " + string.Join(", ", log));
        }
        if (!log.Contains("enter:On")) {
            throw new Exception("Expected 'enter:On' in log, got " + string.Join(", ", log));
        }
        Console.WriteLine("After toggle to On: [" + string.Join(", ", log) + "]");

        // Toggle back to Off - should exit On, enter Off
        s.toggle();
        log = (List<string>)s.get_log();
        int enterOffCount = 0;
        foreach (var entry in log) {
            if (entry == "enter:Off") enterOffCount++;
        }
        if (enterOffCount != 2) {
            throw new Exception("Expected 2 'enter:Off' entries, got " + string.Join(", ", log));
        }
        if (!log.Contains("exit:On")) {
            throw new Exception("Expected 'exit:On' in log, got " + string.Join(", ", log));
        }
        Console.WriteLine("After toggle to Off: [" + string.Join(", ", log) + "]");

        Console.WriteLine("PASS: Enter/Exit handlers work correctly");
    }
}
