import java.util.*;


import java.util.*;

class EnterExitFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    EnterExitFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    EnterExitFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class EnterExitFrameContext {
    EnterExitFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    EnterExitFrameContext(EnterExitFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class EnterExitCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    EnterExitFrameEvent forward_event;
    EnterExitCompartment parent_compartment;

    EnterExitCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    EnterExitCompartment copy() {
        EnterExitCompartment c = new EnterExitCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class EnterExit {
    private ArrayList<EnterExitCompartment> _state_stack;
    private EnterExitCompartment __compartment;
    private EnterExitCompartment __next_compartment;
    private ArrayList<EnterExitFrameContext> _context_stack;
    public ArrayList<String> log = new ArrayList<>();

    public EnterExit() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new EnterExitCompartment("Off");
        __next_compartment = null;
        EnterExitFrameEvent __frame_event = new EnterExitFrameEvent("$>");
        EnterExitFrameContext __ctx = new EnterExitFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(EnterExitFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            EnterExitFrameEvent exit_event = new EnterExitFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                EnterExitFrameEvent enter_event = new EnterExitFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    EnterExitFrameEvent enter_event = new EnterExitFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(EnterExitFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Off")) {
            _state_Off(__e);
        } else if (state_name.equals("On")) {
            _state_On(__e);
        }
    }

    private void __transition(EnterExitCompartment next) {
        __next_compartment = next;
    }

    public void toggle() {
        EnterExitFrameEvent __e = new EnterExitFrameEvent("toggle");
        EnterExitFrameContext __ctx = new EnterExitFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList<String> get_log() {
        EnterExitFrameEvent __e = new EnterExitFrameEvent("get_log");
        EnterExitFrameContext __ctx = new EnterExitFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList<String>) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Off(EnterExitFrameEvent __e) {
        if (__e._message.equals("<$")) {
            this.log.add("exit:Off");
            System.out.println("Exiting Off state");
        } else if (__e._message.equals("$>")) {
            this.log.add("enter:Off");
            System.out.println("Entered Off state");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("toggle")) {
            var __compartment = new EnterExitCompartment("On");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_On(EnterExitFrameEvent __e) {
        if (__e._message.equals("<$")) {
            this.log.add("exit:On");
            System.out.println("Exiting On state");
        } else if (__e._message.equals("$>")) {
            this.log.add("enter:On");
            System.out.println("Entered On state");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("toggle")) {
            var __compartment = new EnterExitCompartment("Off");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    @SuppressWarnings("unchecked")
    public static void main(String[] args) {
        System.out.println("=== Test 05: Enter/Exit Handlers ===");
        var s = new EnterExit();

        // Initial enter should have been called
        ArrayList<String> log = (ArrayList<String>) s.get_log();
        if (!log.contains("enter:Off")) {
            throw new RuntimeException("Expected 'enter:Off' in log, got " + log);
        }
        System.out.println("After construction: " + log);

        // Toggle to On - should exit Off, enter On
        s.toggle();
        log = (ArrayList<String>) s.get_log();
        if (!log.contains("exit:Off")) {
            throw new RuntimeException("Expected 'exit:Off' in log, got " + log);
        }
        if (!log.contains("enter:On")) {
            throw new RuntimeException("Expected 'enter:On' in log, got " + log);
        }
        System.out.println("After toggle to On: " + log);

        // Toggle back to Off - should exit On, enter Off
        s.toggle();
        log = (ArrayList<String>) s.get_log();
        int enterOffCount = 0;
        for (String entry : log) {
            if (entry.equals("enter:Off")) enterOffCount++;
        }
        if (enterOffCount != 2) {
            throw new RuntimeException("Expected 2 'enter:Off' entries, got " + log);
        }
        if (!log.contains("exit:On")) {
            throw new RuntimeException("Expected 'exit:On' in log, got " + log);
        }
        System.out.println("After toggle to Off: " + log);

        System.out.println("PASS: Enter/Exit handlers work correctly");
    }
}
