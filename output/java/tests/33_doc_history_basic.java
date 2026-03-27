import java.util.*;


import java.util.*;

class HistoryBasicFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HistoryBasicFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HistoryBasicFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HistoryBasicFrameContext {
    HistoryBasicFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HistoryBasicFrameContext(HistoryBasicFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HistoryBasicCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HistoryBasicFrameEvent forward_event;
    HistoryBasicCompartment parent_compartment;

    HistoryBasicCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HistoryBasicCompartment copy() {
        HistoryBasicCompartment c = new HistoryBasicCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HistoryBasic {
    private ArrayList<HistoryBasicCompartment> _state_stack;
    private HistoryBasicCompartment __compartment;
    private HistoryBasicCompartment __next_compartment;
    private ArrayList<HistoryBasicFrameContext> _context_stack;

    public HistoryBasic() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new HistoryBasicCompartment("A");
        __next_compartment = null;
        HistoryBasicFrameEvent __frame_event = new HistoryBasicFrameEvent("$>");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("A")) {
            _state_A(__e);
        } else if (state_name.equals("B")) {
            _state_B(__e);
        } else if (state_name.equals("C")) {
            _state_C(__e);
        }
    }

    private void __transition(HistoryBasicCompartment next) {
        __next_compartment = next;
    }

    public void gotoC_from_A() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("gotoC_from_A");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void gotoC_from_B() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("gotoC_from_B");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void gotoB() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("gotoB");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void return_back() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("return_back");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        HistoryBasicFrameEvent __e = new HistoryBasicFrameEvent("get_state");
        HistoryBasicFrameContext __ctx = new HistoryBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_C(HistoryBasicFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "C";
            return;
        } else if (__e._message.equals("return_back")) {
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
        }
    }

    private void _state_B(HistoryBasicFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "B";
            return;
        } else if (__e._message.equals("gotoC_from_B")) {
            _state_stack.add(__compartment.copy());
            var __compartment = new HistoryBasicCompartment("C");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_A(HistoryBasicFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "A";
            return;
        } else if (__e._message.equals("gotoB")) {
            var __compartment = new HistoryBasicCompartment("B");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("gotoC_from_A")) {
            _state_stack.add(__compartment.copy());
            var __compartment = new HistoryBasicCompartment("C");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 33: Doc History Basic ===");
        var h = new HistoryBasic();

        // Start in A
        if (!h.get_state().equals("A")) {
            System.out.println("FAIL: Expected 'A', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go to C from A (push A)
        h.gotoC_from_A();
        if (!h.get_state().equals("C")) {
            System.out.println("FAIL: Expected 'C', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Return back (pop to A)
        h.return_back();
        if (!h.get_state().equals("A")) {
            System.out.println("FAIL: Expected 'A' after pop, got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Now go to B
        h.gotoB();
        if (!h.get_state().equals("B")) {
            System.out.println("FAIL: Expected 'B', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go to C from B (push B)
        h.gotoC_from_B();
        if (!h.get_state().equals("C")) {
            System.out.println("FAIL: Expected 'C', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Return back (pop to B)
        h.return_back();
        if (!h.get_state().equals("B")) {
            System.out.println("FAIL: Expected 'B' after pop, got '" + h.get_state() + "'");
            System.exit(1);
        }

        System.out.println("PASS: History push/pop works correctly");
    }
}
