import java.util.*;


import java.util.*;

class HSMOmittedHandlersFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMOmittedHandlersFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMOmittedHandlersFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMOmittedHandlersFrameContext {
    HSMOmittedHandlersFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMOmittedHandlersFrameContext(HSMOmittedHandlersFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMOmittedHandlersCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMOmittedHandlersFrameEvent forward_event;
    HSMOmittedHandlersCompartment parent_compartment;

    HSMOmittedHandlersCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMOmittedHandlersCompartment copy() {
        HSMOmittedHandlersCompartment c = new HSMOmittedHandlersCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMOmittedHandlers {
    private ArrayList<HSMOmittedHandlersCompartment> _state_stack;
    private HSMOmittedHandlersCompartment __compartment;
    private HSMOmittedHandlersCompartment __next_compartment;
    private ArrayList<HSMOmittedHandlersFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMOmittedHandlers() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMOmittedHandlersCompartment("Parent");
        this.__compartment = new HSMOmittedHandlersCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMOmittedHandlersFrameEvent __frame_event = new HSMOmittedHandlersFrameEvent("$>");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMOmittedHandlersFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMOmittedHandlersFrameEvent exit_event = new HSMOmittedHandlersFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMOmittedHandlersFrameEvent enter_event = new HSMOmittedHandlersFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMOmittedHandlersFrameEvent enter_event = new HSMOmittedHandlersFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMOmittedHandlersFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMOmittedHandlersCompartment next) {
        __next_compartment = next;
    }

    public void handled_by_child() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("handled_by_child");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forwarded_explicitly() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("forwarded_explicitly");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void unhandled_no_forward() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("unhandled_no_forward");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("get_log");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMOmittedHandlersFrameEvent __e = new HSMOmittedHandlersFrameEvent("get_state");
        HSMOmittedHandlersFrameContext __ctx = new HSMOmittedHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMOmittedHandlersFrameEvent __e) {
        if (__e._message.equals("forwarded_explicitly")) {
            this.log.add("Parent:forwarded_explicitly");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        } else if (__e._message.equals("handled_by_child")) {
            this.log.add("Parent:handled_by_child");
        } else if (__e._message.equals("unhandled_no_forward")) {
            this.log.add("Parent:unhandled_no_forward");
        }
    }

    private void _state_Child(HSMOmittedHandlersFrameEvent __e) {
        if (__e._message.equals("forwarded_explicitly")) {
            this.log.add("Child:before_forward");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Child";
            return;
        } else if (__e._message.equals("handled_by_child")) {
            this.log.add("Child:handled_by_child");
        }
    }
}

class HSMDefaultForward2FrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMDefaultForward2FrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMDefaultForward2FrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMDefaultForward2FrameContext {
    HSMDefaultForward2FrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMDefaultForward2FrameContext(HSMDefaultForward2FrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMDefaultForward2Compartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMDefaultForward2FrameEvent forward_event;
    HSMDefaultForward2Compartment parent_compartment;

    HSMDefaultForward2Compartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMDefaultForward2Compartment copy() {
        HSMDefaultForward2Compartment c = new HSMDefaultForward2Compartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMDefaultForward2 {
    private ArrayList<HSMDefaultForward2Compartment> _state_stack;
    private HSMDefaultForward2Compartment __compartment;
    private HSMDefaultForward2Compartment __next_compartment;
    private ArrayList<HSMDefaultForward2FrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMDefaultForward2() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMDefaultForward2Compartment("Parent");
        this.__compartment = new HSMDefaultForward2Compartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMDefaultForward2FrameEvent __frame_event = new HSMDefaultForward2FrameEvent("$>");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMDefaultForward2FrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMDefaultForward2FrameEvent exit_event = new HSMDefaultForward2FrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMDefaultForward2FrameEvent enter_event = new HSMDefaultForward2FrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMDefaultForward2FrameEvent enter_event = new HSMDefaultForward2FrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMDefaultForward2FrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMDefaultForward2Compartment next) {
        __next_compartment = next;
    }

    public void child_handled() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("child_handled");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void parent_handled() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("parent_handled");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void both_respond() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("both_respond");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMDefaultForward2FrameEvent __e = new HSMDefaultForward2FrameEvent("get_log");
        HSMDefaultForward2FrameContext __ctx = new HSMDefaultForward2FrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMDefaultForward2FrameEvent __e) {
        if (__e._message.equals("both_respond")) {
            this.log.add("Parent:both_respond");
        } else if (__e._message.equals("child_handled")) {
            this.log.add("Parent:child_handled");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("parent_handled")) {
            this.log.add("Parent:parent_handled");
        }
    }

    private void _state_Child(HSMDefaultForward2FrameEvent __e) {
        if (__e._message.equals("child_handled")) {
            this.log.add("Child:child_handled");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else {
            _state_Parent(__e);
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 50: HSM Omitted Handlers ===");

        // Part 1: Explicit forwarding vs no forwarding
        var s1 = new HSMOmittedHandlers();

        // TC2.6.1: Event handled by child only
        s1.handled_by_child();
        ArrayList log = s1.get_log();
        if (!log.contains("Child:handled_by_child")) {
            System.out.println("FAIL: Expected Child handler, got " + log);
            System.exit(1);
        }
        if (log.contains("Parent:handled_by_child")) {
            System.out.println("FAIL: Parent should NOT be called, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.6.1: Handled by child, not forwarded - PASS");

        // TC2.6.2: Event explicitly forwarded to parent
        s1.forwarded_explicitly();
        log = s1.get_log();
        if (!log.contains("Child:before_forward")) {
            System.out.println("FAIL: Expected Child forward, got " + log);
            System.exit(1);
        }
        if (!log.contains("Parent:forwarded_explicitly")) {
            System.out.println("FAIL: Expected Parent handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.6.2: Explicitly forwarded to parent - PASS");

        // TC2.6.3: Unhandled event with no forward - silently ignored
        s1.unhandled_no_forward();
        log = s1.get_log();
        if (log.contains("Parent:unhandled_no_forward")) {
            System.out.println("FAIL: Unhandled should be ignored, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.6.3: Unhandled (no forward) is silently ignored - PASS");

        // Part 2: State-level default forward
        var s2 = new HSMDefaultForward2();

        // TC2.6.4: Event handled by child (no forward despite => $^)
        s2.child_handled();
        log = s2.get_log();
        if (!log.contains("Child:child_handled")) {
            System.out.println("FAIL: Expected Child handler, got " + log);
            System.exit(1);
        }
        if (log.contains("Parent:child_handled")) {
            System.out.println("FAIL: Handled by child, not forwarded, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.6.4: Child handles, not forwarded - PASS");

        // TC2.6.5: Unhandled event forwarded via => $^
        s2.parent_handled();
        log = s2.get_log();
        if (!log.contains("Parent:parent_handled")) {
            System.out.println("FAIL: Expected Parent handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.6.5: Unhandled forwarded via state-level => $^ - PASS");

        // TC2.6.6: Another unhandled event forwarded
        s2.both_respond();
        log = s2.get_log();
        if (!log.contains("Parent:both_respond")) {
            System.out.println("FAIL: Expected Parent handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.6.6: Default forward works for multiple events - PASS");

        System.out.println("PASS: HSM omitted handlers work correctly");
    }
}
