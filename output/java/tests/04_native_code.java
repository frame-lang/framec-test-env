import java.util.*;


import java.util.*;

class Helper {
    static int helper_function(int x) {
        // Native helper function defined before system
        return x * 2;
    }
}

class NativeCodeFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    NativeCodeFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    NativeCodeFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class NativeCodeFrameContext {
    NativeCodeFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    NativeCodeFrameContext(NativeCodeFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class NativeCodeCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    NativeCodeFrameEvent forward_event;
    NativeCodeCompartment parent_compartment;

    NativeCodeCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    NativeCodeCompartment copy() {
        NativeCodeCompartment c = new NativeCodeCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class NativeCode {
    private ArrayList<NativeCodeCompartment> _state_stack;
    private NativeCodeCompartment __compartment;
    private NativeCodeCompartment __next_compartment;
    private ArrayList<NativeCodeFrameContext> _context_stack;

    public NativeCode() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new NativeCodeCompartment("Active");
        __next_compartment = null;
        NativeCodeFrameEvent __frame_event = new NativeCodeFrameEvent("$>");
        NativeCodeFrameContext __ctx = new NativeCodeFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(NativeCodeFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            NativeCodeFrameEvent exit_event = new NativeCodeFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                NativeCodeFrameEvent enter_event = new NativeCodeFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    NativeCodeFrameEvent enter_event = new NativeCodeFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(NativeCodeFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Active")) {
            _state_Active(__e);
        }
    }

    private void __transition(NativeCodeCompartment next) {
        __next_compartment = next;
    }

    public int compute(int value) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("value", value);
        NativeCodeFrameEvent __e = new NativeCodeFrameEvent("compute", __params);
        NativeCodeFrameContext __ctx = new NativeCodeFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public double use_math() {
        NativeCodeFrameEvent __e = new NativeCodeFrameEvent("use_math");
        NativeCodeFrameContext __ctx = new NativeCodeFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (double) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Active(NativeCodeFrameEvent __e) {
        if (__e._message.equals("compute")) {
            var value = (int) __e._parameters.get("value");
            // Native code with local variables
            int temp = value + 10;
            int result = Helper.helper_function(temp);
            System.out.println("Computed: " + value + " -> " + result);
            _context_stack.get(_context_stack.size() - 1)._return = result;
            return;
        } else if (__e._message.equals("use_math")) {
            // Using Math module
            double result = Math.sqrt(16) + Math.PI;
            System.out.println("Math result: " + result);
            _context_stack.get(_context_stack.size() - 1)._return = result;
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 04: Native Code Preservation ===");
        var s = new NativeCode();

        // Test native code in handler with helper function
        int result = (int) s.compute(5);
        int expected = (5 + 10) * 2;  // 30
        if (result != expected) {
            throw new RuntimeException("Expected " + expected + ", got " + result);
        }
        System.out.println("compute(5) = " + result);

        // Test Math module usage
        double mathResult = (double) s.use_math();
        double expectedMath = Math.sqrt(16) + Math.PI;
        if (Math.abs(mathResult - expectedMath) >= 0.001) {
            throw new RuntimeException("Expected ~" + expectedMath + ", got " + mathResult);
        }
        System.out.println("use_math() = " + mathResult);

        System.out.println("PASS: Native code preservation works correctly");
    }
}
