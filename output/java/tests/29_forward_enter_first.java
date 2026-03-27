import java.util.*;


import java.util.*;

class ForwardEnterFirstFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    ForwardEnterFirstFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    ForwardEnterFirstFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class ForwardEnterFirstFrameContext {
    ForwardEnterFirstFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    ForwardEnterFirstFrameContext(ForwardEnterFirstFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class ForwardEnterFirstCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    ForwardEnterFirstFrameEvent forward_event;
    ForwardEnterFirstCompartment parent_compartment;

    ForwardEnterFirstCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    ForwardEnterFirstCompartment copy() {
        ForwardEnterFirstCompartment c = new ForwardEnterFirstCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class ForwardEnterFirst {
    private ArrayList<ForwardEnterFirstCompartment> _state_stack;
    private ForwardEnterFirstCompartment __compartment;
    private ForwardEnterFirstCompartment __next_compartment;
    private ArrayList<ForwardEnterFirstFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public ForwardEnterFirst() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new ForwardEnterFirstCompartment("Idle");
        __next_compartment = null;
        ForwardEnterFirstFrameEvent __frame_event = new ForwardEnterFirstFrameEvent("$>");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(ForwardEnterFirstFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            ForwardEnterFirstFrameEvent exit_event = new ForwardEnterFirstFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                ForwardEnterFirstFrameEvent enter_event = new ForwardEnterFirstFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    ForwardEnterFirstFrameEvent enter_event = new ForwardEnterFirstFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(ForwardEnterFirstFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Working")) {
            _state_Working(__e);
        }
    }

    private void __transition(ForwardEnterFirstCompartment next) {
        __next_compartment = next;
    }

    public void process() {
        ForwardEnterFirstFrameEvent __e = new ForwardEnterFirstFrameEvent("process");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public int get_counter() {
        ForwardEnterFirstFrameEvent __e = new ForwardEnterFirstFrameEvent("get_counter");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public ArrayList get_log() {
        ForwardEnterFirstFrameEvent __e = new ForwardEnterFirstFrameEvent("get_log");
        ForwardEnterFirstFrameContext __ctx = new ForwardEnterFirstFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Working(ForwardEnterFirstFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Working")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("counter")) {
                __sv_comp.state_vars.put("counter", 100);
            }
            this.log.add("Working:enter");
        } else if (__e._message.equals("get_counter")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("counter");
            return;
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("process")) {
            this.log.add("Working:process:counter=" + (int) __sv_comp.state_vars.get("counter"));
            __sv_comp.state_vars.put("counter", (int) __sv_comp.state_vars.get("counter") + 1);
        }
    }

    private void _state_Idle(ForwardEnterFirstFrameEvent __e) {
        if (__e._message.equals("get_counter")) {
            _context_stack.get(_context_stack.size() - 1)._return = -1;
            return;
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("process")) {
            var __compartment = new ForwardEnterFirstCompartment("Working");
            __compartment.parent_compartment = this.__compartment.copy();
            __compartment.forward_event = __e;
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 29: Forward Enter First ===");
        var s = new ForwardEnterFirst();

        if (s.get_counter() != -1) {
            System.out.println("FAIL: Expected -1 in Idle");
            System.exit(1);
        }

        s.process();

        int counter = s.get_counter();
        ArrayList log = s.get_log();
        System.out.println("Counter after forward: " + counter);
        System.out.println("Log: " + log);

        if (!log.contains("Working:enter")) {
            System.out.println("FAIL: Expected 'Working:enter' in log: " + log);
            System.exit(1);
        }

        if (!log.contains("Working:process:counter=100")) {
            System.out.println("FAIL: Expected 'Working:process:counter=100' in log: " + log);
            System.exit(1);
        }

        if (counter != 101) {
            System.out.println("FAIL: Expected counter=101, got " + counter);
            System.exit(1);
        }

        int enterIdx = log.indexOf("Working:enter");
        int processIdx = log.indexOf("Working:process:counter=100");
        if (enterIdx >= processIdx) {
            System.out.println("FAIL: $> should run before process: " + log);
            System.exit(1);
        }

        System.out.println("PASS: Forward sends $> first for non-$> events");
    }
}
