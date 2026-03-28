import java.util.*;


import java.util.*;

class HSMForwardFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMForwardFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMForwardFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMForwardFrameContext {
    HSMForwardFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMForwardFrameContext(HSMForwardFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMForwardCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMForwardFrameEvent forward_event;
    HSMForwardCompartment parent_compartment;

    HSMForwardCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMForwardCompartment copy() {
        HSMForwardCompartment c = new HSMForwardCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMForward {
    private ArrayList<HSMForwardCompartment> _state_stack;
    private HSMForwardCompartment __compartment;
    private HSMForwardCompartment __next_compartment;
    private ArrayList<HSMForwardFrameContext> _context_stack;
    public ArrayList<String> log = new ArrayList<>();

    public HSMForward() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMForwardCompartment("Parent");
        this.__compartment = new HSMForwardCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMForwardFrameEvent __frame_event = new HSMForwardFrameEvent("$>");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMForwardFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMForwardFrameEvent exit_event = new HSMForwardFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMForwardFrameEvent enter_event = new HSMForwardFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMForwardFrameEvent enter_event = new HSMForwardFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMForwardFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMForwardCompartment next) {
        __next_compartment = next;
    }

    public void event_a() {
        HSMForwardFrameEvent __e = new HSMForwardFrameEvent("event_a");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void event_b() {
        HSMForwardFrameEvent __e = new HSMForwardFrameEvent("event_b");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList<String> get_log() {
        HSMForwardFrameEvent __e = new HSMForwardFrameEvent("get_log");
        HSMForwardFrameContext __ctx = new HSMForwardFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList<String>) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMForwardFrameEvent __e) {
        if (__e._message.equals("event_a")) {
            this.log.add("Parent:event_a");
        } else if (__e._message.equals("event_b")) {
            this.log.add("Parent:event_b");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        }
    }

    private void _state_Child(HSMForwardFrameEvent __e) {
        if (__e._message.equals("event_a")) {
            this.log.add("Child:event_a");
        } else if (__e._message.equals("event_b")) {
            this.log.add("Child:event_b_forward");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        }
    }
}

class Main {
    @SuppressWarnings("unchecked")
    public static void main(String[] args) {
        System.out.println("=== Test 08: HSM Forward ===");
        var s = new HSMForward();

        // event_a should be handled by Child (no forward)
        s.event_a();
        ArrayList<String> log = (ArrayList<String>) s.get_log();
        if (!log.contains("Child:event_a")) {
            throw new RuntimeException("Expected 'Child:event_a' in log, got " + log);
        }
        System.out.println("After event_a: " + log);

        // event_b should forward to Parent
        s.event_b();
        log = (ArrayList<String>) s.get_log();
        if (!log.contains("Child:event_b_forward")) {
            throw new RuntimeException("Expected 'Child:event_b_forward' in log, got " + log);
        }
        if (!log.contains("Parent:event_b")) {
            throw new RuntimeException("Expected 'Parent:event_b' in log (forwarded), got " + log);
        }
        System.out.println("After event_b (forwarded): " + log);

        System.out.println("PASS: HSM forward works correctly");
    }
}
