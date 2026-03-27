import java.util.*;


import java.util.*;

// Test: Comparison operators in Frame handlers
// Tests: >, <, >=, <=, ==, !=

class ComparisonTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    ComparisonTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    ComparisonTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ComparisonTestFrameContext {
    ComparisonTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    ComparisonTestFrameContext(ComparisonTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class ComparisonTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    ComparisonTestFrameEvent forward_event;
    ComparisonTestCompartment parent_compartment;

    ComparisonTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    ComparisonTestCompartment copy() {
        ComparisonTestCompartment c = new ComparisonTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ComparisonTest {
    private ArrayList<ComparisonTestCompartment> _state_stack;
    private ComparisonTestCompartment __compartment;
    private ComparisonTestCompartment __next_compartment;
    private ArrayList<ComparisonTestFrameContext> _context_stack;
    public int a = 5;
    public int b = 3;

    public ComparisonTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new ComparisonTestCompartment("Ready");
        __next_compartment = null;
        ComparisonTestFrameEvent __frame_event = new ComparisonTestFrameEvent("$>");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(ComparisonTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ComparisonTestFrameEvent exit_event = new ComparisonTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ComparisonTestFrameEvent enter_event = new ComparisonTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    ComparisonTestFrameEvent enter_event = new ComparisonTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ComparisonTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(ComparisonTestCompartment next) {
        __next_compartment = next;
    }

    public boolean test_greater() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_greater");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_less() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_less");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_greater_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_greater_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_less_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_less_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_not_equal() {
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("test_not_equal");
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
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
        ComparisonTestFrameEvent __e = new ComparisonTestFrameEvent("set_values", __params);
        ComparisonTestFrameContext __ctx = new ComparisonTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Ready(ComparisonTestFrameEvent __e) {
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
        } else if (__e._message.equals("test_greater")) {
            if (this.a > this.b) {
                _context_stack.get(_context_stack.size() - 1)._return = true;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = false;
            }
        } else if (__e._message.equals("test_greater_equal")) {
            if (this.a >= this.b) {
                _context_stack.get(_context_stack.size() - 1)._return = true;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = false;
            }
        } else if (__e._message.equals("test_less")) {
            if (this.a < this.b) {
                _context_stack.get(_context_stack.size() - 1)._return = true;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = false;
            }
        } else if (__e._message.equals("test_less_equal")) {
            if (this.a <= this.b) {
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
        System.out.println("1..6");

        ComparisonTest s = new ComparisonTest();

        // a=5, b=3: 5 > 3 is true
        if ((boolean) s.test_greater()) {
            System.out.println("ok 1 - 5 > 3 is true");
        } else {
            System.out.println("not ok 1 - 5 > 3 is true");
        }

        // a=5, b=3: 5 < 3 is false
        if (!(boolean) s.test_less()) {
            System.out.println("ok 2 - 5 < 3 is false");
        } else {
            System.out.println("not ok 2 - 5 < 3 is false");
        }

        // a=5, b=3: 5 >= 3 is true
        if ((boolean) s.test_greater_equal()) {
            System.out.println("ok 3 - 5 >= 3 is true");
        } else {
            System.out.println("not ok 3 - 5 >= 3 is true");
        }

        // a=5, b=3: 5 <= 3 is false
        if (!(boolean) s.test_less_equal()) {
            System.out.println("ok 4 - 5 <= 3 is false");
        } else {
            System.out.println("not ok 4 - 5 <= 3 is false");
        }

        // a=5, b=3: 5 == 3 is false
        if (!(boolean) s.test_equal()) {
            System.out.println("ok 5 - 5 == 3 is false");
        } else {
            System.out.println("not ok 5 - 5 == 3 is false");
        }

        // a=5, b=3: 5 != 3 is true
        if ((boolean) s.test_not_equal()) {
            System.out.println("ok 6 - 5 != 3 is true");
        } else {
            System.out.println("not ok 6 - 5 != 3 is true");
        }
    }
}
