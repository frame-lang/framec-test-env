import java.util.*;


import java.util.*;

class PFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    PFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    PFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PFrameContext {
    PFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    PFrameContext(PFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class PCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    PFrameEvent forward_event;
    PCompartment parent_compartment;

    PCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    PCompartment copy() {
        PCompartment c = new PCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class P {
    private ArrayList<PCompartment> _state_stack;
    private PCompartment __compartment;
    private PCompartment __next_compartment;
    private ArrayList<PFrameContext> _context_stack;

    public P() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new PCompartment("A");
        __next_compartment = null;
        PFrameEvent __frame_event = new PFrameEvent("$>");
        PFrameContext __ctx = new PFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(PFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            PFrameEvent exit_event = new PFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                PFrameEvent enter_event = new PFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    PFrameEvent enter_event = new PFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(PFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("A")) {
            _state_A(__e);
        } else if (state_name.equals("B")) {
            _state_B(__e);
        }
    }

    private void __transition(PCompartment next) {
        __next_compartment = next;
    }

    public void e() {
        PFrameEvent __e = new PFrameEvent("e");
        PFrameContext __ctx = new PFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_A(PFrameEvent __e) {
        if (__e._message.equals("e")) {
            var __compartment = new PCompartment("B");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_B(PFrameEvent __e) {
        if (__e._message.equals("e")) {
            ;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..1");
        try {
            P s = new P();
            s.e();
            System.out.println("ok 1 - basic_project");
        } catch (Exception ex) {
            System.out.println("not ok 1 - basic_project # " + ex);
        }
    }
}
