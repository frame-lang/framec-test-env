import java.util.*;


import java.util.*;

class SystemReturnReentrantTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SystemReturnReentrantTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SystemReturnReentrantTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnReentrantTestFrameContext {
    SystemReturnReentrantTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SystemReturnReentrantTestFrameContext(SystemReturnReentrantTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SystemReturnReentrantTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SystemReturnReentrantTestFrameEvent forward_event;
    SystemReturnReentrantTestCompartment parent_compartment;

    SystemReturnReentrantTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SystemReturnReentrantTestCompartment copy() {
        SystemReturnReentrantTestCompartment c = new SystemReturnReentrantTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnReentrantTest {
    private ArrayList<SystemReturnReentrantTestCompartment> _state_stack;
    private SystemReturnReentrantTestCompartment __compartment;
    private SystemReturnReentrantTestCompartment __next_compartment;
    private ArrayList<SystemReturnReentrantTestFrameContext> _context_stack;

    public SystemReturnReentrantTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SystemReturnReentrantTestCompartment("Start");
        __next_compartment = null;
        SystemReturnReentrantTestFrameEvent __frame_event = new SystemReturnReentrantTestFrameEvent("$>");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SystemReturnReentrantTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnReentrantTestFrameEvent exit_event = new SystemReturnReentrantTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnReentrantTestFrameEvent enter_event = new SystemReturnReentrantTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SystemReturnReentrantTestFrameEvent enter_event = new SystemReturnReentrantTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnReentrantTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        }
    }

    private void __transition(SystemReturnReentrantTestCompartment next) {
        __next_compartment = next;
    }

    public String outer_call() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("outer_call");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String inner_call() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("inner_call");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String nested_call() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("nested_call");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_log() {
        SystemReturnReentrantTestFrameEvent __e = new SystemReturnReentrantTestFrameEvent("get_log");
        SystemReturnReentrantTestFrameContext __ctx = new SystemReturnReentrantTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Start(SystemReturnReentrantTestFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Start")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("log")) {
                __sv_comp.state_vars.put("log", "");
            }
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = (String) __sv_comp.state_vars.get("log");
            return;
        } else if (__e._message.equals("inner_call")) {
            __sv_comp.state_vars.put("log", (String) __sv_comp.state_vars.get("log") + "inner,");
            _context_stack.get(_context_stack.size() - 1)._return = "inner_result";
            return;
        } else if (__e._message.equals("nested_call")) {
            __sv_comp.state_vars.put("log", (String) __sv_comp.state_vars.get("log") + "nested_start,");
            // Two levels of nesting
            String result1 = this.inner_call();
            String result2 = this.outer_call();
            __sv_comp.state_vars.put("log", (String) __sv_comp.state_vars.get("log") + "nested_end,");
            _context_stack.get(_context_stack.size() - 1)._return = "nested:" + result1 + "+" + result2;
            return;
        } else if (__e._message.equals("outer_call")) {
            __sv_comp.state_vars.put("log", (String) __sv_comp.state_vars.get("log") + "outer_start,");
            // Call inner method - this creates nested return context
            String inner_result = this.inner_call();
            __sv_comp.state_vars.put("log", (String) __sv_comp.state_vars.get("log") + "outer_after_inner,");
            // Our return should be independent of inner's return
            _context_stack.get(_context_stack.size() - 1)._return = "outer_result:" + inner_result;
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 16: System Return Reentrant (Nested Calls) ===");

        // Test 1: Simple inner call
        var s1 = new SystemReturnReentrantTest();
        String result1 = s1.inner_call();
        if (!result1.equals("inner_result")) {
            System.out.println("FAIL: Expected 'inner_result', got '" + result1 + "'");
            System.exit(1);
        }
        System.out.println("1. inner_call() = '" + result1 + "'");

        // Test 2: Outer calls inner - return contexts should be separate
        var s2 = new SystemReturnReentrantTest();
        String result2 = s2.outer_call();
        if (!result2.equals("outer_result:inner_result")) {
            System.out.println("FAIL: Expected 'outer_result:inner_result', got '" + result2 + "'");
            System.exit(1);
        }
        String log2 = s2.get_log();
        if (!log2.contains("outer_start")) {
            System.out.println("FAIL: Missing outer_start in log: " + log2);
            System.exit(1);
        }
        if (!log2.contains("inner")) {
            System.out.println("FAIL: Missing inner in log: " + log2);
            System.exit(1);
        }
        if (!log2.contains("outer_after_inner")) {
            System.out.println("FAIL: Missing outer_after_inner in log: " + log2);
            System.exit(1);
        }
        System.out.println("2. outer_call() = '" + result2 + "'");
        System.out.println("   Log: '" + log2 + "'");

        // Test 3: Deeply nested calls
        var s3 = new SystemReturnReentrantTest();
        String result3 = s3.nested_call();
        String expected = "nested:inner_result+outer_result:inner_result";
        if (!result3.equals(expected)) {
            System.out.println("FAIL: Expected '" + expected + "', got '" + result3 + "'");
            System.exit(1);
        }
        System.out.println("3. nested_call() = '" + result3 + "'");

        System.out.println("PASS: System return reentrant (nested calls) works correctly");
    }
}
