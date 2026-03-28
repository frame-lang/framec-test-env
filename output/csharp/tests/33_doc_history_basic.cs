using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class HistoryBasicFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HistoryBasicFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HistoryBasicFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HistoryBasicFrameContext {
    public HistoryBasicFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HistoryBasicFrameContext(HistoryBasicFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HistoryBasicCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HistoryBasicFrameEvent forward_event;
    public HistoryBasicCompartment parent_compartment;

    public HistoryBasicCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HistoryBasicCompartment Copy() {
        HistoryBasicCompartment c = new HistoryBasicCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HistoryBasic {
    private List<HistoryBasicCompartment> _state_stack;
    private HistoryBasicCompartment __compartment;
    private HistoryBasicCompartment __next_compartment;
    private List<HistoryBasicFrameContext> _context_stack;

    public HistoryBasic() {
        _state_stack = new List<HistoryBasicCompartment>();
        _context_stack = new List<HistoryBasicFrameContext>();
        __compartment = new HistoryBasicCompartment("A");
        __next_compartment = null;
        HistoryBasicFrameEvent __frame_event = new HistoryBasicFrameEvent("$>");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HistoryBasicFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HistoryBasicFrameEvent exit_event = new HistoryBasicFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HistoryBasicFrameEvent enter_event = new HistoryBasicFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HistoryBasicFrameEvent enter_event = new HistoryBasicFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HistoryBasicFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        } else if (state_name == "C") {
            _state_C(__e);
        }
    }

    private void __transition(HistoryBasicCompartment next) {
        __next_compartment = next;
    }

    public void gotoC_from_A() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("gotoC_from_A");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void gotoC_from_B() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("gotoC_from_B");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void gotoB() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("gotoB");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void return_back() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("return_back");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("get_state");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_B(HistoryBasicFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "B";
            return;
        } else if (__e._message == "gotoC_from_B") {
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new HistoryBasicCompartment("C");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_A(HistoryBasicFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "A";
            return;
        } else if (__e._message == "gotoB") {
            { var __new_compartment = new HistoryBasicCompartment("B");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "gotoC_from_A") {
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new HistoryBasicCompartment("C");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_C(HistoryBasicFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "C";
            return;
        } else if (__e._message == "return_back") {
            var __popped = _state_stack[_state_stack.Count - 1]; _state_stack.RemoveAt(_state_stack.Count - 1);
            __transition(__popped);
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 33: Doc History Basic ===");
        var h = new HistoryBasic();

        // Start in A
        if ((string)h.get_state() != "A") {
            Console.WriteLine("FAIL: Expected 'A', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go to C from A (push A)
        h.gotoC_from_A();
        if ((string)h.get_state() != "C") {
            Console.WriteLine("FAIL: Expected 'C', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Return back (pop to A)
        h.return_back();
        if ((string)h.get_state() != "A") {
            Console.WriteLine("FAIL: Expected 'A' after pop, got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Now go to B
        h.gotoB();
        if ((string)h.get_state() != "B") {
            Console.WriteLine("FAIL: Expected 'B', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Go to C from B (push B)
        h.gotoC_from_B();
        if ((string)h.get_state() != "C") {
            Console.WriteLine("FAIL: Expected 'C', got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        // Return back (pop to B)
        h.return_back();
        if ((string)h.get_state() != "B") {
            Console.WriteLine("FAIL: Expected 'B' after pop, got '" + h.get_state() + "'");
            Environment.Exit(1);
        }

        Console.WriteLine("PASS: History push/pop works correctly");
    }
}
