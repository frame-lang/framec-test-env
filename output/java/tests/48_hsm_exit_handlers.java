import java.util.*;


import java.util.*;

class HSMExitHandlersFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMExitHandlersFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMExitHandlersFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMExitHandlersFrameContext {
    HSMExitHandlersFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMExitHandlersFrameContext(HSMExitHandlersFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMExitHandlersCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMExitHandlersFrameEvent forward_event;
    HSMExitHandlersCompartment parent_compartment;

    HSMExitHandlersCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMExitHandlersCompartment copy() {
        HSMExitHandlersCompartment c = new HSMExitHandlersCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMExitHandlers {
    private ArrayList<HSMExitHandlersCompartment> _state_stack;
    private HSMExitHandlersCompartment __compartment;
    private HSMExitHandlersCompartment __next_compartment;
    private ArrayList<HSMExitHandlersFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMExitHandlers() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMExitHandlersCompartment("Parent");
        this.__compartment = new HSMExitHandlersCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMExitHandlersFrameEvent __frame_event = new HSMExitHandlersFrameEvent("$>");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMExitHandlersFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMExitHandlersFrameEvent exit_event = new HSMExitHandlersFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMExitHandlersFrameEvent enter_event = new HSMExitHandlersFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMExitHandlersFrameEvent enter_event = new HSMExitHandlersFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMExitHandlersFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        } else if (state_name.equals("Other")) {
            _state_Other(__e);
        }
    }

    private void __transition(HSMExitHandlersCompartment next) {
        __next_compartment = next;
    }

    public void go_to_other() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("go_to_other");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_to_parent() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("go_to_parent");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_to_child() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("go_to_child");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("get_log");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("get_state");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_child_var() {
        HSMExitHandlersFrameEvent __e = new HSMExitHandlersFrameEvent("get_child_var");
        HSMExitHandlersFrameContext __ctx = new HSMExitHandlersFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Other(HSMExitHandlersFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log.add("Other:enter");
        } else if (__e._message.equals("get_child_var")) {
            _context_stack.get(_context_stack.size() - 1)._return = -1;
            return;
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Other";
            return;
        } else if (__e._message.equals("go_to_child")) {
            var __compartment = new HSMExitHandlersCompartment("Child");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("go_to_parent")) {
            var __compartment = new HSMExitHandlersCompartment("Parent");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Parent(HSMExitHandlersFrameEvent __e) {
        if (__e._message.equals("<$")) {
            this.log.add("Parent:exit");
        } else if (__e._message.equals("$>")) {
            this.log.add("Parent:enter");
        } else if (__e._message.equals("get_child_var")) {
            _context_stack.get(_context_stack.size() - 1)._return = -1;
            return;
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        } else if (__e._message.equals("go_to_child")) {
            var __compartment = new HSMExitHandlersCompartment("Child");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("go_to_other")) {
            var __compartment = new HSMExitHandlersCompartment("Other");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Child(HSMExitHandlersFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Child")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("<$")) {
            int val = (int) __sv_comp.state_vars.get("child_var");
            this.log.add("Child:exit(var=" + val + ")");
        } else if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("child_var")) {
                __sv_comp.state_vars.put("child_var", 42);
            }
            this.log.add("Child:enter");
        } else if (__e._message.equals("get_child_var")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("child_var");
            return;
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Child";
            return;
        } else if (__e._message.equals("go_to_other")) {
            var __compartment = new HSMExitHandlersCompartment("Other");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("go_to_parent")) {
            var __compartment = new HSMExitHandlersCompartment("Parent");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 48: HSM Exit Handlers ===");
        var s = new HSMExitHandlers();

        // Initial state is Child
        ArrayList log = s.get_log();
        if (!log.contains("Child:enter")) {
            System.out.println("FAIL: Expected Child:enter on init, got " + log);
            System.exit(1);
        }
        if (!s.get_state().equals("Child")) {
            System.out.println("FAIL: Expected Child, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC2.4.0: Initial state is Child with enter - PASS");

        // TC2.4.1: Child exit fires when transitioning out of child
        s.go_to_other();
        log = s.get_log();
        if (!log.contains("Child:exit(var=42)")) {
            System.out.println("FAIL: Expected Child:exit, got " + log);
            System.exit(1);
        }
        if (!log.contains("Other:enter")) {
            System.out.println("FAIL: Expected Other:enter, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.4.1: Child exit fires when transitioning out - PASS");

        // TC2.4.2: Parent exit does NOT fire when transitioning out of child
        if (log.contains("Parent:exit")) {
            System.out.println("FAIL: Parent:exit should NOT fire for child exit, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.4.2: Parent exit NOT fired for child exit - PASS");

        // TC2.4.3: Exit handler can access child's state variables (verified by var=42 in log)
        System.out.println("TC2.4.3: Exit handler accesses state var (var=42) - PASS");

        // TC2.4.4: Parent exit fires when transitioning out of Parent
        s.go_to_parent();
        log = s.get_log();
        if (!log.contains("Parent:enter")) {
            System.out.println("FAIL: Expected Parent:enter, got " + log);
            System.exit(1);
        }

        s.go_to_other();
        log = s.get_log();
        if (!log.contains("Parent:exit")) {
            System.out.println("FAIL: Expected Parent:exit, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.4.4: Parent exit fires when leaving parent - PASS");

        System.out.println("PASS: HSM exit handlers work correctly");
    }
}
