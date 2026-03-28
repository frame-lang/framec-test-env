import java.util.*;


import java.util.*;

class HSMParentStateVarsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMParentStateVarsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMParentStateVarsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMParentStateVarsFrameContext {
    HSMParentStateVarsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMParentStateVarsFrameContext(HSMParentStateVarsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMParentStateVarsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMParentStateVarsFrameEvent forward_event;
    HSMParentStateVarsCompartment parent_compartment;

    HSMParentStateVarsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMParentStateVarsCompartment copy() {
        HSMParentStateVarsCompartment c = new HSMParentStateVarsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMParentStateVars {
    private ArrayList<HSMParentStateVarsCompartment> _state_stack;
    private HSMParentStateVarsCompartment __compartment;
    private HSMParentStateVarsCompartment __next_compartment;
    private ArrayList<HSMParentStateVarsFrameContext> _context_stack;

    public HSMParentStateVars() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMParentStateVarsCompartment("Parent");
        __parent_comp_0.state_vars.put("parent_count", 100);
        this.__compartment = new HSMParentStateVarsCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMParentStateVarsFrameEvent __frame_event = new HSMParentStateVarsFrameEvent("$>");
        HSMParentStateVarsFrameContext __ctx = new HSMParentStateVarsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMParentStateVarsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMParentStateVarsFrameEvent exit_event = new HSMParentStateVarsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMParentStateVarsFrameEvent enter_event = new HSMParentStateVarsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMParentStateVarsFrameEvent enter_event = new HSMParentStateVarsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMParentStateVarsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMParentStateVarsCompartment next) {
        __next_compartment = next;
    }

    public int get_child_count() {
        HSMParentStateVarsFrameEvent __e = new HSMParentStateVarsFrameEvent("get_child_count");
        HSMParentStateVarsFrameContext __ctx = new HSMParentStateVarsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_parent_count() {
        HSMParentStateVarsFrameEvent __e = new HSMParentStateVarsFrameEvent("get_parent_count");
        HSMParentStateVarsFrameContext __ctx = new HSMParentStateVarsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMParentStateVarsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Parent")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("parent_count")) {
                __sv_comp.state_vars.put("parent_count", 100);
            }
        } else if (__e._message.equals("get_parent_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("parent_count");
            return;
        }
    }

    private void _state_Child(HSMParentStateVarsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Child")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("child_count")) {
                __sv_comp.state_vars.put("child_count", 0);
            }
        } else if (__e._message.equals("get_child_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("child_count");
            return;
        } else if (__e._message.equals("get_parent_count")) {
            _state_Parent(__e);
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 40: HSM Parent State Variables ===");
        var s = new HSMParentStateVars();

        int childCount = s.get_child_count();
        if (childCount != 0) {
            System.out.println("FAIL: Expected child_count=0, got " + childCount);
            System.exit(1);
        }
        System.out.println("Child count: " + childCount);

        int parentCount = s.get_parent_count();
        if (parentCount != 100) {
            System.out.println("FAIL: Expected parent_count=100, got " + parentCount);
            System.exit(1);
        }
        System.out.println("Parent count: " + parentCount);

        System.out.println("PASS: HSM parent state variables work correctly");
    }
}
