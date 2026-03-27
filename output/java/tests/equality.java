import java.util.*;


import java.util.*;

// Test: Equality operators in Frame handlers
// Tests: ==, !=

class EqualityTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    EqualityTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    EqualityTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class EqualityTestFrameContext {
    EqualityTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    EqualityTestFrameContext(EqualityTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class EqualityTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    EqualityTestFrameEvent forward_event;
    EqualityTestCompartment parent_compartment;

    EqualityTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    EqualityTestCompartment copy() {
        EqualityTestCompartment c = new EqualityTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class EqualityTest {
    private ArrayList<EqualityTestCompartment> _state_stack;
    private EqualityTestCompartment __compartment;
    private EqualityTestCompartment __next_compartment;
    private ArrayList<EqualityTestFrameContext> _context_stack;
    public int a = 5;
    public int b = 5;

    public EqualityTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new EqualityTestCompartment("Ready");
        __next_compartment = null;
        EqualityTestFrameEvent __frame_event = new EqualityTestFrameEvent("$>");
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(EqualityTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            EqualityTestFrameEvent exit_event = new EqualityTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                EqualityTestFrameEvent enter_event = new EqualityTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    EqualityTestFrameEvent enter_event = new EqualityTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(EqualityTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(EqualityTestCompartment next) {
        __next_compartment = next;
    }

    public boolean test_equal() {
        EqualityTestFrameEvent __e = new EqualityTestFrameEvent("test_equal");
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_not_equal() {
        EqualityTestFrameEvent __e = new EqualityTestFrameEvent("test_not_equal");
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void set_values(int x, int y) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("x", x);
        __params.put("y", y);
        EqualityTestFrameEvent __e = new EqualityTestFrameEvent("set_values", __params);
        EqualityTestFrameContext __ctx = new EqualityTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Ready(EqualityTestFrameEvent __e) {
        if (__e._message.equals("set_values")) {
            var x = (int) __e._parameters.get("x");
            var y = (int) __e._parameters.get("y");
            this.a = x;
            this.b = y;
        } else if (__e._message.equals("test_equal")) {
            if (this.a == this.b) {
                _context_stack.get(_context_stack.size() - 1)._return = true;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = false;
            }
        } else if (__e._message.equals("test_not_equal")) {
            if (this.a != this.b) {
                _context_stack.get(_context_stack.size() - 1)._return = true;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = false;
            }
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..4");

        EqualityTest s = new EqualityTest();

        // a=5, b=5: 5 == 5 is true
        if ((boolean) s.test_equal()) {
            System.out.println("ok 1 - 5 == 5 is true");
        } else {
            System.out.println("not ok 1 - 5 == 5 is true");
        }

        // a=5, b=5: 5 != 5 is false
        if (!(boolean) s.test_not_equal()) {
            System.out.println("ok 2 - 5 != 5 is false");
        } else {
            System.out.println("not ok 2 - 5 != 5 is false");
        }

        // Change values: a=5, b=3
        s.set_values(5, 3);

        // a=5, b=3: 5 == 3 is false
        if (!(boolean) s.test_equal()) {
            System.out.println("ok 3 - 5 == 3 is false");
        } else {
            System.out.println("not ok 3 - 5 == 3 is false");
        }

        // a=5, b=3: 5 != 3 is true
        if ((boolean) s.test_not_equal()) {
            System.out.println("ok 4 - 5 != 3 is true");
        } else {
            System.out.println("not ok 4 - 5 != 3 is true");
        }
    }
}
