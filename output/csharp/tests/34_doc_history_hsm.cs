using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HistoryHSMFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HistoryHSMFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HistoryHSMFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HistoryHSMFrameContext {
    public HistoryHSMFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HistoryHSMFrameContext(HistoryHSMFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HistoryHSMCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HistoryHSMFrameEvent forward_event;
    public HistoryHSMCompartment parent_compartment;

    public HistoryHSMCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HistoryHSMCompartment Copy() {
        HistoryHSMCompartment c = new HistoryHSMCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HistoryHSM {
    private List<HistoryHSMCompartment> _state_stack;
    private HistoryHSMCompartment __compartment;
    private HistoryHSMCompartment __next_compartment;
    private List<HistoryHSMFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public HistoryHSM() {
        _state_stack = new List<HistoryHSMCompartment>();
        _context_stack = new List<HistoryHSMFrameContext>();
        __compartment = new HistoryHSMCompartment("Waiting");
        __next_compartment = null;
        HistoryHSMFrameEvent __frame_event = new HistoryHSMFrameEvent("$>");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HistoryHSMFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HistoryHSMFrameEvent exit_event = new HistoryHSMFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HistoryHSMFrameEvent enter_event = new HistoryHSMFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HistoryHSMFrameEvent enter_event = new HistoryHSMFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HistoryHSMFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Waiting") {
            _state_Waiting(__e);
        } else if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        } else if (state_name == "AB") {
            _state_AB(__e);
        } else if (state_name == "C") {
            _state_C(__e);
        }
    }

    private void __transition(HistoryHSMCompartment next) {
        __next_compartment = next;
    }

    public void gotoA() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("gotoA");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void gotoB() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("gotoB");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void gotoC() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("gotoC");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void goBack() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("goBack");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("get_state");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public List<object> get_log() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("get_log");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_A(HistoryHSMFrameEvent __e) {
        if (__e._message == "$>") {
            this.log_msg("In $A");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "A";
            return;
        } else if (__e._message == "gotoB") {
            this.log_msg("gotoB");
            { var __new_compartment = new HistoryHSMCompartment("B");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else {
            _state_AB(__e);
        }
    }

    private void _state_B(HistoryHSMFrameEvent __e) {
        if (__e._message == "$>") {
            this.log_msg("In $B");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "B";
            return;
        } else if (__e._message == "gotoA") {
            this.log_msg("gotoA");
            { var __new_compartment = new HistoryHSMCompartment("A");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else {
            _state_AB(__e);
        }
    }

    private void _state_AB(HistoryHSMFrameEvent __e) {
        if (__e._message == "gotoC") {
            this.log_msg("gotoC in $AB");
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new HistoryHSMCompartment("C");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_C(HistoryHSMFrameEvent __e) {
        if (__e._message == "$>") {
            this.log_msg("In $C");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "C";
            return;
        } else if (__e._message == "goBack") {
            this.log_msg("goBack");
            var __popped = _state_stack[_state_stack.Count - 1]; _state_stack.RemoveAt(_state_stack.Count - 1);
            __transition(__popped);
            return;
        }
    }

    private void _state_Waiting(HistoryHSMFrameEvent __e) {
        if (__e._message == "$>") {
            this.log_msg("In $Waiting");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Waiting";
            return;
        } else if (__e._message == "gotoA") {
            this.log_msg("gotoA");
            { var __new_compartment = new HistoryHSMCompartment("A");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "gotoB") {
            this.log_msg("gotoB");
            { var __new_compartment = new HistoryHSMCompartment("B");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void log_msg(string msg) {
                    this.log.Add(msg);
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 34: Doc History HSM ===");
        var h = new HistoryHSM();

        // Start in Waiting
        if ((string)h.get_state() != "Waiting") {
            Console.WriteLine("FAIL: Expected 'Waiting', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go to A
        h.gotoA();
        if ((string)h.get_state() != "A") {
            Console.WriteLine("FAIL: Expected 'A', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go to C (using inherited gotoC from $AB)
        h.gotoC();
        if ((string)h.get_state() != "C") {
            Console.WriteLine("FAIL: Expected 'C', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go back (should pop to A)
        h.goBack();
        if ((string)h.get_state() != "A") {
            Console.WriteLine("FAIL: Expected 'A' after goBack, got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go to B
        h.gotoB();
        if ((string)h.get_state() != "B") {
            Console.WriteLine("FAIL: Expected 'B', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go to C (again using inherited gotoC)
        h.gotoC();
        if ((string)h.get_state() != "C") {
            Console.WriteLine("FAIL: Expected 'C', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go back (should pop to B)
        h.goBack();
        if ((string)h.get_state() != "B") {
            Console.WriteLine("FAIL: Expected 'B' after goBack, got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        Console.WriteLine("Log: [" + string.Join(", ", h.get_log()) + "]");
        Console.WriteLine("PASS: HSM with history works correctly");
    }
}
