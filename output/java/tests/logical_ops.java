import java.util.*;


import java.util.*;

// Test: Logical operators in Frame handlers
// Tests: &&, ||, !

class LogicalTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    LogicalTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    LogicalTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class LogicalTestFrameContext {
    LogicalTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    LogicalTestFrameContext(LogicalTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class LogicalTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    LogicalTestFrameEvent forward_event;
    LogicalTestCompartment parent_compartment;

    LogicalTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    LogicalTestCompartment copy() {
        LogicalTestCompartment c = new LogicalTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class LogicalTest {
    private ArrayList<LogicalTestCompartment> _state_stack;
    private LogicalTestCompartment __compartment;
    private LogicalTestCompartment __next_compartment;
    private ArrayList<LogicalTestFrameContext> _context_stack;
    public boolean a = true;
    public boolean b = false;

    public LogicalTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new LogicalTestCompartment("Ready");
        __next_compartment = null;
        LogicalTestFrameEvent __frame_event = new LogicalTestFrameEvent("$>");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(LogicalTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            LogicalTestFrameEvent exit_event = new LogicalTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                LogicalTestFrameEvent enter_event = new LogicalTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    LogicalTestFrameEvent enter_event = new LogicalTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(LogicalTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(LogicalTestCompartment next) {
        __next_compartment = next;
    }

    public boolean test_and() {
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("test_and");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_or() {
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("test_or");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean test_not() {
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("test_not");
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void set_values(boolean x, boolean y) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("x", x);
        __params.put("y", y);
        LogicalTestFrameEvent __e = new LogicalTestFrameEvent("set_values", __params);
        LogicalTestFrameContext __ctx = new LogicalTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Ready(LogicalTestFrameEvent __e) {
        if (__e._message.equals("set_values")) {
            var x = (boolean) __e._parameters.get("x");
            var y = (boolean) __e._parameters.get("y");
            this.a = x;
            this.b = y;
        } else if (__e._message.equals("test_and")) {
            if (this.a && this.b) {
                _context_stack.get(_context_stack.size() - 1)._return = true;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = false;
            }
        } else if (__e._message.equals("test_not")) {
            if (!this.a) {
                _context_stack.get(_context_stack.size() - 1)._return = true;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = false;
            }
        } else if (__e._message.equals("test_or")) {
            if (this.a || this.b) {
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

        LogicalTest s = new LogicalTest();

        // a=true, b=false: true && false = false
        if (!(boolean) s.test_and()) {
            System.out.println("ok 1 - true && false is false");
        } else {
            System.out.println("not ok 1 - true && false is false");
        }

        // a=true, b=false: true || false = true
        if ((boolean) s.test_or()) {
            System.out.println("ok 2 - true || false is true");
        } else {
            System.out.println("not ok 2 - true || false is true");
        }

        // a=true: !true = false
        if (!(boolean) s.test_not()) {
            System.out.println("ok 3 - !true is false");
        } else {
            System.out.println("not ok 3 - !true is false");
        }

        // Change values: a=true, b=true
        s.set_values(true, true);

        // true && true = true
        if ((boolean) s.test_and()) {
            System.out.println("ok 4 - true && true is true");
        } else {
            System.out.println("not ok 4 - true && true is true");
        }

        // Change values: a=false, b=false
        s.set_values(false, false);

        // false || false = false
        if (!(boolean) s.test_or()) {
            System.out.println("ok 5 - false || false is false");
        } else {
            System.out.println("not ok 5 - false || false is false");
        }

        // !false = true
        if ((boolean) s.test_not()) {
            System.out.println("ok 6 - !false is true");
        } else {
            System.out.println("not ok 6 - !false is true");
        }
    }
}
