import java.util.*;


import java.util.*;

// NOTE: Default return value syntax (method(): type = default) not yet implemented.
// This test validates behavior when handler doesn't set @@:return.

class SystemReturnDefaultTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SystemReturnDefaultTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SystemReturnDefaultTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnDefaultTestFrameContext {
    SystemReturnDefaultTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SystemReturnDefaultTestFrameContext(SystemReturnDefaultTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SystemReturnDefaultTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SystemReturnDefaultTestFrameEvent forward_event;
    SystemReturnDefaultTestCompartment parent_compartment;

    SystemReturnDefaultTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SystemReturnDefaultTestCompartment copy() {
        SystemReturnDefaultTestCompartment c = new SystemReturnDefaultTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnDefaultTest {
    private ArrayList<SystemReturnDefaultTestCompartment> _state_stack;
    private SystemReturnDefaultTestCompartment __compartment;
    private SystemReturnDefaultTestCompartment __next_compartment;
    private ArrayList<SystemReturnDefaultTestFrameContext> _context_stack;

    public SystemReturnDefaultTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SystemReturnDefaultTestCompartment("Start");
        __next_compartment = null;
        SystemReturnDefaultTestFrameEvent __frame_event = new SystemReturnDefaultTestFrameEvent("$>");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SystemReturnDefaultTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnDefaultTestFrameEvent exit_event = new SystemReturnDefaultTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnDefaultTestFrameEvent enter_event = new SystemReturnDefaultTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SystemReturnDefaultTestFrameEvent enter_event = new SystemReturnDefaultTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnDefaultTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        }
    }

    private void __transition(SystemReturnDefaultTestCompartment next) {
        __next_compartment = next;
    }

    public String handler_sets_value() {
        SystemReturnDefaultTestFrameEvent __e = new SystemReturnDefaultTestFrameEvent("handler_sets_value");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String handler_no_return() {
        SystemReturnDefaultTestFrameEvent __e = new SystemReturnDefaultTestFrameEvent("handler_no_return");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_count() {
        SystemReturnDefaultTestFrameEvent __e = new SystemReturnDefaultTestFrameEvent("get_count");
        SystemReturnDefaultTestFrameContext __ctx = new SystemReturnDefaultTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Start(SystemReturnDefaultTestFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Start")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("count")) {
                __sv_comp.state_vars.put("count", 0);
            }
        } else if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("count");
            return;
        } else if (__e._message.equals("handler_no_return")) {
            // Does not set return - should return null
            __sv_comp.state_vars.put("count", (int) __sv_comp.state_vars.get("count") + 1);
        } else if (__e._message.equals("handler_sets_value")) {
            _context_stack.get(_context_stack.size() - 1)._return = "set_by_handler";
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 14: System Return Default Behavior ===");
        var s = new SystemReturnDefaultTest();

        // Test 1: Handler explicitly sets return value
        String result1 = (String) s.handler_sets_value();
        if (!"set_by_handler".equals(result1)) {
            throw new RuntimeException("Expected 'set_by_handler', got '" + result1 + "'");
        }
        System.out.println("1. handler_sets_value() = '" + result1 + "'");

        // Test 2: Handler does NOT set return - should return null
        String result2 = (String) s.handler_no_return();
        if (result2 != null) {
            throw new RuntimeException("Expected null, got '" + result2 + "'");
        }
        System.out.println("2. handler_no_return() = " + result2);

        // Test 3: Verify handler was called (side effect check)
        int count = (int) s.get_count();
        if (count != 1) {
            throw new RuntimeException("Expected count=1, got " + count);
        }
        System.out.println("3. Handler was called, count = " + count);

        // Test 4: Call again to verify idempotence
        String result4 = (String) s.handler_no_return();
        if (result4 != null) {
            throw new RuntimeException("Expected null again, got '" + result4 + "'");
        }
        count = (int) s.get_count();
        if (count != 2) {
            throw new RuntimeException("Expected count=2, got " + count);
        }
        System.out.println("4. Second call: result=" + result4 + ", count=" + count);

        System.out.println("PASS: System return default behavior works correctly");
    }
}
