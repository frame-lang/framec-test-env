import java.util.*;


import java.util.*;

class ActionsTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    ActionsTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    ActionsTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ActionsTestFrameContext {
    ActionsTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    ActionsTestFrameContext(ActionsTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class ActionsTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    ActionsTestFrameEvent forward_event;
    ActionsTestCompartment parent_compartment;

    ActionsTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    ActionsTestCompartment copy() {
        ActionsTestCompartment c = new ActionsTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ActionsTest {
    private ArrayList<ActionsTestCompartment> _state_stack;
    private ActionsTestCompartment __compartment;
    private ActionsTestCompartment __next_compartment;
    private ArrayList<ActionsTestFrameContext> _context_stack;
    public String log = "";

    public ActionsTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new ActionsTestCompartment("Ready");
        __next_compartment = null;
        ActionsTestFrameEvent __frame_event = new ActionsTestFrameEvent("$>");
        ActionsTestFrameContext __ctx = new ActionsTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(ActionsTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ActionsTestFrameEvent exit_event = new ActionsTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ActionsTestFrameEvent enter_event = new ActionsTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    ActionsTestFrameEvent enter_event = new ActionsTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ActionsTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(ActionsTestCompartment next) {
        __next_compartment = next;
    }

    public int process(int value) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("value", value);
        ActionsTestFrameEvent __e = new ActionsTestFrameEvent("process", __params);
        ActionsTestFrameContext __ctx = new ActionsTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_log() {
        ActionsTestFrameEvent __e = new ActionsTestFrameEvent("get_log");
        ActionsTestFrameContext __ctx = new ActionsTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Ready(ActionsTestFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("process")) {
            var value = (int) __e._parameters.get("value");
            this.__log_event("start");
            this.__validate_positive(value);
            this.__log_event("valid");
            int result = value * 2;
            this.__log_event("done");
            _context_stack.get(_context_stack.size() - 1)._return = result;
            return;
        }
    }

    private void __log_event(String msg) {
                    this.log = this.log + msg + ";";
    }

    private void __validate_positive(int n) {
                    if (n < 0) {
                        throw new RuntimeException("Value must be positive: " + n);
                    }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 21: Actions Basic (Java) ===");
        var s = new ActionsTest();

        // Test 1: Actions are called correctly
        int result = s.process(5);
        if (result != 10) {
            System.out.println("FAIL: Expected 10, got " + result);
            System.exit(1);
        }
        System.out.println("1. process(5) = " + result);

        // Test 2: Log shows action calls
        String log = s.get_log();
        if (!log.contains("start")) {
            System.out.println("FAIL: Missing 'start' in log: " + log);
            System.exit(1);
        }
        if (!log.contains("valid")) {
            System.out.println("FAIL: Missing 'valid' in log: " + log);
            System.exit(1);
        }
        if (!log.contains("done")) {
            System.out.println("FAIL: Missing 'done' in log: " + log);
            System.exit(1);
        }
        System.out.println("2. Log: " + log);

        // Test 3: Action with validation
        try {
            s.process(-1);
            System.out.println("FAIL: Should have thrown RuntimeException");
            System.exit(1);
        } catch (RuntimeException e) {
            if (e.getMessage().contains("positive")) {
                System.out.println("3. Validation caught: " + e.getMessage());
            } else {
                throw e;
            }
        }

        System.out.println("PASS: Actions basic works correctly");
    }
}
