import java.util.*;


import java.util.*;

class HSMDefaultForwardFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMDefaultForwardFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMDefaultForwardFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMDefaultForwardFrameContext {
    HSMDefaultForwardFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMDefaultForwardFrameContext(HSMDefaultForwardFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMDefaultForwardCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMDefaultForwardFrameEvent forward_event;
    HSMDefaultForwardCompartment parent_compartment;

    HSMDefaultForwardCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMDefaultForwardCompartment copy() {
        HSMDefaultForwardCompartment c = new HSMDefaultForwardCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMDefaultForward {
    private ArrayList<HSMDefaultForwardCompartment> _state_stack;
    private HSMDefaultForwardCompartment __compartment;
    private HSMDefaultForwardCompartment __next_compartment;
    private ArrayList<HSMDefaultForwardFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMDefaultForward() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMDefaultForwardCompartment("Parent");
        this.__compartment = new HSMDefaultForwardCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMDefaultForwardFrameEvent __frame_event = new HSMDefaultForwardFrameEvent("$>");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMDefaultForwardFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMDefaultForwardFrameEvent exit_event = new HSMDefaultForwardFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMDefaultForwardFrameEvent enter_event = new HSMDefaultForwardFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMDefaultForwardFrameEvent enter_event = new HSMDefaultForwardFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMDefaultForwardFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMDefaultForwardCompartment next) {
        __next_compartment = next;
    }

    public void handled_event() {
        HSMDefaultForwardFrameEvent __e = new HSMDefaultForwardFrameEvent("handled_event");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void unhandled_event() {
        HSMDefaultForwardFrameEvent __e = new HSMDefaultForwardFrameEvent("unhandled_event");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMDefaultForwardFrameEvent __e = new HSMDefaultForwardFrameEvent("get_log");
        HSMDefaultForwardFrameContext __ctx = new HSMDefaultForwardFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMDefaultForwardFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("handled_event")) {
            this.log.add("Parent:handled_event");
        } else if (__e._message.equals("unhandled_event")) {
            this.log.add("Parent:unhandled_event");
        }
    }

    private void _state_Child(HSMDefaultForwardFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("handled_event")) {
            this.log.add("Child:handled_event");
        } else {
            _state_Parent(__e);
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 30: HSM State-Level Default Forward ===");
        var s = new HSMDefaultForward();

        s.handled_event();
        ArrayList log = s.get_log();
        if (!log.contains("Child:handled_event")) {
            System.out.println("FAIL: Expected 'Child:handled_event' in log, got " + log);
            System.exit(1);
        }
        System.out.println("After handled_event: " + log);

        s.unhandled_event();
        log = s.get_log();
        if (!log.contains("Parent:unhandled_event")) {
            System.out.println("FAIL: Expected 'Parent:unhandled_event' in log (forwarded), got " + log);
            System.exit(1);
        }
        System.out.println("After unhandled_event (forwarded): " + log);

        System.out.println("PASS: HSM state-level default forward works correctly");
    }
}
