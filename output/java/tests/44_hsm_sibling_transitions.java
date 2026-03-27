import java.util.*;


import java.util.*;

class HSMSiblingTransitionsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMSiblingTransitionsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMSiblingTransitionsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMSiblingTransitionsFrameContext {
    HSMSiblingTransitionsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMSiblingTransitionsFrameContext(HSMSiblingTransitionsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMSiblingTransitionsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMSiblingTransitionsFrameEvent forward_event;
    HSMSiblingTransitionsCompartment parent_compartment;

    HSMSiblingTransitionsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMSiblingTransitionsCompartment copy() {
        HSMSiblingTransitionsCompartment c = new HSMSiblingTransitionsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMSiblingTransitions {
    private ArrayList<HSMSiblingTransitionsCompartment> _state_stack;
    private HSMSiblingTransitionsCompartment __compartment;
    private HSMSiblingTransitionsCompartment __next_compartment;
    private ArrayList<HSMSiblingTransitionsFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMSiblingTransitions() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMSiblingTransitionsCompartment("Parent");
        this.__compartment = new HSMSiblingTransitionsCompartment("ChildA");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMSiblingTransitionsFrameEvent __frame_event = new HSMSiblingTransitionsFrameEvent("$>");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMSiblingTransitionsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMSiblingTransitionsFrameEvent exit_event = new HSMSiblingTransitionsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMSiblingTransitionsFrameEvent enter_event = new HSMSiblingTransitionsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMSiblingTransitionsFrameEvent enter_event = new HSMSiblingTransitionsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMSiblingTransitionsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("ChildA")) {
            _state_ChildA(__e);
        } else if (state_name.equals("ChildB")) {
            _state_ChildB(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMSiblingTransitionsCompartment next) {
        __next_compartment = next;
    }

    public void go_to_b() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("go_to_b");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_to_a() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("go_to_a");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forward_action() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("forward_action");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("get_log");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMSiblingTransitionsFrameEvent __e = new HSMSiblingTransitionsFrameEvent("get_state");
        HSMSiblingTransitionsFrameContext __ctx = new HSMSiblingTransitionsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_ChildB(HSMSiblingTransitionsFrameEvent __e) {
        if (__e._message.equals("<$")) {
            this.log.add("ChildB:exit");
        } else if (__e._message.equals("$>")) {
            this.log.add("ChildB:enter");
        } else if (__e._message.equals("forward_action")) {
            this.log.add("ChildB:forward");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "ChildB";
            return;
        } else if (__e._message.equals("go_to_a")) {
            this.log.add("ChildB:go_to_a");
            var __compartment = new HSMSiblingTransitionsCompartment("ChildA");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Parent(HSMSiblingTransitionsFrameEvent __e) {
        if (__e._message.equals("forward_action")) {
            this.log.add("Parent:forward_action");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        }
    }

    private void _state_ChildA(HSMSiblingTransitionsFrameEvent __e) {
        if (__e._message.equals("<$")) {
            this.log.add("ChildA:exit");
        } else if (__e._message.equals("$>")) {
            this.log.add("ChildA:enter");
        } else if (__e._message.equals("forward_action")) {
            this.log.add("ChildA:forward");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "ChildA";
            return;
        } else if (__e._message.equals("go_to_b")) {
            this.log.add("ChildA:go_to_b");
            var __compartment = new HSMSiblingTransitionsCompartment("ChildB");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 44: HSM Sibling Transitions ===");
        var s = new HSMSiblingTransitions();

        // Initial state is ChildA with enter handler fired
        ArrayList log = s.get_log();
        if (!log.contains("ChildA:enter")) {
            System.out.println("FAIL: Expected ChildA:enter on init, got " + log);
            System.exit(1);
        }
        if (!s.get_state().equals("ChildA")) {
            System.out.println("FAIL: Expected ChildA, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC1.4.0: Initial state ChildA with enter - PASS");

        // TC1.4.1: Transition from ChildA to ChildB
        s.go_to_b();
        if (!s.get_state().equals("ChildB")) {
            System.out.println("FAIL: Expected ChildB, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC1.4.1: Transition A->B works - PASS");

        // TC1.4.2: Exit handler fired on source
        log = s.get_log();
        if (!log.contains("ChildA:exit")) {
            System.out.println("FAIL: Expected ChildA:exit, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.4.2: Exit handler fires on source - PASS");

        // TC1.4.3: Enter handler fired on target
        if (!log.contains("ChildB:enter")) {
            System.out.println("FAIL: Expected ChildB:enter, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.4.3: Enter handler fires on target - PASS");

        // TC1.4.4: Parent relationship preserved - ChildB can forward
        s.forward_action();
        log = s.get_log();
        if (!log.contains("ChildB:forward")) {
            System.out.println("FAIL: Expected ChildB:forward, got " + log);
            System.exit(1);
        }
        if (!log.contains("Parent:forward_action")) {
            System.out.println("FAIL: Expected Parent handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.4.4: Parent relationship preserved - PASS");

        // TC1.4.5: Transition back to ChildA
        s.go_to_a();
        if (!s.get_state().equals("ChildA")) {
            System.out.println("FAIL: Expected ChildA, got " + s.get_state());
            System.exit(1);
        }
        log = s.get_log();
        int exitBCount = 0;
        int enterACount = 0;
        for (Object item : log) {
            if (item.equals("ChildB:exit")) exitBCount++;
            if (item.equals("ChildA:enter")) enterACount++;
        }
        if (exitBCount != 1) {
            System.out.println("FAIL: Expected ChildB:exit once, got " + log);
            System.exit(1);
        }
        if (enterACount != 2) {
            System.out.println("FAIL: Expected ChildA:enter twice, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.4.5: Transition B->A works with enter/exit - PASS");

        // TC1.4.6: ChildA can still forward after returning
        s.forward_action();
        log = s.get_log();
        if (!log.contains("ChildA:forward")) {
            System.out.println("FAIL: Expected ChildA:forward, got " + log);
            System.exit(1);
        }
        int parentCount = 0;
        for (Object item : log) {
            if (item.equals("Parent:forward_action")) parentCount++;
        }
        if (parentCount != 2) {
            System.out.println("FAIL: Expected 2 Parent handlers, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.4.6: ChildA forwards after returning - PASS");

        System.out.println("PASS: HSM sibling transitions work correctly");
    }
}
