import java.util.*;


import java.util.*;

class WithInterfaceFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    WithInterfaceFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    WithInterfaceFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class WithInterfaceFrameContext {
    WithInterfaceFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    WithInterfaceFrameContext(WithInterfaceFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class WithInterfaceCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    WithInterfaceFrameEvent forward_event;
    WithInterfaceCompartment parent_compartment;

    WithInterfaceCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    WithInterfaceCompartment copy() {
        WithInterfaceCompartment c = new WithInterfaceCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class WithInterface {
    private ArrayList<WithInterfaceCompartment> _state_stack;
    private WithInterfaceCompartment __compartment;
    private WithInterfaceCompartment __next_compartment;
    private ArrayList<WithInterfaceFrameContext> _context_stack;
    public int call_count = 0;

    public WithInterface() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new WithInterfaceCompartment("Ready");
        __next_compartment = null;
        WithInterfaceFrameEvent __frame_event = new WithInterfaceFrameEvent("$>");
        WithInterfaceFrameContext __ctx = new WithInterfaceFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(WithInterfaceFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            WithInterfaceFrameEvent exit_event = new WithInterfaceFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                WithInterfaceFrameEvent enter_event = new WithInterfaceFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    WithInterfaceFrameEvent enter_event = new WithInterfaceFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(WithInterfaceFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Ready")) {
            _state_Ready(__e);
        }
    }

    private void __transition(WithInterfaceCompartment next) {
        __next_compartment = next;
    }

    public String greet(String name) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("name", name);
        WithInterfaceFrameEvent __e = new WithInterfaceFrameEvent("greet", __params);
        WithInterfaceFrameContext __ctx = new WithInterfaceFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_count() {
        WithInterfaceFrameEvent __e = new WithInterfaceFrameEvent("get_count");
        WithInterfaceFrameContext __ctx = new WithInterfaceFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Ready(WithInterfaceFrameEvent __e) {
        if (__e._message.equals("get_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.call_count;
            return;
        } else if (__e._message.equals("greet")) {
            var name = (String) __e._parameters.get("name");
            this.call_count += 1;
            _context_stack.get(_context_stack.size() - 1)._return = "Hello, " + name + "!";
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 02: Interface Methods ===");
        var s = new WithInterface();

        // Test interface method with parameter and return
        String result = s.greet("World");
        if (!"Hello, World!".equals(result)) {
            throw new RuntimeException("Expected 'Hello, World!', got '" + result + "'");
        }
        System.out.println("greet('World') = " + result);

        // Test domain variable access through interface
        int count = (int) s.get_count();
        if (count != 1) {
            throw new RuntimeException("Expected count=1, got " + count);
        }
        System.out.println("get_count() = " + count);

        // Call again to verify state
        s.greet("Frame");
        int count2 = (int) s.get_count();
        if (count2 != 2) {
            throw new RuntimeException("Expected count=2, got " + count2);
        }
        System.out.println("After second call: get_count() = " + count2);

        System.out.println("PASS: Interface methods work correctly");
    }
}
