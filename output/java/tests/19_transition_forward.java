import java.util.*;


import java.util.*;

class EventForwardTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    EventForwardTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    EventForwardTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class EventForwardTestFrameContext {
    EventForwardTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    EventForwardTestFrameContext(EventForwardTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class EventForwardTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    EventForwardTestFrameEvent forward_event;
    EventForwardTestCompartment parent_compartment;

    EventForwardTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    EventForwardTestCompartment copy() {
        EventForwardTestCompartment c = new EventForwardTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class EventForwardTest {
    private ArrayList<EventForwardTestCompartment> _state_stack;
    private EventForwardTestCompartment __compartment;
    private EventForwardTestCompartment __next_compartment;
    private ArrayList<EventForwardTestFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public EventForwardTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new EventForwardTestCompartment("Idle");
        __next_compartment = null;
        EventForwardTestFrameEvent __frame_event = new EventForwardTestFrameEvent("$>");
        EventForwardTestFrameContext __ctx = new EventForwardTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(EventForwardTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            EventForwardTestFrameEvent exit_event = new EventForwardTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                EventForwardTestFrameEvent enter_event = new EventForwardTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    EventForwardTestFrameEvent enter_event = new EventForwardTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(EventForwardTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Working")) {
            _state_Working(__e);
        }
    }

    private void __transition(EventForwardTestCompartment next) {
        __next_compartment = next;
    }

    public void process() {
        EventForwardTestFrameEvent __e = new EventForwardTestFrameEvent("process");
        EventForwardTestFrameContext __ctx = new EventForwardTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        EventForwardTestFrameEvent __e = new EventForwardTestFrameEvent("get_log");
        EventForwardTestFrameContext __ctx = new EventForwardTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Idle(EventForwardTestFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("process")) {
            this.log.add("idle:process:before");
            var __compartment = new EventForwardTestCompartment("Working");
            __compartment.parent_compartment = this.__compartment.copy();
            __compartment.forward_event = __e;
            __transition(__compartment);
            return;
            // This should NOT execute because -> => returns after dispatch
            this.log.add("idle:process:after");
        }
    }

    private void _state_Working(EventForwardTestFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("process")) {
            this.log.add("working:process");
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 19: Transition Forward (Java) ===");
        var s = new EventForwardTest();
        s.process();
        ArrayList log = s.get_log();
        System.out.println("Log: " + log);

        if (!log.contains("idle:process:before")) {
            System.out.println("FAIL: Expected 'idle:process:before' in log: " + log);
            System.exit(1);
        }
        if (!log.contains("working:process")) {
            System.out.println("FAIL: Expected 'working:process' in log: " + log);
            System.exit(1);
        }
        if (log.contains("idle:process:after")) {
            System.out.println("FAIL: Should NOT have 'idle:process:after' in log: " + log);
            System.exit(1);
        }

        System.out.println("PASS: Transition forward works correctly");
    }
}
