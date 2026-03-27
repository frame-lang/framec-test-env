import java.util.*;


import java.util.*;

class Stubs {
    static void x() {}
    static void y() {}
}

class SFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SFrameContext {
    SFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SFrameContext(SFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SFrameEvent forward_event;
    SCompartment parent_compartment;

    SCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SCompartment copy() {
        SCompartment c = new SCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class S {
    private ArrayList<SCompartment> _state_stack;
    private SCompartment __compartment;
    private SCompartment __next_compartment;
    private ArrayList<SFrameContext> _context_stack;

    public S() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SCompartment("A");
        __next_compartment = null;
        SFrameEvent __frame_event = new SFrameEvent("$>");
        SFrameContext __ctx = new SFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SFrameEvent exit_event = new SFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SFrameEvent enter_event = new SFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SFrameEvent enter_event = new SFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("A")) {
            _state_A(__e);
        }
    }

    private void __transition(SCompartment next) {
        __next_compartment = next;
    }

    public void e() {
        SFrameEvent __e = new SFrameEvent("e");
        SFrameContext __ctx = new SFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_A(SFrameEvent __e) {
        if (__e._message.equals("e")) {
            _state_stack.add(__compartment.copy());
            Stubs.x();
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..1");
        try {
            S s = new S();
            s.e();
            System.out.println("ok 1 - stack_ops_then_native");
        } catch (Exception ex) {
            System.out.println("not ok 1 - stack_ops_then_native # " + ex);
        }
    }
}
