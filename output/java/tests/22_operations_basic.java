import java.util.*;


import java.util.*;

class OperationsTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    OperationsTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    OperationsTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class OperationsTestFrameContext {
    OperationsTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    OperationsTestFrameContext(OperationsTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class OperationsTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    OperationsTestFrameEvent forward_event;
    OperationsTestCompartment parent_compartment;

    OperationsTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    OperationsTestCompartment copy() {
        OperationsTestCompartment c = new OperationsTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class OperationsTest {
    private ArrayList<OperationsTestCompartment> _state_stack;
    private OperationsTestCompartment __compartment;
    private OperationsTestCompartment __next_compartment;
    private ArrayList<OperationsTestFrameContext> _context_stack;
    public int last_result = 0;

    public OperationsTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new OperationsTestCompartment("Ready");
        __next_compartment = null;
        OperationsTestFrameEvent __frame_event = new OperationsTestFrameEvent("$>");
        OperationsTestFrameContext __ctx = new OperationsTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(OperationsTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            OperationsTestFrameEvent exit_event = new OperationsTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                OperationsTestFrameEvent enter_event = new OperationsTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    OperationsTestFrameEvent enter_event = new OperationsTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(OperationsTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(OperationsTestCompartment next) {
        __next_compartment = next;
    }

    public int compute(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        OperationsTestFrameEvent __e = new OperationsTestFrameEvent("compute", __params);
        OperationsTestFrameContext __ctx = new OperationsTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_last_result() {
        OperationsTestFrameEvent __e = new OperationsTestFrameEvent("get_last_result");
        OperationsTestFrameContext __ctx = new OperationsTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Ready(OperationsTestFrameEvent __e) {
        if (__e._message.equals("compute")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            // Use instance operations
            int sum_val = this.add(a, b);
            int prod_val = this.multiply(a, b);
            int last_result = sum_val + prod_val;
            _context_stack.get(_context_stack.size() - 1)._return = last_result;
            return;
        } else if (__e._message.equals("get_last_result")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.last_result;
            return;
        }
    }

    public int add(int x, int y) {
                    return x + y;
    }

    public int multiply(int x, int y) {
                    return x * y;
    }

    public static int factorial(int n) {
                    if (n <= 1) {
                        return 1;
                    }
                    return n * OperationsTest.factorial(n - 1);
    }

    public static boolean is_even(int n) {
                    return n % 2 == 0;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 22: Operations Basic (Java) ===");
        var s = new OperationsTest();

        // Test 1: Instance operations
        int result = s.add(3, 4);
        if (result != 7) {
            System.out.println("FAIL: Expected 7, got " + result);
            System.exit(1);
        }
        System.out.println("1. add(3, 4) = " + result);

        result = s.multiply(3, 4);
        if (result != 12) {
            System.out.println("FAIL: Expected 12, got " + result);
            System.exit(1);
        }
        System.out.println("2. multiply(3, 4) = " + result);

        // Test 2: Operations used in handler
        result = s.compute(3, 4);
        // compute returns add(3,4) + multiply(3,4) = 7 + 12 = 19
        if (result != 19) {
            System.out.println("FAIL: Expected 19, got " + result);
            System.exit(1);
        }
        System.out.println("3. compute(3, 4) = " + result);

        // Test 3: Static operations
        result = OperationsTest.factorial(5);
        if (result != 120) {
            System.out.println("FAIL: Expected 120, got " + result);
            System.exit(1);
        }
        System.out.println("4. factorial(5) = " + result);

        boolean is_even = OperationsTest.is_even(4);
        if (is_even != true) {
            System.out.println("FAIL: Expected true, got " + is_even);
            System.exit(1);
        }
        System.out.println("5. is_even(4) = " + is_even);

        is_even = OperationsTest.is_even(7);
        if (is_even != false) {
            System.out.println("FAIL: Expected false, got " + is_even);
            System.exit(1);
        }
        System.out.println("6. is_even(7) = " + is_even);

        // Test 4: Static via class
        result = OperationsTest.factorial(4);
        if (result != 24) {
            System.out.println("FAIL: Expected 24, got " + result);
            System.exit(1);
        }
        System.out.println("7. OperationsTest.factorial(4) = " + result);

        System.out.println("PASS: Operations basic works correctly");
    }
}
