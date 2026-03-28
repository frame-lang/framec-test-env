import java.util.*;


import java.util.*;

class HistoryHSMFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HistoryHSMFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HistoryHSMFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HistoryHSMFrameContext {
    HistoryHSMFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HistoryHSMFrameContext(HistoryHSMFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HistoryHSMCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HistoryHSMFrameEvent forward_event;
    HistoryHSMCompartment parent_compartment;

    HistoryHSMCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HistoryHSMCompartment copy() {
        HistoryHSMCompartment c = new HistoryHSMCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HistoryHSM {
    private ArrayList<HistoryHSMCompartment> _state_stack;
    private HistoryHSMCompartment __compartment;
    private HistoryHSMCompartment __next_compartment;
    private ArrayList<HistoryHSMFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HistoryHSM() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new HistoryHSMCompartment("Waiting");
        __next_compartment = null;
        HistoryHSMFrameEvent __frame_event = new HistoryHSMFrameEvent("$>");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Waiting")) {
            _state_Waiting(__e);
        } else if (state_name.equals("A")) {
            _state_A(__e);
        } else if (state_name.equals("B")) {
            _state_B(__e);
        } else if (state_name.equals("AB")) {
            _state_AB(__e);
        } else if (state_name.equals("C")) {
            _state_C(__e);
        }
    }

    private void __transition(HistoryHSMCompartment next) {
        __next_compartment = next;
    }

    public void gotoA() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("gotoA");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void gotoB() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("gotoB");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void gotoC() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("gotoC");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void goBack() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("goBack");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("get_state");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public ArrayList get_log() {
        HistoryHSMFrameEvent __e = new HistoryHSMFrameEvent("get_log");
        HistoryHSMFrameContext __ctx = new HistoryHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Waiting(HistoryHSMFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log_msg("In $Waiting");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Waiting";
            return;
        } else if (__e._message.equals("gotoA")) {
            this.log_msg("gotoA");
            var __compartment = new HistoryHSMCompartment("A");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("gotoB")) {
            this.log_msg("gotoB");
            var __compartment = new HistoryHSMCompartment("B");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_C(HistoryHSMFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log_msg("In $C");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "C";
            return;
        } else if (__e._message.equals("goBack")) {
            this.log_msg("goBack");
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
        }
    }

    private void _state_B(HistoryHSMFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log_msg("In $B");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "B";
            return;
        } else if (__e._message.equals("gotoA")) {
            this.log_msg("gotoA");
            var __compartment = new HistoryHSMCompartment("A");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else {
            _state_AB(__e);
        }
    }

    private void _state_A(HistoryHSMFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log_msg("In $A");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "A";
            return;
        } else if (__e._message.equals("gotoB")) {
            this.log_msg("gotoB");
            var __compartment = new HistoryHSMCompartment("B");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else {
            _state_AB(__e);
        }
    }

    private void _state_AB(HistoryHSMFrameEvent __e) {
        if (__e._message.equals("gotoC")) {
            this.log_msg("gotoC in $AB");
            _state_stack.add(__compartment.copy());
            var __compartment = new HistoryHSMCompartment("C");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void log_msg(String msg) {
                    this.log.add(msg);
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 34: Doc History HSM ===");
        var h = new HistoryHSM();

        // Start in Waiting
        if (!h.get_state().equals("Waiting")) {
            System.out.println("FAIL: Expected 'Waiting', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go to A
        h.gotoA();
        if (!h.get_state().equals("A")) {
            System.out.println("FAIL: Expected 'A', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go to C (using inherited gotoC from $AB)
        h.gotoC();
        if (!h.get_state().equals("C")) {
            System.out.println("FAIL: Expected 'C', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go back (should pop to A)
        h.goBack();
        if (!h.get_state().equals("A")) {
            System.out.println("FAIL: Expected 'A' after goBack, got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go to B
        h.gotoB();
        if (!h.get_state().equals("B")) {
            System.out.println("FAIL: Expected 'B', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go to C (again using inherited gotoC)
        h.gotoC();
        if (!h.get_state().equals("C")) {
            System.out.println("FAIL: Expected 'C', got '" + h.get_state() + "'");
            System.exit(1);
        }

        // Go back (should pop to B)
        h.goBack();
        if (!h.get_state().equals("B")) {
            System.out.println("FAIL: Expected 'B' after goBack, got '" + h.get_state() + "'");
            System.exit(1);
        }

        System.out.println("Log: " + h.get_log());
        System.out.println("PASS: HSM with history works correctly");
    }
}
