import java.util.*;


import java.util.*;

class WithParamsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    WithParamsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    WithParamsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class WithParamsFrameContext {
    WithParamsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    WithParamsFrameContext(WithParamsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class WithParamsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    WithParamsFrameEvent forward_event;
    WithParamsCompartment parent_compartment;

    WithParamsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    WithParamsCompartment copy() {
        WithParamsCompartment c = new WithParamsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class WithParams {
    private ArrayList<WithParamsCompartment> _state_stack;
    private WithParamsCompartment __compartment;
    private WithParamsCompartment __next_compartment;
    private ArrayList<WithParamsFrameContext> _context_stack;
    public int total = 0;

    public WithParams() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new WithParamsCompartment("Idle");
        __next_compartment = null;
        WithParamsFrameEvent __frame_event = new WithParamsFrameEvent("$>");
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(WithParamsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            WithParamsFrameEvent exit_event = new WithParamsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                WithParamsFrameEvent enter_event = new WithParamsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    WithParamsFrameEvent enter_event = new WithParamsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(WithParamsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Running")) {
            _state_Running(__e);
        }
    }

    private void __transition(WithParamsCompartment next) {
        __next_compartment = next;
    }

    public void start(int initial) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("initial", initial);
        WithParamsFrameEvent __e = new WithParamsFrameEvent("start", __params);
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void add(int value) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("value", value);
        WithParamsFrameEvent __e = new WithParamsFrameEvent("add", __params);
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public int multiply(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        WithParamsFrameEvent __e = new WithParamsFrameEvent("multiply", __params);
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_total() {
        WithParamsFrameEvent __e = new WithParamsFrameEvent("get_total");
        WithParamsFrameContext __ctx = new WithParamsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Running(WithParamsFrameEvent __e) {
        if (__e._message.equals("add")) {
            var value = (int) __e._parameters.get("value");
            this.total += value;
            System.out.println("Added " + value + ", total is now " + this.total);
        } else if (__e._message.equals("get_total")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.total;
            return;
        } else if (__e._message.equals("multiply")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            int result = a * b;
            this.total += result;
            System.out.println("Multiplied " + a + " * " + b + " = " + result + ", total is now " + this.total);
            _context_stack.get(_context_stack.size() - 1)._return = result;
            return;
        } else if (__e._message.equals("start")) {
            var initial = (int) __e._parameters.get("initial");
            System.out.println("Already running");
        }
    }

    private void _state_Idle(WithParamsFrameEvent __e) {
        if (__e._message.equals("add")) {
            var value = (int) __e._parameters.get("value");
            System.out.println("Cannot add in Idle state");
        } else if (__e._message.equals("get_total")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.total;
            return;
        } else if (__e._message.equals("multiply")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            _context_stack.get(_context_stack.size() - 1)._return = 0;
            return;
        } else if (__e._message.equals("start")) {
            var initial = (int) __e._parameters.get("initial");
            this.total = initial;
            System.out.println("Started with initial value: " + initial);
            var __compartment = new WithParamsCompartment("Running");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 07: Handler Parameters ===");
        var s = new WithParams();

        // Initial total should be 0
        int total = (int) s.get_total();
        if (total != 0) {
            throw new RuntimeException("Expected initial total=0, got " + total);
        }

        // Start with initial value
        s.start(100);
        total = (int) s.get_total();
        if (total != 100) {
            throw new RuntimeException("Expected total=100, got " + total);
        }
        System.out.println("After start(100): total = " + total);

        // Add value
        s.add(25);
        total = (int) s.get_total();
        if (total != 125) {
            throw new RuntimeException("Expected total=125, got " + total);
        }
        System.out.println("After add(25): total = " + total);

        // Multiply with two params
        int result = (int) s.multiply(3, 5);
        if (result != 15) {
            throw new RuntimeException("Expected multiply result=15, got " + result);
        }
        total = (int) s.get_total();
        if (total != 140) {
            throw new RuntimeException("Expected total=140, got " + total);
        }
        System.out.println("After multiply(3,5): result = " + result + ", total = " + total);

        System.out.println("PASS: Handler parameters work correctly");
    }
}
