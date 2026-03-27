import java.util.*;


import java.util.*;

class HSMEnterChildOnlyFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMEnterChildOnlyFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMEnterChildOnlyFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterChildOnlyFrameContext {
    HSMEnterChildOnlyFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMEnterChildOnlyFrameContext(HSMEnterChildOnlyFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMEnterChildOnlyCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMEnterChildOnlyFrameEvent forward_event;
    HSMEnterChildOnlyCompartment parent_compartment;

    HSMEnterChildOnlyCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMEnterChildOnlyCompartment copy() {
        HSMEnterChildOnlyCompartment c = new HSMEnterChildOnlyCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterChildOnly {
    private ArrayList<HSMEnterChildOnlyCompartment> _state_stack;
    private HSMEnterChildOnlyCompartment __compartment;
    private HSMEnterChildOnlyCompartment __next_compartment;
    private ArrayList<HSMEnterChildOnlyFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMEnterChildOnly() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new HSMEnterChildOnlyCompartment("Start");
        __next_compartment = null;
        HSMEnterChildOnlyFrameEvent __frame_event = new HSMEnterChildOnlyFrameEvent("$>");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMEnterChildOnlyFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterChildOnlyFrameEvent exit_event = new HSMEnterChildOnlyFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterChildOnlyFrameEvent enter_event = new HSMEnterChildOnlyFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMEnterChildOnlyFrameEvent enter_event = new HSMEnterChildOnlyFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterChildOnlyFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterChildOnlyCompartment next) {
        __next_compartment = next;
    }

    public void go_to_child() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("go_to_child");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forward_action() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("forward_action");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("get_log");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMEnterChildOnlyFrameEvent __e = new HSMEnterChildOnlyFrameEvent("get_state");
        HSMEnterChildOnlyFrameContext __ctx = new HSMEnterChildOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Child(HSMEnterChildOnlyFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log.add("Child:enter");
        } else if (__e._message.equals("forward_action")) {
            this.log.add("Child:forward");
            _state_Parent(__e);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Child";
            return;
        }
    }

    private void _state_Start(HSMEnterChildOnlyFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Start";
            return;
        } else if (__e._message.equals("go_to_child")) {
            var __compartment = new HSMEnterChildOnlyCompartment("Child");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Parent(HSMEnterChildOnlyFrameEvent __e) {
        if (__e._message.equals("forward_action")) {
            this.log.add("Parent:forward_action");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 45: HSM Enter in Child Only ===");
        var s = new HSMEnterChildOnly();

        // Start state has no enter
        if (!s.get_state().equals("Start")) {
            System.out.println("FAIL: Expected Start, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC2.1.0: Initial state is Start - PASS");

        // TC2.1.1: Child enter handler fires on entry
        s.go_to_child();
        ArrayList log = s.get_log();
        if (!log.contains("Child:enter")) {
            System.out.println("FAIL: Expected Child:enter, got " + log);
            System.exit(1);
        }
        if (!s.get_state().equals("Child")) {
            System.out.println("FAIL: Expected Child, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC2.1.1: Child enter handler fires - PASS");

        // TC2.1.2: No error when parent lacks enter (verified by compilation/execution)
        System.out.println("TC2.1.2: No error when parent lacks enter - PASS");

        // TC2.1.3: Forward to parent works without parent having enter
        s.forward_action();
        log = s.get_log();
        if (!log.contains("Child:forward")) {
            System.out.println("FAIL: Expected Child:forward, got " + log);
            System.exit(1);
        }
        if (!log.contains("Parent:forward_action")) {
            System.out.println("FAIL: Expected Parent handler, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.1.3: Forward works without parent enter - PASS");

        System.out.println("PASS: HSM enter in child only works correctly");
    }
}
