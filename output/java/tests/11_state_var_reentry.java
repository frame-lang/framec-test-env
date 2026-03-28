import java.util.*;


import java.util.*;

class StateVarReentryFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    StateVarReentryFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    StateVarReentryFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateVarReentryFrameContext {
    StateVarReentryFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    StateVarReentryFrameContext(StateVarReentryFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class StateVarReentryCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    StateVarReentryFrameEvent forward_event;
    StateVarReentryCompartment parent_compartment;

    StateVarReentryCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    StateVarReentryCompartment copy() {
        StateVarReentryCompartment c = new StateVarReentryCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateVarReentry {
    private ArrayList<StateVarReentryCompartment> _state_stack;
    private StateVarReentryCompartment __compartment;
    private StateVarReentryCompartment __next_compartment;
    private ArrayList<StateVarReentryFrameContext> _context_stack;

    public StateVarReentry() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new StateVarReentryCompartment("Counter");
        __next_compartment = null;
        StateVarReentryFrameEvent __frame_event = new StateVarReentryFrameEvent("$>");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(StateVarReentryFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateVarReentryFrameEvent exit_event = new StateVarReentryFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateVarReentryFrameEvent enter_event = new StateVarReentryFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    StateVarReentryFrameEvent enter_event = new StateVarReentryFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateVarReentryFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Counter")) {
            _state_Counter(__e);
        } else if (state_name.equals("Other")) {
            _state_Other(__e);
        }
    }

    private void __transition(StateVarReentryCompartment next) {
        __next_compartment = next;
    }

    public int increment() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("increment");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_count() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("get_count");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void go_other() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("go_other");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void come_back() {
        StateVarReentryFrameEvent __e = new StateVarReentryFrameEvent("come_back");
        StateVarReentryFrameContext __ctx = new StateVarReentryFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Other(StateVarReentryFrameEvent __e) {
        if (__e._message.equals("come_back")) {
            var __compartment = new StateVarReentryCompartment("Counter");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = -1;
            return;
        } else if (__e._message.equals("increment")) {
            _context_stack.get(_context_stack.size() - 1)._return = -1;
            return;
        }
    }

    private void _state_Counter(StateVarReentryFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Counter")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("count")) {
                __sv_comp.state_vars.put("count", 0);
            }
        } else if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("count");
            return;
        } else if (__e._message.equals("go_other")) {
            var __compartment = new StateVarReentryCompartment("Other");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("increment")) {
            __sv_comp.state_vars.put("count", (int) __sv_comp.state_vars.get("count") + 1);
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("count");
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 11: State Variable Reentry ===");
        var s = new StateVarReentry();

        // Increment a few times
        s.increment();
        s.increment();
        int count = (int) s.get_count();
        if (count != 2) {
            throw new RuntimeException("Expected 2 after two increments, got " + count);
        }
        System.out.println("Count before leaving: " + count);

        // Leave the state
        s.go_other();
        System.out.println("Transitioned to Other state");

        // Come back - state var should be reinitialized to 0
        s.come_back();
        count = (int) s.get_count();
        if (count != 0) {
            throw new RuntimeException("Expected 0 after re-entering Counter (state var reinit), got " + count);
        }
        System.out.println("Count after re-entering Counter: " + count);

        // Increment again to verify it works
        int result = (int) s.increment();
        if (result != 1) {
            throw new RuntimeException("Expected 1 after increment, got " + result);
        }
        System.out.println("After increment: " + result);

        System.out.println("PASS: State variables reinitialize on state reentry");
    }
}
