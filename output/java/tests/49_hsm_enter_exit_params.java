import java.util.*;


import java.util.*;

class HSMEnterExitParamsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMEnterExitParamsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMEnterExitParamsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterExitParamsFrameContext {
    HSMEnterExitParamsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMEnterExitParamsFrameContext(HSMEnterExitParamsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMEnterExitParamsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMEnterExitParamsFrameEvent forward_event;
    HSMEnterExitParamsCompartment parent_compartment;

    HSMEnterExitParamsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMEnterExitParamsCompartment copy() {
        HSMEnterExitParamsCompartment c = new HSMEnterExitParamsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterExitParams {
    private ArrayList<HSMEnterExitParamsCompartment> _state_stack;
    private HSMEnterExitParamsCompartment __compartment;
    private HSMEnterExitParamsCompartment __next_compartment;
    private ArrayList<HSMEnterExitParamsFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMEnterExitParams() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new HSMEnterExitParamsCompartment("Start");
        __next_compartment = null;
        HSMEnterExitParamsFrameEvent __frame_event = new HSMEnterExitParamsFrameEvent("$>");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMEnterExitParamsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterExitParamsFrameEvent exit_event = new HSMEnterExitParamsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterExitParamsFrameEvent enter_event = new HSMEnterExitParamsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMEnterExitParamsFrameEvent enter_event = new HSMEnterExitParamsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterExitParamsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("ChildA")) {
            _state_ChildA(__e);
        } else if (state_name.equals("ChildB")) {
            _state_ChildB(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterExitParamsCompartment next) {
        __next_compartment = next;
    }

    public void go_to_a() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("go_to_a");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_to_sibling() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("go_to_sibling");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_back() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("go_back");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("get_log");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMEnterExitParamsFrameEvent __e = new HSMEnterExitParamsFrameEvent("get_state");
        HSMEnterExitParamsFrameContext __ctx = new HSMEnterExitParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Start(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Start";
            return;
        } else if (__e._message.equals("go_to_a")) {
            var __compartment = new HSMEnterExitParamsCompartment("ChildA");
            __compartment.parent_compartment = this.__compartment.copy();
            __compartment.enter_args.put("0", "starting");
            __transition(__compartment);
            return;
        }
    }

    private void _state_ChildA(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message.equals("<$")) {
            var reason = (String) __compartment.exit_args.get("0");
            this.log.add("ChildA:exit(" + reason + ")");
        } else if (__e._message.equals("$>")) {
            var msg = (String) __compartment.enter_args.get("0");
            this.log.add("ChildA:enter(" + msg + ")");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "ChildA";
            return;
        } else if (__e._message.equals("go_to_sibling")) {
            __compartment.exit_args.put("0", "leaving_A");
            var __compartment = new HSMEnterExitParamsCompartment("ChildB");
            __compartment.parent_compartment = this.__compartment.copy();
            __compartment.enter_args.put("0", "arriving_B");
            __transition(__compartment);
            return;
        }
    }

    private void _state_ChildB(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message.equals("<$")) {
            var reason = (String) __compartment.exit_args.get("0");
            this.log.add("ChildB:exit(" + reason + ")");
        } else if (__e._message.equals("$>")) {
            var msg = (String) __compartment.enter_args.get("0");
            this.log.add("ChildB:enter(" + msg + ")");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "ChildB";
            return;
        } else if (__e._message.equals("go_back")) {
            __compartment.exit_args.put("0", "leaving_B");
            var __compartment = new HSMEnterExitParamsCompartment("ChildA");
            __compartment.parent_compartment = this.__compartment.copy();
            __compartment.enter_args.put("0", "returning_A");
            __transition(__compartment);
            return;
        }
    }

    private void _state_Parent(HSMEnterExitParamsFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 49: HSM Enter/Exit with Params ===");
        var s = new HSMEnterExitParams();

        // First go to ChildA with enter params
        s.go_to_a();
        ArrayList log = s.get_log();
        if (!log.contains("ChildA:enter(starting)")) {
            System.out.println("FAIL: Expected ChildA:enter(starting), got " + log);
            System.exit(1);
        }
        System.out.println("TC2.5.0: Initial transition with enter params - PASS");

        // TC2.5.1: Exit params passed correctly
        s.go_to_sibling();
        log = s.get_log();
        if (!log.contains("ChildA:exit(leaving_A)")) {
            System.out.println("FAIL: Expected exit with param, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.5.1: Exit params passed correctly - PASS");

        // TC2.5.2: Enter params passed to target state
        if (!log.contains("ChildB:enter(arriving_B)")) {
            System.out.println("FAIL: Expected enter with param, got " + log);
            System.exit(1);
        }
        if (!s.get_state().equals("ChildB")) {
            System.out.println("FAIL: Expected ChildB, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC2.5.2: Enter params passed to target - PASS");

        // TC2.5.3: Return transition with different params
        s.go_back();
        log = s.get_log();
        if (!log.contains("ChildB:exit(leaving_B)")) {
            System.out.println("FAIL: Expected ChildB exit, got " + log);
            System.exit(1);
        }
        if (!log.contains("ChildA:enter(returning_A)")) {
            System.out.println("FAIL: Expected ChildA enter, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.5.3: Return transition with params - PASS");

        System.out.println("PASS: HSM enter/exit with params works correctly");
    }
}
