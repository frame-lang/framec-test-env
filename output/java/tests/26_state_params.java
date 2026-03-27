import java.util.*;


import java.util.*;

class StateParamsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    StateParamsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    StateParamsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StateParamsFrameContext {
    StateParamsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    StateParamsFrameContext(StateParamsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class StateParamsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    StateParamsFrameEvent forward_event;
    StateParamsCompartment parent_compartment;

    StateParamsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    StateParamsCompartment copy() {
        StateParamsCompartment c = new StateParamsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StateParams {
    private ArrayList<StateParamsCompartment> _state_stack;
    private StateParamsCompartment __compartment;
    private StateParamsCompartment __next_compartment;
    private ArrayList<StateParamsFrameContext> _context_stack;

    public StateParams() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new StateParamsCompartment("Idle");
        __next_compartment = null;
        StateParamsFrameEvent __frame_event = new StateParamsFrameEvent("$>");
        StateParamsFrameContext __ctx = new StateParamsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(StateParamsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StateParamsFrameEvent exit_event = new StateParamsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StateParamsFrameEvent enter_event = new StateParamsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    StateParamsFrameEvent enter_event = new StateParamsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StateParamsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Counter")) {
            _state_Counter(__e);
        }
    }

    private void __transition(StateParamsCompartment next) {
        __next_compartment = next;
    }

    public void start(int val) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("val", val);
        StateParamsFrameEvent __e = new StateParamsFrameEvent("start", __params);
        StateParamsFrameContext __ctx = new StateParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public int get_value() {
        StateParamsFrameEvent __e = new StateParamsFrameEvent("get_value");
        StateParamsFrameContext __ctx = new StateParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Idle(StateParamsFrameEvent __e) {
        if (__e._message.equals("get_value")) {
            _context_stack.get(_context_stack.size() - 1)._return = 0;
            return;
        } else if (__e._message.equals("start")) {
            var val = (int) __e._parameters.get("val");
            var __compartment = new StateParamsCompartment("Counter");
            __compartment.parent_compartment = this.__compartment.copy();
            __compartment.state_args.put("0", val);
            __transition(__compartment);
            return;
        }
    }

    private void _state_Counter(StateParamsFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Counter")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("count")) {
                __sv_comp.state_vars.put("count", 0);
            }
            // Access state param via compartment - using string key "0"
            __sv_comp.state_vars.put("count", this.__compartment.state_args.get("0"));
            int count_val = (int) __sv_comp.state_vars.get("count");
            System.out.println("Counter entered with initial=" + count_val);
        } else if (__e._message.equals("get_value")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("count");
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 26: State Parameters ===");
        var s = new StateParams();

        int val = s.get_value();
        if (val != 0) {
            System.out.println("FAIL: Expected 0 in Idle, got " + val);
            System.exit(1);
        }
        System.out.println("Initial value: " + val);

        s.start(42);
        val = s.get_value();
        if (val != 42) {
            System.out.println("FAIL: Expected 42 in Counter from state param, got " + val);
            System.exit(1);
        }
        System.out.println("Value after transition: " + val);

        System.out.println("PASS: State parameters work correctly");
    }
}
