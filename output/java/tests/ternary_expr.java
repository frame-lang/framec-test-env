import java.util.*;


import java.util.*;

// Test: Ternary/conditional expressions in Frame handlers
// Java uses: cond ? a : b

class TernaryTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    TernaryTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    TernaryTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TernaryTestFrameContext {
    TernaryTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    TernaryTestFrameContext(TernaryTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class TernaryTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    TernaryTestFrameEvent forward_event;
    TernaryTestCompartment parent_compartment;

    TernaryTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    TernaryTestCompartment copy() {
        TernaryTestCompartment c = new TernaryTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TernaryTest {
    private ArrayList<TernaryTestCompartment> _state_stack;
    private TernaryTestCompartment __compartment;
    private TernaryTestCompartment __next_compartment;
    private ArrayList<TernaryTestFrameContext> _context_stack;
    public boolean cond = true;

    public TernaryTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new TernaryTestCompartment("Ready");
        __next_compartment = null;
        TernaryTestFrameEvent __frame_event = new TernaryTestFrameEvent("$>");
        TernaryTestFrameContext __ctx = new TernaryTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(TernaryTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TernaryTestFrameEvent exit_event = new TernaryTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TernaryTestFrameEvent enter_event = new TernaryTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    TernaryTestFrameEvent enter_event = new TernaryTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TernaryTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(TernaryTestCompartment next) {
        __next_compartment = next;
    }

    public int get_value() {
        TernaryTestFrameEvent __e = new TernaryTestFrameEvent("get_value");
        TernaryTestFrameContext __ctx = new TernaryTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void set_condition(boolean c) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("c", c);
        TernaryTestFrameEvent __e = new TernaryTestFrameEvent("set_condition", __params);
        TernaryTestFrameContext __ctx = new TernaryTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Ready(TernaryTestFrameEvent __e) {
        if (__e._message.equals("get_value")) {
            int result = this.cond ? 100 : 200;
            _context_stack.get(_context_stack.size() - 1)._return = result;
        } else if (__e._message.equals("set_condition")) {
            var c = (boolean) __e._parameters.get("c");
            this.cond = c;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..2");

        TernaryTest s = new TernaryTest();

        // cond=true: should return 100
        int v1 = (int) s.get_value();
        if (v1 == 100) {
            System.out.println("ok 1 - cond=true returns 100");
        } else {
            System.out.println("not ok 1 - cond=true returns 100 # got " + v1);
        }

        // cond=false: should return 200
        s.set_condition(false);
        int v2 = (int) s.get_value();
        if (v2 == 200) {
            System.out.println("ok 2 - cond=false returns 200");
        } else {
            System.out.println("not ok 2 - cond=false returns 200 # got " + v2);
        }
    }
}
