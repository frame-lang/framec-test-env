import java.util.*;


import java.util.*;

class CalculatorFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    CalculatorFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    CalculatorFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class CalculatorFrameContext {
    CalculatorFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    CalculatorFrameContext(CalculatorFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class CalculatorCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    CalculatorFrameEvent forward_event;
    CalculatorCompartment parent_compartment;

    CalculatorCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    CalculatorCompartment copy() {
        CalculatorCompartment c = new CalculatorCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class Calculator {
    private ArrayList<CalculatorCompartment> _state_stack;
    private CalculatorCompartment __compartment;
    private CalculatorCompartment __next_compartment;
    private ArrayList<CalculatorFrameContext> _context_stack;
    public int result = 0;

    public Calculator() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new CalculatorCompartment("Ready");
        __next_compartment = null;
        CalculatorFrameEvent __frame_event = new CalculatorFrameEvent("$>");
        CalculatorFrameContext __ctx = new CalculatorFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(CalculatorFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            CalculatorFrameEvent exit_event = new CalculatorFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                CalculatorFrameEvent enter_event = new CalculatorFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    CalculatorFrameEvent enter_event = new CalculatorFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(CalculatorFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(CalculatorCompartment next) {
        __next_compartment = next;
    }

    public int add(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        CalculatorFrameEvent __e = new CalculatorFrameEvent("add", __params);
        CalculatorFrameContext __ctx = new CalculatorFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_result() {
        CalculatorFrameEvent __e = new CalculatorFrameEvent("get_result");
        CalculatorFrameContext __ctx = new CalculatorFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Ready(CalculatorFrameEvent __e) {
        if (__e._message.equals("add")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            this.result = a + b;
            _context_stack.get(_context_stack.size() - 1)._return = this.result;
            return;
        } else if (__e._message.equals("get_result")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.result;
            return;
        }
    }
}

class CounterFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    CounterFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    CounterFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class CounterFrameContext {
    CounterFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    CounterFrameContext(CounterFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class CounterCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    CounterFrameEvent forward_event;
    CounterCompartment parent_compartment;

    CounterCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    CounterCompartment copy() {
        CounterCompartment c = new CounterCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class Counter {
    private ArrayList<CounterCompartment> _state_stack;
    private CounterCompartment __compartment;
    private CounterCompartment __next_compartment;
    private ArrayList<CounterFrameContext> _context_stack;
    public int count = 0;

    public Counter() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new CounterCompartment("Active");
        __next_compartment = null;
        CounterFrameEvent __frame_event = new CounterFrameEvent("$>");
        CounterFrameContext __ctx = new CounterFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(CounterFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            CounterFrameEvent exit_event = new CounterFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                CounterFrameEvent enter_event = new CounterFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    CounterFrameEvent enter_event = new CounterFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(CounterFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Active")) {
            _state_Active(__e);
        }
    }

    private void __transition(CounterCompartment next) {
        __next_compartment = next;
    }

    public void increment() {
        CounterFrameEvent __e = new CounterFrameEvent("increment");
        CounterFrameContext __ctx = new CounterFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (void) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_count() {
        CounterFrameEvent __e = new CounterFrameEvent("get_count");
        CounterFrameContext __ctx = new CounterFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Active(CounterFrameEvent __e) {
        if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.count;
            return;
        } else if (__e._message.equals("increment")) {
            this.count = this.count + 1;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 39: Tagged System Instantiation ===");

        // Tagged instantiation - validated at transpile time
        var calc = new Calculator();
        var counter = new Counter();

        // Test Calculator
        int result = calc.add(3, 4);
        if (result != 7) {
            System.out.println("FAIL: Expected 7, got " + result);
            System.exit(1);
        }
        System.out.println("Calculator.add(3, 4) = " + result);

        result = calc.get_result();
        if (result != 7) {
            System.out.println("FAIL: Expected 7, got " + result);
            System.exit(1);
        }
        System.out.println("Calculator.get_result() = " + result);

        // Test Counter
        counter.increment();
        counter.increment();
        counter.increment();
        int count = counter.get_count();
        if (count != 3) {
            System.out.println("FAIL: Expected 3, got " + count);
            System.exit(1);
        }
        System.out.println("Counter after 3 increments: " + count);

        System.out.println("PASS: Tagged instantiation works correctly");
    }
}
