import java.util.*;


import java.util.*;

class StateVarPushPopFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    StateVarPushPopFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    StateVarPushPopFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateVarPushPopFrameContext {
    StateVarPushPopFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    StateVarPushPopFrameContext(StateVarPushPopFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class StateVarPushPopCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    StateVarPushPopFrameEvent forward_event;
    StateVarPushPopCompartment parent_compartment;

    StateVarPushPopCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    StateVarPushPopCompartment copy() {
        StateVarPushPopCompartment c = new StateVarPushPopCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateVarPushPop {
    private ArrayList<StateVarPushPopCompartment> _state_stack;
    private StateVarPushPopCompartment __compartment;
    private StateVarPushPopCompartment __next_compartment;
    private ArrayList<StateVarPushPopFrameContext> _context_stack;

    public StateVarPushPop() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new StateVarPushPopCompartment("Counter");
        __next_compartment = null;
        StateVarPushPopFrameEvent __frame_event = new StateVarPushPopFrameEvent("$>");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(StateVarPushPopFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateVarPushPopFrameEvent exit_event = new StateVarPushPopFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateVarPushPopFrameEvent enter_event = new StateVarPushPopFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    StateVarPushPopFrameEvent enter_event = new StateVarPushPopFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateVarPushPopFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Counter")) {
            _state_Counter(__e);
        } else if (state_name.equals("Other")) {
            _state_Other(__e);
        }
    }

    private void __transition(StateVarPushPopCompartment next) {
        __next_compartment = next;
    }

    public int increment() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("increment");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_count() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("get_count");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void save_and_go() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("save_and_go");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void restore() {
        StateVarPushPopFrameEvent __e = new StateVarPushPopFrameEvent("restore");
        StateVarPushPopFrameContext __ctx = new StateVarPushPopFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Counter(StateVarPushPopFrameEvent __e) {
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
        } else if (__e._message.equals("save_and_go")) {
            _state_stack.add(__compartment.copy());
            var __compartment = new StateVarPushPopCompartment("Other");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Other(StateVarPushPopFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Other")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("other_count")) {
                __sv_comp.state_vars.put("other_count", 100);
            }
        } else if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("other_count");
            return;
        } else if (__e._message.equals("increment")) {
            __sv_comp.state_vars.put("other_count", (int) __sv_comp.state_vars.get("other_count") + 1);
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("other_count");
            return;
        } else if (__e._message.equals("restore")) {
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 12: State Variable Push/Pop ===");
        var s = new StateVarPushPop();

        // Increment counter to 3
        s.increment();
        s.increment();
        s.increment();
        int count = (int) s.get_count();
        if (count != 3) {
            throw new RuntimeException("Expected 3, got " + count);
        }
        System.out.println("Counter before push: " + count);

        // Push and go to Other state
        s.save_and_go();
        System.out.println("Pushed and transitioned to Other");

        // In Other state, count should be 100 (Other's state var)
        count = (int) s.get_count();
        if (count != 100) {
            throw new RuntimeException("Expected 100 in Other state, got " + count);
        }
        System.out.println("Other state count: " + count);

        // Increment in Other
        s.increment();
        count = (int) s.get_count();
        if (count != 101) {
            throw new RuntimeException("Expected 101 after increment, got " + count);
        }
        System.out.println("Other state after increment: " + count);

        // Pop back - should restore Counter with count=3
        s.restore();
        System.out.println("Popped back to Counter");

        count = (int) s.get_count();
        if (count != 3) {
            throw new RuntimeException("Expected 3 after pop (preserved), got " + count);
        }
        System.out.println("Counter after pop: " + count);

        // Increment to verify it works
        s.increment();
        count = (int) s.get_count();
        if (count != 4) {
            throw new RuntimeException("Expected 4, got " + count);
        }
        System.out.println("Counter after increment: " + count);

        System.out.println("PASS: State variables preserved across push/pop");
    }
}
