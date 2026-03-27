import java.util.*;


import java.util.*;

class ReturnInitTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    ReturnInitTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    ReturnInitTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ReturnInitTestFrameContext {
    ReturnInitTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    ReturnInitTestFrameContext(ReturnInitTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class ReturnInitTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    ReturnInitTestFrameEvent forward_event;
    ReturnInitTestCompartment parent_compartment;

    ReturnInitTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    ReturnInitTestCompartment copy() {
        ReturnInitTestCompartment c = new ReturnInitTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ReturnInitTest {
    private ArrayList<ReturnInitTestCompartment> _state_stack;
    private ReturnInitTestCompartment __compartment;
    private ReturnInitTestCompartment __next_compartment;
    private ArrayList<ReturnInitTestFrameContext> _context_stack;

    public ReturnInitTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new ReturnInitTestCompartment("Start");
        __next_compartment = null;
        ReturnInitTestFrameEvent __frame_event = new ReturnInitTestFrameEvent("$>");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(ReturnInitTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ReturnInitTestFrameEvent exit_event = new ReturnInitTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ReturnInitTestFrameEvent enter_event = new ReturnInitTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    ReturnInitTestFrameEvent enter_event = new ReturnInitTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ReturnInitTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("Active")) {
            _state_Active(__e);
        }
    }

    private void __transition(ReturnInitTestCompartment next) {
        __next_compartment = next;
    }

    public String get_status() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("get_status");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, "unknown");
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_count() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("get_count");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, 0);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public boolean get_flag() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("get_flag");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, false);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void trigger() {
        ReturnInitTestFrameEvent __e = new ReturnInitTestFrameEvent("trigger");
        ReturnInitTestFrameContext __ctx = new ReturnInitTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Start(ReturnInitTestFrameEvent __e) {
        if (__e._message.equals("$>")) {
            // Start state enter (no-op)
        } else if (__e._message.equals("get_count")) {
            // Don't set return - should use default 0
        } else if (__e._message.equals("get_flag")) {
            // Don't set return - should use default false
        } else if (__e._message.equals("get_status")) {
            // Don't set return - should use default "unknown"
        } else if (__e._message.equals("trigger")) {
            var __compartment = new ReturnInitTestCompartment("Active");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Active(ReturnInitTestFrameEvent __e) {
        if (__e._message.equals("$>")) {
            // Active state enter (no-op)
        } else if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = 42;
        } else if (__e._message.equals("get_flag")) {
            _context_stack.get(_context_stack.size() - 1)._return = true;
        } else if (__e._message.equals("get_status")) {
            _context_stack.get(_context_stack.size() - 1)._return = "active";
        } else if (__e._message.equals("trigger")) {
            var __compartment = new ReturnInitTestCompartment("Start");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..6");

        var s = new ReturnInitTest();

        // Test 1: Default string return
        if (s.get_status().equals("unknown")) {
            System.out.println("ok 1 - default string return is 'unknown'");
        } else {
            System.out.println("not ok 1 - default string return is 'unknown' # got " + s.get_status());
        }

        // Test 2: Default int return
        if (s.get_count() == 0) {
            System.out.println("ok 2 - default int return is 0");
        } else {
            System.out.println("not ok 2 - default int return is 0 # got " + s.get_count());
        }

        // Test 3: Default bool return
        if (s.get_flag() == false) {
            System.out.println("ok 3 - default bool return is false");
        } else {
            System.out.println("not ok 3 - default bool return is false # got " + s.get_flag());
        }

        // Transition to Active state
        s.trigger();

        // Test 4: Explicit string return overrides default
        if (s.get_status().equals("active")) {
            System.out.println("ok 4 - explicit return overrides default string");
        } else {
            System.out.println("not ok 4 - explicit return overrides default string # got " + s.get_status());
        }

        // Test 5: Explicit int return overrides default
        if (s.get_count() == 42) {
            System.out.println("ok 5 - explicit return overrides default int");
        } else {
            System.out.println("not ok 5 - explicit return overrides default int # got " + s.get_count());
        }

        // Test 6: Explicit bool return overrides default
        if (s.get_flag() == true) {
            System.out.println("ok 6 - explicit return overrides default bool");
        } else {
            System.out.println("not ok 6 - explicit return overrides default bool # got " + s.get_flag());
        }

        System.out.println("# PASS - return_init provides default return values");
    }
}
