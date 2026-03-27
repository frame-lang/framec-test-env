import java.util.*;


import java.util.*;

class SysXFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SysXFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SysXFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SysXFrameContext {
    SysXFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SysXFrameContext(SysXFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SysXCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SysXFrameEvent forward_event;
    SysXCompartment parent_compartment;

    SysXCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SysXCompartment copy() {
        SysXCompartment c = new SysXCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SysX {
    private ArrayList<SysXCompartment> _state_stack;
    private SysXCompartment __compartment;
    private SysXCompartment __next_compartment;
    private ArrayList<SysXFrameContext> _context_stack;

    public SysX() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SysXCompartment("A");
        __next_compartment = null;
        SysXFrameEvent __frame_event = new SysXFrameEvent("$>");
        SysXFrameContext __ctx = new SysXFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SysXFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SysXFrameEvent exit_event = new SysXFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SysXFrameEvent enter_event = new SysXFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SysXFrameEvent enter_event = new SysXFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SysXFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("A")) {
            _state_A(__e);
        } else if (state_name.equals("B")) {
            _state_B(__e);
        }
    }

    private void __transition(SysXCompartment next) {
        __next_compartment = next;
    }

    public void e() {
        SysXFrameEvent __e = new SysXFrameEvent("e");
        SysXFrameContext __ctx = new SysXFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_B(SysXFrameEvent __e) {

    }

    private void _state_A(SysXFrameEvent __e) {
        if (__e._message.equals("e")) {
            var __compartment = new SysXCompartment("B");
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
            SysX s = new SysX();
            s.e();
            System.out.println("ok 1 - transition_state_id_exec");
        } catch (Exception ex) {
            System.out.println("not ok 1 - transition_state_id_exec # " + ex);
        }
    }
}
