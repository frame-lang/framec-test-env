import java.util.*;


import java.util.*;

class S2FrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    S2FrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    S2FrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class S2FrameContext {
    S2FrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    S2FrameContext(S2FrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class S2Compartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    S2FrameEvent forward_event;
    S2Compartment parent_compartment;

    S2Compartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    S2Compartment copy() {
        S2Compartment c = new S2Compartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class S2 {
    private ArrayList<S2Compartment> _state_stack;
    private S2Compartment __compartment;
    private S2Compartment __next_compartment;
    private ArrayList<S2FrameContext> _context_stack;

    public S2() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new S2Compartment("A");
        __next_compartment = null;
        S2FrameEvent __frame_event = new S2FrameEvent("$>");
        S2FrameContext __ctx = new S2FrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(S2FrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            S2FrameEvent exit_event = new S2FrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                S2FrameEvent enter_event = new S2FrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    S2FrameEvent enter_event = new S2FrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(S2FrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("A")) {
            _state_A(__e);
        }
    }

    private void __transition(S2Compartment next) {
        __next_compartment = next;
    }

    public void e() {
        S2FrameEvent __e = new S2FrameEvent("e");
        S2FrameContext __ctx = new S2FrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_A(S2FrameEvent __e) {
        if (__e._message.equals("e")) {
            var __compartment = new S2Compartment("A");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..1");
        try {
            S2 s = new S2();
            s.e();
            System.out.println("ok 1 - mod_b");
        } catch (Exception ex) {
            System.out.println("not ok 1 - mod_b # " + ex);
        }
    }
}
