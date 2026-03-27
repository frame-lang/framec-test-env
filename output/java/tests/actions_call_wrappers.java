import java.util.*;


import java.util.*;

class CallMismatchFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    CallMismatchFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    CallMismatchFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class CallMismatchFrameContext {
    CallMismatchFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    CallMismatchFrameContext(CallMismatchFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class CallMismatchCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    CallMismatchFrameEvent forward_event;
    CallMismatchCompartment parent_compartment;

    CallMismatchCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    CallMismatchCompartment copy() {
        CallMismatchCompartment c = new CallMismatchCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class CallMismatch {
    private ArrayList<CallMismatchCompartment> _state_stack;
    private CallMismatchCompartment __compartment;
    private CallMismatchCompartment __next_compartment;
    private ArrayList<CallMismatchFrameContext> _context_stack;
    public String last = "";

    public CallMismatch() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new CallMismatchCompartment("S");
        __next_compartment = null;
        CallMismatchFrameEvent __frame_event = new CallMismatchFrameEvent("$>");
        CallMismatchFrameContext __ctx = new CallMismatchFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(CallMismatchFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            CallMismatchFrameEvent exit_event = new CallMismatchFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                CallMismatchFrameEvent enter_event = new CallMismatchFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    CallMismatchFrameEvent enter_event = new CallMismatchFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(CallMismatchFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("S")) {
            _state_S(__e);
        }
    }

    private void __transition(CallMismatchCompartment next) {
        __next_compartment = next;
    }

    public void e() {
        CallMismatchFrameEvent __e = new CallMismatchFrameEvent("e");
        CallMismatchFrameContext __ctx = new CallMismatchFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_S(CallMismatchFrameEvent __e) {
        if (__e._message.equals("e")) {
            this.handle();
        }
    }

    private void log(Object message) {
                    // log sink
                    this.last = message;
    }

    private void handle() {
                    // Calls 'log' without _action_ prefix; wrappers should preserve FRM names
                    this.log("hello");
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..1");
        try {
            CallMismatch s = new CallMismatch();
            s.e();
            System.out.println("ok 1 - actions_call_wrappers");
        } catch (Exception ex) {
            System.out.println("not ok 1 - actions_call_wrappers # " + ex);
        }
    }
}
