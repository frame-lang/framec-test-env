import java.util.*;


import java.util.*;

class SimpleDockerFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SimpleDockerFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SimpleDockerFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SimpleDockerFrameContext {
    SimpleDockerFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SimpleDockerFrameContext(SimpleDockerFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SimpleDockerCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SimpleDockerFrameEvent forward_event;
    SimpleDockerCompartment parent_compartment;

    SimpleDockerCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SimpleDockerCompartment copy() {
        SimpleDockerCompartment c = new SimpleDockerCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SimpleDocker {
    private ArrayList<SimpleDockerCompartment> _state_stack;
    private SimpleDockerCompartment __compartment;
    private SimpleDockerCompartment __next_compartment;
    private ArrayList<SimpleDockerFrameContext> _context_stack;

    public SimpleDocker() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SimpleDockerCompartment("Start");
        __next_compartment = null;
        SimpleDockerFrameEvent __frame_event = new SimpleDockerFrameEvent("$>");
        SimpleDockerFrameContext __ctx = new SimpleDockerFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SimpleDockerFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SimpleDockerFrameEvent exit_event = new SimpleDockerFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SimpleDockerFrameEvent enter_event = new SimpleDockerFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SimpleDockerFrameEvent enter_event = new SimpleDockerFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SimpleDockerFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("End")) {
            _state_End(__e);
        }
    }

    private void __transition(SimpleDockerCompartment next) {
        __next_compartment = next;
    }

    public void run() {
        SimpleDockerFrameEvent __e = new SimpleDockerFrameEvent("run");
        SimpleDockerFrameContext __ctx = new SimpleDockerFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Start(SimpleDockerFrameEvent __e) {
        if (__e._message.equals("run")) {
            System.out.println("SUCCESS: Hello from Docker");
            var __compartment = new SimpleDockerCompartment("End");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_End(SimpleDockerFrameEvent __e) {

    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..1");
        try {
            SimpleDocker s = new SimpleDocker();
            System.out.println("ok 1 - simple_test");
        } catch (Exception ex) {
            System.out.println("not ok 1 - simple_test # " + ex);
        }
    }
}
