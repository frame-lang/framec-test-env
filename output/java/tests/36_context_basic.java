import java.util.*;


import java.util.*;

class ContextBasicTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    ContextBasicTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    ContextBasicTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ContextBasicTestFrameContext {
    ContextBasicTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    ContextBasicTestFrameContext(ContextBasicTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class ContextBasicTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    ContextBasicTestFrameEvent forward_event;
    ContextBasicTestCompartment parent_compartment;

    ContextBasicTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    ContextBasicTestCompartment copy() {
        ContextBasicTestCompartment c = new ContextBasicTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ContextBasicTest {
    private ArrayList<ContextBasicTestCompartment> _state_stack;
    private ContextBasicTestCompartment __compartment;
    private ContextBasicTestCompartment __next_compartment;
    private ArrayList<ContextBasicTestFrameContext> _context_stack;

    public ContextBasicTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new ContextBasicTestCompartment("Ready");
        __next_compartment = null;
        ContextBasicTestFrameEvent __frame_event = new ContextBasicTestFrameEvent("$>");
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(ContextBasicTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ContextBasicTestFrameEvent exit_event = new ContextBasicTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ContextBasicTestFrameEvent enter_event = new ContextBasicTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    ContextBasicTestFrameEvent enter_event = new ContextBasicTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ContextBasicTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(ContextBasicTestCompartment next) {
        __next_compartment = next;
    }

    public int add(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        ContextBasicTestFrameEvent __e = new ContextBasicTestFrameEvent("add", __params);
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_event_name() {
        ContextBasicTestFrameEvent __e = new ContextBasicTestFrameEvent("get_event_name");
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String greet(String name) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("name", name);
        ContextBasicTestFrameEvent __e = new ContextBasicTestFrameEvent("greet", __params);
        ContextBasicTestFrameContext __ctx = new ContextBasicTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Ready(ContextBasicTestFrameEvent __e) {
        if (__e._message.equals("add")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            // Access params via @@ shorthand
            _context_stack.get(_context_stack.size() - 1)._return = a + b;
        } else if (__e._message.equals("get_event_name")) {
            // Access event name
            _context_stack.get(_context_stack.size() - 1)._return = _context_stack.get(_context_stack.size() - 1)._event._message;
        } else if (__e._message.equals("greet")) {
            var name = (String) __e._parameters.get("name");
            // Mix param access and return
            String result = "Hello, " + name + "!";
            _context_stack.get(_context_stack.size() - 1)._return = result;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 36: Context Basic ===");
        var s = new ContextBasicTest();

        // Test 1: @@.a and @@.b param access, @@:return
        int result1 = s.add(3, 5);
        if (result1 != 8) {
            System.out.println("FAIL: Expected 8, got " + result1);
            System.exit(1);
        }
        System.out.println("1. add(3, 5) = " + result1);

        // Test 2: @@:event access
        String eventName = s.get_event_name();
        if (!eventName.equals("get_event_name")) {
            System.out.println("FAIL: Expected 'get_event_name', got '" + eventName + "'");
            System.exit(1);
        }
        System.out.println("2. @@:event = '" + eventName + "'");

        // Test 3: @@.name param access with string
        String greeting = s.greet("World");
        if (!greeting.equals("Hello, World!")) {
            System.out.println("FAIL: Expected 'Hello, World!', got '" + greeting + "'");
            System.exit(1);
        }
        System.out.println("3. greet('World') = '" + greeting + "'");

        System.out.println("PASS: Context basic access works correctly");
    }
}
