import java.util.*;


import java.util.*;

class TransitionEnterArgsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    TransitionEnterArgsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    TransitionEnterArgsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TransitionEnterArgsFrameContext {
    TransitionEnterArgsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    TransitionEnterArgsFrameContext(TransitionEnterArgsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class TransitionEnterArgsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    TransitionEnterArgsFrameEvent forward_event;
    TransitionEnterArgsCompartment parent_compartment;

    TransitionEnterArgsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    TransitionEnterArgsCompartment copy() {
        TransitionEnterArgsCompartment c = new TransitionEnterArgsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TransitionEnterArgs {
    private ArrayList<TransitionEnterArgsCompartment> _state_stack;
    private TransitionEnterArgsCompartment __compartment;
    private TransitionEnterArgsCompartment __next_compartment;
    private ArrayList<TransitionEnterArgsFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public TransitionEnterArgs() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new TransitionEnterArgsCompartment("Idle");
        __next_compartment = null;
        TransitionEnterArgsFrameEvent __frame_event = new TransitionEnterArgsFrameEvent("$>");
        TransitionEnterArgsFrameContext __ctx = new TransitionEnterArgsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(TransitionEnterArgsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TransitionEnterArgsFrameEvent exit_event = new TransitionEnterArgsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TransitionEnterArgsFrameEvent enter_event = new TransitionEnterArgsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    TransitionEnterArgsFrameEvent enter_event = new TransitionEnterArgsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TransitionEnterArgsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Active")) {
            _state_Active(__e);
        }
    }

    private void __transition(TransitionEnterArgsCompartment next) {
        __next_compartment = next;
    }

    public void start() {
        TransitionEnterArgsFrameEvent __e = new TransitionEnterArgsFrameEvent("start");
        TransitionEnterArgsFrameContext __ctx = new TransitionEnterArgsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        TransitionEnterArgsFrameEvent __e = new TransitionEnterArgsFrameEvent("get_log");
        TransitionEnterArgsFrameContext __ctx = new TransitionEnterArgsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Idle(TransitionEnterArgsFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("start")) {
            this.log.add("idle:start");
            var __compartment = new TransitionEnterArgsCompartment("Active");
            __compartment.parent_compartment = this.__compartment.copy();
            __compartment.enter_args.put("0", "from_idle");
            __compartment.enter_args.put("1", 42);
            __transition(__compartment);
            return;
        }
    }

    private void _state_Active(TransitionEnterArgsFrameEvent __e) {
        if (__e._message.equals("$>")) {
            var source = (String) __compartment.enter_args.get("0");
            var value = (int) __compartment.enter_args.get("1");
            this.log.add("active:enter:" + source + ":" + value);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("start")) {
            this.log.add("active:start");
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 17: Transition Enter Args ===");
        var s = new TransitionEnterArgs();

        // Initial state is Idle
        ArrayList log = s.get_log();
        if (log.size() != 0) {
            System.out.println("FAIL: Expected empty log, got " + log);
            System.exit(1);
        }

        // Transition to Active with args
        s.start();
        log = s.get_log();
        if (!log.contains("idle:start")) {
            System.out.println("FAIL: Expected 'idle:start' in log, got " + log);
            System.exit(1);
        }
        if (!log.contains("active:enter:from_idle:42")) {
            System.out.println("FAIL: Expected 'active:enter:from_idle:42' in log, got " + log);
            System.exit(1);
        }
        System.out.println("Log after transition: " + log);

        System.out.println("PASS: Transition enter args work correctly");
    }
}
