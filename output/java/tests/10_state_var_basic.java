import java.util.*;


import java.util.*;

class StateVarBasicFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    StateVarBasicFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    StateVarBasicFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateVarBasicFrameContext {
    StateVarBasicFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    StateVarBasicFrameContext(StateVarBasicFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class StateVarBasicCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    StateVarBasicFrameEvent forward_event;
    StateVarBasicCompartment parent_compartment;

    StateVarBasicCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    StateVarBasicCompartment copy() {
        StateVarBasicCompartment c = new StateVarBasicCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateVarBasic {
    private ArrayList<StateVarBasicCompartment> _state_stack;
    private StateVarBasicCompartment __compartment;
    private StateVarBasicCompartment __next_compartment;
    private ArrayList<StateVarBasicFrameContext> _context_stack;

    public StateVarBasic() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new StateVarBasicCompartment("Counter");
        __next_compartment = null;
        StateVarBasicFrameEvent __frame_event = new StateVarBasicFrameEvent("$>");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(StateVarBasicFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateVarBasicFrameEvent exit_event = new StateVarBasicFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateVarBasicFrameEvent enter_event = new StateVarBasicFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    StateVarBasicFrameEvent enter_event = new StateVarBasicFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateVarBasicFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Counter")) {
            _state_Counter(__e);
        }
    }

    private void __transition(StateVarBasicCompartment next) {
        __next_compartment = next;
    }

    public int increment() {
        StateVarBasicFrameEvent __e = new StateVarBasicFrameEvent("increment");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_count() {
        StateVarBasicFrameEvent __e = new StateVarBasicFrameEvent("get_count");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void reset() {
        StateVarBasicFrameEvent __e = new StateVarBasicFrameEvent("reset");
        StateVarBasicFrameContext __ctx = new StateVarBasicFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Counter(StateVarBasicFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Counter")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("count")) {
                __sv_comp.state_vars.put("count", 0);
            }
        } else if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("count");
            return;
        } else if (__e._message.equals("increment")) {
            __sv_comp.state_vars.put("count", (int) __sv_comp.state_vars.get("count") + 1);
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("count");
            return;
        } else if (__e._message.equals("reset")) {
            __sv_comp.state_vars.put("count", 0);
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 10: State Variable Basic ===");
        var s = new StateVarBasic();

        // Initial value should be 0
        int count = (int) s.get_count();
        if (count != 0) {
            throw new RuntimeException("Expected 0, got " + count);
        }
        System.out.println("Initial count: " + count);

        // Increment should return new value
        int result = (int) s.increment();
        if (result != 1) {
            throw new RuntimeException("Expected 1 after first increment, got " + result);
        }
        System.out.println("After first increment: " + result);

        // Second increment
        result = (int) s.increment();
        if (result != 2) {
            throw new RuntimeException("Expected 2 after second increment, got " + result);
        }
        System.out.println("After second increment: " + result);

        // Reset should set back to 0
        s.reset();
        count = (int) s.get_count();
        if (count != 0) {
            throw new RuntimeException("Expected 0 after reset, got " + count);
        }
        System.out.println("After reset: " + count);

        System.out.println("PASS: State variable basic operations work correctly");
    }
}
