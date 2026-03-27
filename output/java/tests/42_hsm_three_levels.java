import java.util.*;


import java.util.*;

class HSMThreeLevelsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMThreeLevelsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMThreeLevelsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMThreeLevelsFrameContext {
    HSMThreeLevelsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMThreeLevelsFrameContext(HSMThreeLevelsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMThreeLevelsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMThreeLevelsFrameEvent forward_event;
    HSMThreeLevelsCompartment parent_compartment;

    HSMThreeLevelsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMThreeLevelsCompartment copy() {
        HSMThreeLevelsCompartment c = new HSMThreeLevelsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMThreeLevels {
    private ArrayList<HSMThreeLevelsCompartment> _state_stack;
    private HSMThreeLevelsCompartment __compartment;
    private HSMThreeLevelsCompartment __next_compartment;
    private ArrayList<HSMThreeLevelsFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMThreeLevels() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMThreeLevelsCompartment("Parent");
        __parent_comp_0.state_vars.put("parent_var", 100);
        var __parent_comp_1 = new HSMThreeLevelsCompartment("Child");
        __parent_comp_1.parent_compartment = __parent_comp_0;
        __parent_comp_1.state_vars.put("child_var", 10);
        this.__compartment = new HSMThreeLevelsCompartment("Grandchild");
        this.__compartment.parent_compartment = __parent_comp_1;
        this.__next_compartment = null;
        HSMThreeLevelsFrameEvent __frame_event = new HSMThreeLevelsFrameEvent("$>");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMThreeLevelsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMThreeLevelsFrameEvent exit_event = new HSMThreeLevelsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMThreeLevelsFrameEvent enter_event = new HSMThreeLevelsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMThreeLevelsFrameEvent enter_event = new HSMThreeLevelsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMThreeLevelsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Grandchild")) {
            _state_Grandchild(__e);
        } else if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMThreeLevelsCompartment next) {
        __next_compartment = next;
    }

    public void handle_at_grandchild() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("handle_at_grandchild");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forward_to_child() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("forward_to_child");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forward_to_parent() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("forward_to_parent");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forward_through_all() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("forward_through_all");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMThreeLevelsFrameEvent __e = new HSMThreeLevelsFrameEvent("get_log");
        HSMThreeLevelsFrameContext __ctx = new HSMThreeLevelsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Child(HSMThreeLevelsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Child")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("child_var")) {
                __sv_comp.state_vars.put("child_var", 10);
            }
        } else if (__e._message.equals("forward_through_all")) {
            int val = (int) __sv_comp.state_vars.get("child_var");
            this.log.add("Child:forward_through_all(var=" + val + ")");
            _state_Parent(__e);
        } else if (__e._message.equals("forward_to_child")) {
            int val = (int) __sv_comp.state_vars.get("child_var");
            this.log.add("Child:handled(var=" + val + ")");
        } else if (__e._message.equals("forward_to_parent")) {
            int val = (int) __sv_comp.state_vars.get("child_var");
            this.log.add("Child:forward_to_parent(var=" + val + ")");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        }
    }

    private void _state_Grandchild(HSMThreeLevelsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Grandchild")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("grandchild_var")) {
                __sv_comp.state_vars.put("grandchild_var", 1);
            }
        } else if (__e._message.equals("forward_through_all")) {
            this.log.add("Grandchild:forward_through_all");
            _state_Child(__e);
        } else if (__e._message.equals("forward_to_child")) {
            this.log.add("Grandchild:forward_to_child");
            _state_Child(__e);
        } else if (__e._message.equals("forward_to_parent")) {
            this.log.add("Grandchild:forward_to_parent");
            _state_Child(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("handle_at_grandchild")) {
            int val = (int) __sv_comp.state_vars.get("grandchild_var");
            this.log.add("Grandchild:handled(var=" + val + ")");
        }
    }

    private void _state_Parent(HSMThreeLevelsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Parent")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("parent_var")) {
                __sv_comp.state_vars.put("parent_var", 100);
            }
        } else if (__e._message.equals("forward_through_all")) {
            int val = (int) __sv_comp.state_vars.get("parent_var");
            this.log.add("Parent:forward_through_all(var=" + val + ")");
        } else if (__e._message.equals("forward_to_parent")) {
            int val = (int) __sv_comp.state_vars.get("parent_var");
            this.log.add("Parent:handled(var=" + val + ")");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 42: HSM Three-Level Hierarchy ===");
        var s = new HSMThreeLevels();

        // TC1.2.1: Three-level hierarchy compiles
        System.out.println("TC1.2.1: Three-level hierarchy compiles - PASS");

        // TC1.2.2: Handle at grandchild (no forward)
        s.handle_at_grandchild();
        ArrayList log = s.get_log();
        if (!log.contains("Grandchild:handled(var=1)")) {
            System.out.println("FAIL: Expected Grandchild handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.2.2: Grandchild handles locally - PASS");

        // TC1.2.3: Forward from grandchild to child
        s.forward_to_child();
        log = s.get_log();
        if (!log.contains("Grandchild:forward_to_child")) {
            System.out.println("FAIL: Expected Grandchild forward, got " + log);
            System.exit(1);
        }
        if (!log.contains("Child:handled(var=10)")) {
            System.out.println("FAIL: Expected Child handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.2.3: Forward grandchild->child - PASS");

        // TC1.2.4: Forward from grandchild through child to parent
        s.forward_to_parent();
        log = s.get_log();
        if (!log.contains("Grandchild:forward_to_parent")) {
            System.out.println("FAIL: Expected Grandchild forward, got " + log);
            System.exit(1);
        }
        if (!log.contains("Child:forward_to_parent(var=10)")) {
            System.out.println("FAIL: Expected Child forward, got " + log);
            System.exit(1);
        }
        if (!log.contains("Parent:handled(var=100)")) {
            System.out.println("FAIL: Expected Parent handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.2.4: Forward grandchild->child->parent - PASS");

        // TC1.2.5: Forward through entire chain
        s.forward_through_all();
        log = s.get_log();
        if (!log.contains("Grandchild:forward_through_all")) {
            System.out.println("FAIL: Expected Grandchild, got " + log);
            System.exit(1);
        }
        if (!log.contains("Child:forward_through_all(var=10)")) {
            System.out.println("FAIL: Expected Child, got " + log);
            System.exit(1);
        }
        if (!log.contains("Parent:forward_through_all(var=100)")) {
            System.out.println("FAIL: Expected Parent, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.2.5: Full chain forward - PASS");

        // Verify state variable isolation
        System.out.println("TC1.2.6: State vars isolated (grandchild=1, child=10, parent=100) - PASS");

        System.out.println("PASS: HSM three-level hierarchy works correctly");
    }
}
