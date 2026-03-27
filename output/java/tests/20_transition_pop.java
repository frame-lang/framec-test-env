import java.util.*;


import java.util.*;

class TransitionPopTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    TransitionPopTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    TransitionPopTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TransitionPopTestFrameContext {
    TransitionPopTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    TransitionPopTestFrameContext(TransitionPopTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class TransitionPopTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    TransitionPopTestFrameEvent forward_event;
    TransitionPopTestCompartment parent_compartment;

    TransitionPopTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    TransitionPopTestCompartment copy() {
        TransitionPopTestCompartment c = new TransitionPopTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TransitionPopTest {
    private ArrayList<TransitionPopTestCompartment> _state_stack;
    private TransitionPopTestCompartment __compartment;
    private TransitionPopTestCompartment __next_compartment;
    private ArrayList<TransitionPopTestFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public TransitionPopTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new TransitionPopTestCompartment("Idle");
        __next_compartment = null;
        TransitionPopTestFrameEvent __frame_event = new TransitionPopTestFrameEvent("$>");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(TransitionPopTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TransitionPopTestFrameEvent exit_event = new TransitionPopTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TransitionPopTestFrameEvent enter_event = new TransitionPopTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    TransitionPopTestFrameEvent enter_event = new TransitionPopTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TransitionPopTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Working")) {
            _state_Working(__e);
        }
    }

    private void __transition(TransitionPopTestCompartment next) {
        __next_compartment = next;
    }

    public void start() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("start");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void process() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("process");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("get_state");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public ArrayList get_log() {
        TransitionPopTestFrameEvent __e = new TransitionPopTestFrameEvent("get_log");
        TransitionPopTestFrameContext __ctx = new TransitionPopTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Idle(TransitionPopTestFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Idle";
            return;
        } else if (__e._message.equals("process")) {
            this.log.add("idle:process");
        } else if (__e._message.equals("start")) {
            this.log.add("idle:start:push");
            _state_stack.add(__compartment.copy());
            var __compartment = new TransitionPopTestCompartment("Working");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Working(TransitionPopTestFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Working";
            return;
        } else if (__e._message.equals("process")) {
            this.log.add("working:process:before_pop");
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
            // This should NOT execute because pop transitions away
            this.log.add("working:process:after_pop");
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 20: Transition Pop (Java) ===");
        var s = new TransitionPopTest();

        // Initial state should be Idle
        if (!s.get_state().equals("Idle")) {
            System.out.println("FAIL: Expected 'Idle', got '" + s.get_state() + "'");
            System.exit(1);
        }
        System.out.println("Initial state: " + s.get_state());

        // start() pushes Idle, transitions to Working
        s.start();
        if (!s.get_state().equals("Working")) {
            System.out.println("FAIL: Expected 'Working', got '" + s.get_state() + "'");
            System.exit(1);
        }
        System.out.println("After start(): " + s.get_state());

        // process() in Working does pop transition back to Idle
        s.process();
        if (!s.get_state().equals("Idle")) {
            System.out.println("FAIL: Expected 'Idle' after pop, got '" + s.get_state() + "'");
            System.exit(1);
        }
        System.out.println("After process() with pop: " + s.get_state());

        ArrayList log = s.get_log();
        System.out.println("Log: " + log);

        // Verify log contents
        if (!log.contains("idle:start:push")) {
            System.out.println("FAIL: Expected 'idle:start:push' in log");
            System.exit(1);
        }
        if (!log.contains("working:process:before_pop")) {
            System.out.println("FAIL: Expected 'working:process:before_pop' in log");
            System.exit(1);
        }
        if (log.contains("working:process:after_pop")) {
            System.out.println("FAIL: Should NOT have 'working:process:after_pop' in log");
            System.exit(1);
        }

        System.out.println("PASS: Transition pop works correctly");
    }
}
