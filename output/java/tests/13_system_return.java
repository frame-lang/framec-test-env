import java.util.*;


import java.util.*;

class SystemReturnTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SystemReturnTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SystemReturnTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnTestFrameContext {
    SystemReturnTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SystemReturnTestFrameContext(SystemReturnTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SystemReturnTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SystemReturnTestFrameEvent forward_event;
    SystemReturnTestCompartment parent_compartment;

    SystemReturnTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SystemReturnTestCompartment copy() {
        SystemReturnTestCompartment c = new SystemReturnTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnTest {
    private ArrayList<SystemReturnTestCompartment> _state_stack;
    private SystemReturnTestCompartment __compartment;
    private SystemReturnTestCompartment __next_compartment;
    private ArrayList<SystemReturnTestFrameContext> _context_stack;

    public SystemReturnTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SystemReturnTestCompartment("Calculator");
        __next_compartment = null;
        SystemReturnTestFrameEvent __frame_event = new SystemReturnTestFrameEvent("$>");
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SystemReturnTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnTestFrameEvent exit_event = new SystemReturnTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnTestFrameEvent enter_event = new SystemReturnTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SystemReturnTestFrameEvent enter_event = new SystemReturnTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Calculator")) {
            _state_Calculator(__e);
        }
    }

    private void __transition(SystemReturnTestCompartment next) {
        __next_compartment = next;
    }

    public int add(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("add", __params);
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int multiply(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("multiply", __params);
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String greet(String name) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("name", name);
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("greet", __params);
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_value() {
        SystemReturnTestFrameEvent __e = new SystemReturnTestFrameEvent("get_value");
        SystemReturnTestFrameContext __ctx = new SystemReturnTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Calculator(SystemReturnTestFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Calculator")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("value")) {
                __sv_comp.state_vars.put("value", 0);
            }
        } else if (__e._message.equals("add")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            _context_stack.get(_context_stack.size() - 1)._return = a + b;
            return;
        } else if (__e._message.equals("get_value")) {
            __sv_comp.state_vars.put("value", 42);
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("value");
            return;
        } else if (__e._message.equals("greet")) {
            var name = (String) __e._parameters.get("name");
            _context_stack.get(_context_stack.size() - 1)._return = "Hello, " + name + "!";
            return;
        } else if (__e._message.equals("multiply")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            _context_stack.get(_context_stack.size() - 1)._return = a * b;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 13: System Return ===");
        var calc = new SystemReturnTest();

        // Test return sugar
        int result = (int) calc.add(3, 5);
        if (result != 8) {
            throw new RuntimeException("Expected 8, got " + result);
        }
        System.out.println("add(3, 5) = " + result);

        // Test @@:return = expr
        result = (int) calc.multiply(4, 7);
        if (result != 28) {
            throw new RuntimeException("Expected 28, got " + result);
        }
        System.out.println("multiply(4, 7) = " + result);

        // Test string return
        String greeting = (String) calc.greet("World");
        if (!"Hello, World!".equals(greeting)) {
            throw new RuntimeException("Expected 'Hello, World!', got '" + greeting + "'");
        }
        System.out.println("greet('World') = " + greeting);

        // Test return with state variable
        int value = (int) calc.get_value();
        if (value != 42) {
            throw new RuntimeException("Expected 42, got " + value);
        }
        System.out.println("get_value() = " + value);

        System.out.println("PASS: System return works correctly");
    }
}
