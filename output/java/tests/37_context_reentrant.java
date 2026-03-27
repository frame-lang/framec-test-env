import java.util.*;


import java.util.*;

class ContextReentrantTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    ContextReentrantTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    ContextReentrantTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ContextReentrantTestFrameContext {
    ContextReentrantTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    ContextReentrantTestFrameContext(ContextReentrantTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class ContextReentrantTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    ContextReentrantTestFrameEvent forward_event;
    ContextReentrantTestCompartment parent_compartment;

    ContextReentrantTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    ContextReentrantTestCompartment copy() {
        ContextReentrantTestCompartment c = new ContextReentrantTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ContextReentrantTest {
    private ArrayList<ContextReentrantTestCompartment> _state_stack;
    private ContextReentrantTestCompartment __compartment;
    private ContextReentrantTestCompartment __next_compartment;
    private ArrayList<ContextReentrantTestFrameContext> _context_stack;

    public ContextReentrantTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new ContextReentrantTestCompartment("Ready");
        __next_compartment = null;
        ContextReentrantTestFrameEvent __frame_event = new ContextReentrantTestFrameEvent("$>");
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(ContextReentrantTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ContextReentrantTestFrameEvent exit_event = new ContextReentrantTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ContextReentrantTestFrameEvent enter_event = new ContextReentrantTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    ContextReentrantTestFrameEvent enter_event = new ContextReentrantTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ContextReentrantTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(ContextReentrantTestCompartment next) {
        __next_compartment = next;
    }

    public String outer(int x) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("x", x);
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("outer", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String inner(int y) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("y", y);
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("inner", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String deeply_nested(int z) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("z", z);
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("deeply_nested", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_both(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        ContextReentrantTestFrameEvent __e = new ContextReentrantTestFrameEvent("get_both", __params);
        ContextReentrantTestFrameContext __ctx = new ContextReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Ready(ContextReentrantTestFrameEvent __e) {
        if (__e._message.equals("deeply_nested")) {
            var z = (int) __e._parameters.get("z");
            // 3 levels deep
            String outer_result = this.outer(_context_stack.get(_context_stack.size() - 1)._event._parameters.get("z"));
            _context_stack.get(_context_stack.size() - 1)._return = "deep:" + _context_stack.get(_context_stack.size() - 1)._event._parameters.get("z") + "," + outer_result;
        } else if (__e._message.equals("get_both")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            // Test that we can access multiple params
            String result_a = this.inner(_context_stack.get(_context_stack.size() - 1)._event._parameters.get("a"));
            String result_b = this.inner(_context_stack.get(_context_stack.size() - 1)._event._parameters.get("b"));
            // After both inner calls, @@.a and @@.b should still be our params
            _context_stack.get(_context_stack.size() - 1)._return = "a=" + _context_stack.get(_context_stack.size() - 1)._event._parameters.get("a") + ",b=" + _context_stack.get(_context_stack.size() - 1)._event._parameters.get("b") + ",results=" + result_a + "+" + result_b;
        } else if (__e._message.equals("inner")) {
            var y = (int) __e._parameters.get("y");
            // Inner has its own context
            // @@.y should be inner's param, not outer's
            _context_stack.get(_context_stack.size() - 1)._return = String.valueOf(_context_stack.get(_context_stack.size() - 1)._event._parameters.get("y"));
        } else if (__e._message.equals("outer")) {
            var x = (int) __e._parameters.get("x");
            // Set our return before calling inner
            _context_stack.get(_context_stack.size() - 1)._return = "outer_initial";

            // Call inner - should NOT clobber our return
            String inner_result = this.inner(_context_stack.get(_context_stack.size() - 1)._event._parameters.get("x") * 10);

            // Our return should still be accessible
            // Update it with combined result
            _context_stack.get(_context_stack.size() - 1)._return = "outer:" + _context_stack.get(_context_stack.size() - 1)._event._parameters.get("x") + ",inner:" + inner_result;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 37: Context Reentrant ===");
        var s = new ContextReentrantTest();

        // Test 1: Simple nesting - outer calls inner
        String result = s.outer(5);
        String expected = "outer:5,inner:50";
        if (!result.equals(expected)) {
            System.out.println("FAIL: Expected '" + expected + "', got '" + result + "'");
            System.exit(1);
        }
        System.out.println("1. outer(5) = '" + result + "'");

        // Test 2: Inner alone
        result = s.inner(42);
        if (!result.equals("42")) {
            System.out.println("FAIL: Expected '42', got '" + result + "'");
            System.exit(1);
        }
        System.out.println("2. inner(42) = '" + result + "'");

        // Test 3: Deep nesting (3 levels)
        result = s.deeply_nested(3);
        expected = "deep:3,outer:3,inner:30";
        if (!result.equals(expected)) {
            System.out.println("FAIL: Expected '" + expected + "', got '" + result + "'");
            System.exit(1);
        }
        System.out.println("3. deeply_nested(3) = '" + result + "'");

        // Test 4: Multiple inner calls, params preserved
        result = s.get_both(10, 20);
        expected = "a=10,b=20,results=10+20";
        if (!result.equals(expected)) {
            System.out.println("FAIL: Expected '" + expected + "', got '" + result + "'");
            System.exit(1);
        }
        System.out.println("4. get_both(10, 20) = '" + result + "'");

        System.out.println("PASS: Context reentrant works correctly");
    }
}
