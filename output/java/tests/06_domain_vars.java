import java.util.*;


import java.util.*;

class DomainVarsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    DomainVarsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    DomainVarsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class DomainVarsFrameContext {
    DomainVarsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    DomainVarsFrameContext(DomainVarsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class DomainVarsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    DomainVarsFrameEvent forward_event;
    DomainVarsCompartment parent_compartment;

    DomainVarsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    DomainVarsCompartment copy() {
        DomainVarsCompartment c = new DomainVarsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class DomainVars {
    private ArrayList<DomainVarsCompartment> _state_stack;
    private DomainVarsCompartment __compartment;
    private DomainVarsCompartment __next_compartment;
    private ArrayList<DomainVarsFrameContext> _context_stack;
    public int count = 0;
    public String name = "counter";

    public DomainVars() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new DomainVarsCompartment("Counting");
        __next_compartment = null;
        DomainVarsFrameEvent __frame_event = new DomainVarsFrameEvent("$>");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(DomainVarsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            DomainVarsFrameEvent exit_event = new DomainVarsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                DomainVarsFrameEvent enter_event = new DomainVarsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    DomainVarsFrameEvent enter_event = new DomainVarsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(DomainVarsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Counting")) {
            _state_Counting(__e);
        }
    }

    private void __transition(DomainVarsCompartment next) {
        __next_compartment = next;
    }

    public void increment() {
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("increment");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void decrement() {
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("decrement");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public int get_count() {
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("get_count");
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void set_count(int value) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("value", value);
        DomainVarsFrameEvent __e = new DomainVarsFrameEvent("set_count", __params);
        DomainVarsFrameContext __ctx = new DomainVarsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Counting(DomainVarsFrameEvent __e) {
        if (__e._message.equals("decrement")) {
            this.count -= 1;
            System.out.println(this.name + ": decremented to " + this.count);
        } else if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.count;
            return;
        } else if (__e._message.equals("increment")) {
            this.count += 1;
            System.out.println(this.name + ": incremented to " + this.count);
        } else if (__e._message.equals("set_count")) {
            var value = (int) __e._parameters.get("value");
            this.count = value;
            System.out.println(this.name + ": set to " + this.count);
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 06: Domain Variables ===");
        var s = new DomainVars();

        // Initial value should be 0
        int count = (int) s.get_count();
        if (count != 0) {
            throw new RuntimeException("Expected initial count=0, got " + count);
        }
        System.out.println("Initial count: " + count);

        // Increment
        s.increment();
        count = (int) s.get_count();
        if (count != 1) {
            throw new RuntimeException("Expected count=1, got " + count);
        }

        s.increment();
        count = (int) s.get_count();
        if (count != 2) {
            throw new RuntimeException("Expected count=2, got " + count);
        }

        // Decrement
        s.decrement();
        count = (int) s.get_count();
        if (count != 1) {
            throw new RuntimeException("Expected count=1, got " + count);
        }

        // Set directly
        s.set_count(100);
        count = (int) s.get_count();
        if (count != 100) {
            throw new RuntimeException("Expected count=100, got " + count);
        }

        System.out.println("Final count: " + count);
        System.out.println("PASS: Domain variables work correctly");
    }
}
