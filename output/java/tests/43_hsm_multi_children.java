import java.util.*;


import java.util.*;

class HSMMultiChildrenFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMMultiChildrenFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMMultiChildrenFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMMultiChildrenFrameContext {
    HSMMultiChildrenFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMMultiChildrenFrameContext(HSMMultiChildrenFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMMultiChildrenCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMMultiChildrenFrameEvent forward_event;
    HSMMultiChildrenCompartment parent_compartment;

    HSMMultiChildrenCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMMultiChildrenCompartment copy() {
        HSMMultiChildrenCompartment c = new HSMMultiChildrenCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMMultiChildren {
    private ArrayList<HSMMultiChildrenCompartment> _state_stack;
    private HSMMultiChildrenCompartment __compartment;
    private HSMMultiChildrenCompartment __next_compartment;
    private ArrayList<HSMMultiChildrenFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMMultiChildren() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMMultiChildrenCompartment("Parent");
        this.__compartment = new HSMMultiChildrenCompartment("ChildA");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMMultiChildrenFrameEvent __frame_event = new HSMMultiChildrenFrameEvent("$>");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMMultiChildrenFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMMultiChildrenFrameEvent exit_event = new HSMMultiChildrenFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMMultiChildrenFrameEvent enter_event = new HSMMultiChildrenFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMMultiChildrenFrameEvent enter_event = new HSMMultiChildrenFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMMultiChildrenFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("ChildA")) {
            _state_ChildA(__e);
        } else if (state_name.equals("ChildB")) {
            _state_ChildB(__e);
        } else if (state_name.equals("ChildC")) {
            _state_ChildC(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMMultiChildrenCompartment next) {
        __next_compartment = next;
    }

    public void start_a() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("start_a");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void start_b() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("start_b");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void start_c() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("start_c");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void do_action() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("do_action");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forward_action() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("forward_action");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("get_log");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMMultiChildrenFrameEvent __e = new HSMMultiChildrenFrameEvent("get_state");
        HSMMultiChildrenFrameContext __ctx = new HSMMultiChildrenFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMMultiChildrenFrameEvent __e) {
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

    private void _state_ChildB(HSMMultiChildrenFrameEvent __e) {
        if (__e._message.equals("do_action")) {
            this.log.add("ChildB:do_action");
        } else if (__e._message.equals("forward_action")) {
            this.log.add("ChildB:forward_action");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "ChildB";
            return;
        } else if (__e._message.equals("start_a")) {
            var __compartment = new HSMMultiChildrenCompartment("ChildA");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("start_b")) {
            // stay
        } else if (__e._message.equals("start_c")) {
            var __compartment = new HSMMultiChildrenCompartment("ChildC");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_ChildA(HSMMultiChildrenFrameEvent __e) {
        if (__e._message.equals("do_action")) {
            this.log.add("ChildA:do_action");
        } else if (__e._message.equals("forward_action")) {
            this.log.add("ChildA:forward_action");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "ChildA";
            return;
        } else if (__e._message.equals("start_a")) {
            // stay
        } else if (__e._message.equals("start_b")) {
            var __compartment = new HSMMultiChildrenCompartment("ChildB");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("start_c")) {
            var __compartment = new HSMMultiChildrenCompartment("ChildC");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_ChildC(HSMMultiChildrenFrameEvent __e) {
        if (__e._message.equals("do_action")) {
            this.log.add("ChildC:do_action");
        } else if (__e._message.equals("forward_action")) {
            this.log.add("ChildC:forward_action");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "ChildC";
            return;
        } else if (__e._message.equals("start_a")) {
            var __compartment = new HSMMultiChildrenCompartment("ChildA");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("start_b")) {
            var __compartment = new HSMMultiChildrenCompartment("ChildB");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("start_c")) {
            // stay
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 43: HSM Multiple Children ===");
        var s = new HSMMultiChildren();

        // TC1.3.1: Multiple children declare same parent (verified by compilation)
        System.out.println("TC1.3.1: Multiple children with same parent compiles - PASS");

        // Start in ChildA
        if (!s.get_state().equals("ChildA")) {
            System.out.println("FAIL: Expected ChildA, got " + s.get_state());
            System.exit(1);
        }

        // TC1.3.2: ChildA can forward to shared parent
        s.forward_action();
        ArrayList log = s.get_log();
        if (!log.contains("ChildA:forward_action")) {
            System.out.println("FAIL: Expected ChildA forward, got " + log);
            System.exit(1);
        }
        if (!log.contains("Parent:forward_action")) {
            System.out.println("FAIL: Expected Parent handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.3.2: ChildA forwards to parent - PASS");

        // TC1.3.3: Transition to sibling
        s.start_b();
        if (!s.get_state().equals("ChildB")) {
            System.out.println("FAIL: Expected ChildB after transition, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC1.3.3: Transition A->B works - PASS");

        // TC1.3.4: ChildB can also forward to same parent
        s.forward_action();
        log = s.get_log();
        if (!log.contains("ChildB:forward_action")) {
            System.out.println("FAIL: Expected ChildB forward, got " + log);
            System.exit(1);
        }
        int parentCount = 0;
        for (Object item : log) {
            if (item.equals("Parent:forward_action")) parentCount++;
        }
        if (parentCount != 2) {
            System.out.println("FAIL: Expected 2 Parent forwards, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.3.4: ChildB forwards to same parent - PASS");

        // TC1.3.5: Transition to ChildC
        s.start_c();
        if (!s.get_state().equals("ChildC")) {
            System.out.println("FAIL: Expected ChildC, got " + s.get_state());
            System.exit(1);
        }
        s.forward_action();
        log = s.get_log();
        if (!log.contains("ChildC:forward_action")) {
            System.out.println("FAIL: Expected ChildC forward, got " + log);
            System.exit(1);
        }
        int parentCount2 = 0;
        for (Object item : log) {
            if (item.equals("Parent:forward_action")) parentCount2++;
        }
        if (parentCount2 != 3) {
            System.out.println("FAIL: Expected 3 Parent forwards, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.3.5: ChildC forwards to same parent - PASS");

        // TC1.3.6: Each sibling maintains independent actions
        s.start_a();
        s.do_action();
        s.start_b();
        s.do_action();
        s.start_c();
        s.do_action();
        log = s.get_log();
        if (!log.contains("ChildA:do_action")) {
            System.out.println("FAIL: Expected ChildA action");
            System.exit(1);
        }
        if (!log.contains("ChildB:do_action")) {
            System.out.println("FAIL: Expected ChildB action");
            System.exit(1);
        }
        if (!log.contains("ChildC:do_action")) {
            System.out.println("FAIL: Expected ChildC action");
            System.exit(1);
        }
        System.out.println("TC1.3.6: Each sibling has independent handlers - PASS");

        System.out.println("PASS: HSM multiple children work correctly");
    }
}
