import java.util.*;


import java.util.*;

class ContextDataTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    ContextDataTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    ContextDataTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ContextDataTestFrameContext {
    ContextDataTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    ContextDataTestFrameContext(ContextDataTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class ContextDataTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    ContextDataTestFrameEvent forward_event;
    ContextDataTestCompartment parent_compartment;

    ContextDataTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    ContextDataTestCompartment copy() {
        ContextDataTestCompartment c = new ContextDataTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ContextDataTest {
    private ArrayList<ContextDataTestCompartment> _state_stack;
    private ContextDataTestCompartment __compartment;
    private ContextDataTestCompartment __next_compartment;
    private ArrayList<ContextDataTestFrameContext> _context_stack;

    public ContextDataTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new ContextDataTestCompartment("Start");
        __next_compartment = null;
        ContextDataTestFrameEvent __frame_event = new ContextDataTestFrameEvent("$>");
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(ContextDataTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ContextDataTestFrameEvent exit_event = new ContextDataTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ContextDataTestFrameEvent enter_event = new ContextDataTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    ContextDataTestFrameEvent enter_event = new ContextDataTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ContextDataTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("End")) {
            _state_End(__e);
        }
    }

    private void __transition(ContextDataTestCompartment next) {
        __next_compartment = next;
    }

    public String process_with_data(int value) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("value", value);
        ContextDataTestFrameEvent __e = new ContextDataTestFrameEvent("process_with_data", __params);
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String check_data_isolation() {
        ContextDataTestFrameEvent __e = new ContextDataTestFrameEvent("check_data_isolation");
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String transition_preserves_data(int x) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("x", x);
        ContextDataTestFrameEvent __e = new ContextDataTestFrameEvent("transition_preserves_data", __params);
        ContextDataTestFrameContext __ctx = new ContextDataTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_End(ContextDataTestFrameEvent __e) {
        if (__e._message.equals("$>")) {
            // Enter handler can access data set by previous handlers
            ((ArrayList)_context_stack.get(_context_stack.size() - 1)._data.get("trace")).add("enter");
            _context_stack.get(_context_stack.size() - 1)._data.put("ended_in", "End");

            // Build final result from accumulated data
            ArrayList trace = (ArrayList)_context_stack.get(_context_stack.size() - 1)._data.get("trace");
            String trace_str = trace != null ? String.join(",", trace) : "no_trace";
            _context_stack.get(_context_stack.size() - 1)._return = "from=" + _context_stack.get(_context_stack.size() - 1)._data.get("started_in") + ",to=" + _context_stack.get(_context_stack.size() - 1)._data.get("ended_in") + ",value=" + _context_stack.get(_context_stack.size() - 1)._data.get("value") + ",trace=" + trace_str;
        }
    }

    private void _state_Start(ContextDataTestFrameEvent __e) {
        if (__e._message.equals("<$")) {
            // Exit handler can access data set by event handler
            ((ArrayList)_context_stack.get(_context_stack.size() - 1)._data.get("trace")).add("exit");
        } else if (__e._message.equals("check_data_isolation")) {
            // Set data, call another method, verify our data preserved
            _context_stack.get(_context_stack.size() - 1)._data.put("outer", "outer_value");

            // This creates its own context with its own data
            String inner_result = this.process_with_data(99);

            // Our data should still be here
            _context_stack.get(_context_stack.size() - 1)._return = "outer_data=" + _context_stack.get(_context_stack.size() - 1)._data.get("outer") + ",inner=" + inner_result;
        } else if (__e._message.equals("process_with_data")) {
            var value = (int) __e._parameters.get("value");
            // Set data in handler
            _context_stack.get(_context_stack.size() - 1)._data.put("input", value);
            _context_stack.get(_context_stack.size() - 1)._data.put("trace", new ArrayList(Arrays.asList("handler")));

            _context_stack.get(_context_stack.size() - 1)._return = "processed:" + _context_stack.get(_context_stack.size() - 1)._data.get("input");
        } else if (__e._message.equals("transition_preserves_data")) {
            var x = (int) __e._parameters.get("x");
            // Set data, transition, verify data available in lifecycle handlers
            _context_stack.get(_context_stack.size() - 1)._data.put("started_in", "Start");
            _context_stack.get(_context_stack.size() - 1)._data.put("value", x);
            _context_stack.get(_context_stack.size() - 1)._data.put("trace", new ArrayList(Arrays.asList("handler")));
            var __compartment = new ContextDataTestCompartment("End");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 38: Context Data ===");

        // Test 1: Basic data set/get
        var s1 = new ContextDataTest();
        String result = s1.process_with_data(42);
        if (!result.equals("processed:42")) {
            System.out.println("FAIL: Expected 'processed:42', got '" + result + "'");
            System.exit(1);
        }
        System.out.println("1. process_with_data(42) = '" + result + "'");

        // Test 2: Data isolation between nested calls
        var s2 = new ContextDataTest();
        result = s2.check_data_isolation();
        String expected = "outer_data=outer_value,inner=processed:99";
        if (!result.equals(expected)) {
            System.out.println("FAIL: Expected '" + expected + "', got '" + result + "'");
            System.exit(1);
        }
        System.out.println("2. check_data_isolation() = '" + result + "'");

        // Test 3: Data preserved across transition (handler -> <$ -> $>)
        var s3 = new ContextDataTest();
        result = s3.transition_preserves_data(100);
        // Data should flow: handler sets -> exit accesses -> enter accesses and returns
        if (!result.contains("from=Start")) {
            System.out.println("FAIL: Expected 'from=Start' in '" + result + "'");
            System.exit(1);
        }
        if (!result.contains("to=End")) {
            System.out.println("FAIL: Expected 'to=End' in '" + result + "'");
            System.exit(1);
        }
        if (!result.contains("value=100")) {
            System.out.println("FAIL: Expected 'value=100' in '" + result + "'");
            System.exit(1);
        }
        System.out.println("3. transition_preserves_data(100) = '" + result + "'");

        System.out.println("PASS: Context data works correctly");
    }
}
