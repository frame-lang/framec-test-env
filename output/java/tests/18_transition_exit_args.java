import java.util.*;


import java.util.*;

class TransitionExitArgsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    TransitionExitArgsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    TransitionExitArgsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TransitionExitArgsFrameContext {
    TransitionExitArgsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    TransitionExitArgsFrameContext(TransitionExitArgsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class TransitionExitArgsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    TransitionExitArgsFrameEvent forward_event;
    TransitionExitArgsCompartment parent_compartment;

    TransitionExitArgsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    TransitionExitArgsCompartment copy() {
        TransitionExitArgsCompartment c = new TransitionExitArgsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TransitionExitArgs {
    private ArrayList<TransitionExitArgsCompartment> _state_stack;
    private TransitionExitArgsCompartment __compartment;
    private TransitionExitArgsCompartment __next_compartment;
    private ArrayList<TransitionExitArgsFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public TransitionExitArgs() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new TransitionExitArgsCompartment("Active");
        __next_compartment = null;
        TransitionExitArgsFrameEvent __frame_event = new TransitionExitArgsFrameEvent("$>");
        TransitionExitArgsFrameContext __ctx = new TransitionExitArgsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(TransitionExitArgsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TransitionExitArgsFrameEvent exit_event = new TransitionExitArgsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TransitionExitArgsFrameEvent enter_event = new TransitionExitArgsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    TransitionExitArgsFrameEvent enter_event = new TransitionExitArgsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TransitionExitArgsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Active")) {
            _state_Active(__e);
        } else if (state_name.equals("Done")) {
            _state_Done(__e);
        }
    }

    private void __transition(TransitionExitArgsCompartment next) {
        __next_compartment = next;
    }

    public void leave() {
        TransitionExitArgsFrameEvent __e = new TransitionExitArgsFrameEvent("leave");
        TransitionExitArgsFrameContext __ctx = new TransitionExitArgsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        TransitionExitArgsFrameEvent __e = new TransitionExitArgsFrameEvent("get_log");
        TransitionExitArgsFrameContext __ctx = new TransitionExitArgsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Active(TransitionExitArgsFrameEvent __e) {
        if (__e._message.equals("<$")) {
            var reason = (String) __compartment.exit_args.get("0");
            var code = (int) __compartment.exit_args.get("1");
            this.log.add("exit:" + reason + ":" + code);
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("leave")) {
            this.log.add("leaving");
            __compartment.exit_args.put("0", "cleanup");
            __compartment.exit_args.put("1", 42);
            var __compartment = new TransitionExitArgsCompartment("Done");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Done(TransitionExitArgsFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log.add("enter:done");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 18: Transition Exit Args ===");
        var s = new TransitionExitArgs();

        // Initial state is Active
        ArrayList log = s.get_log();
        if (log.size() != 0) {
            System.out.println("FAIL: Expected empty log, got " + log);
            System.exit(1);
        }

        // Leave - should call exit handler with args
        s.leave();
        log = s.get_log();
        if (!log.contains("leaving")) {
            System.out.println("FAIL: Expected 'leaving' in log, got " + log);
            System.exit(1);
        }
        if (!log.contains("exit:cleanup:42")) {
            System.out.println("FAIL: Expected 'exit:cleanup:42' in log, got " + log);
            System.exit(1);
        }
        if (!log.contains("enter:done")) {
            System.out.println("FAIL: Expected 'enter:done' in log, got " + log);
            System.exit(1);
        }
        System.out.println("Log after transition: " + log);

        System.out.println("PASS: Transition exit args work correctly");
    }
}
