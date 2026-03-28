import java.util.*;


import java.util.*;

class HSMEnterParentOnlyFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMEnterParentOnlyFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMEnterParentOnlyFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterParentOnlyFrameContext {
    HSMEnterParentOnlyFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMEnterParentOnlyFrameContext(HSMEnterParentOnlyFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMEnterParentOnlyCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMEnterParentOnlyFrameEvent forward_event;
    HSMEnterParentOnlyCompartment parent_compartment;

    HSMEnterParentOnlyCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMEnterParentOnlyCompartment copy() {
        HSMEnterParentOnlyCompartment c = new HSMEnterParentOnlyCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterParentOnly {
    private ArrayList<HSMEnterParentOnlyCompartment> _state_stack;
    private HSMEnterParentOnlyCompartment __compartment;
    private HSMEnterParentOnlyCompartment __next_compartment;
    private ArrayList<HSMEnterParentOnlyFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMEnterParentOnly() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new HSMEnterParentOnlyCompartment("Start");
        __next_compartment = null;
        HSMEnterParentOnlyFrameEvent __frame_event = new HSMEnterParentOnlyFrameEvent("$>");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMEnterParentOnlyFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterParentOnlyFrameEvent exit_event = new HSMEnterParentOnlyFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterParentOnlyFrameEvent enter_event = new HSMEnterParentOnlyFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMEnterParentOnlyFrameEvent enter_event = new HSMEnterParentOnlyFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterParentOnlyFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterParentOnlyCompartment next) {
        __next_compartment = next;
    }

    public void go_to_child() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("go_to_child");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_to_parent() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("go_to_parent");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("get_log");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMEnterParentOnlyFrameEvent __e = new HSMEnterParentOnlyFrameEvent("get_state");
        HSMEnterParentOnlyFrameContext __ctx = new HSMEnterParentOnlyFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Start(HSMEnterParentOnlyFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Start";
            return;
        } else if (__e._message.equals("go_to_child")) {
            var __compartment = new HSMEnterParentOnlyCompartment("Child");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("go_to_parent")) {
            var __compartment = new HSMEnterParentOnlyCompartment("Parent");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Child(HSMEnterParentOnlyFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Child";
            return;
        } else if (__e._message.equals("go_to_parent")) {
            var __compartment = new HSMEnterParentOnlyCompartment("Parent");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Parent(HSMEnterParentOnlyFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log.add("Parent:enter");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        } else if (__e._message.equals("go_to_child")) {
            var __compartment = new HSMEnterParentOnlyCompartment("Child");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 46: HSM Enter in Parent Only ===");
        var s = new HSMEnterParentOnly();

        // TC2.2.1: Child enters without error (no enter handler)
        s.go_to_child();
        if (!s.get_state().equals("Child")) {
            System.out.println("FAIL: Expected Child, got " + s.get_state());
            System.exit(1);
        }
        ArrayList log = s.get_log();
        System.out.println("TC2.2.1: Child enters without error (log: " + log + ") - PASS");

        // TC2.2.2: Parent's enter does NOT auto-fire when child is entered
        if (log.contains("Parent:enter")) {
            System.out.println("FAIL: Parent:enter should NOT fire for child entry, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.2.2: Parent enter NOT auto-fired for child - PASS");

        // TC2.2.3: Parent enter only fires when transitioning directly TO parent
        s.go_to_parent();
        if (!s.get_state().equals("Parent")) {
            System.out.println("FAIL: Expected Parent, got " + s.get_state());
            System.exit(1);
        }
        log = s.get_log();
        if (!log.contains("Parent:enter")) {
            System.out.println("FAIL: Expected Parent:enter when transitioning to Parent, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.2.3: Parent enter fires when transitioning to Parent - PASS");

        // TC2.2.4: Going back to child from parent
        s.go_to_child();
        if (!s.get_state().equals("Child")) {
            System.out.println("FAIL: Expected Child, got " + s.get_state());
            System.exit(1);
        }
        log = s.get_log();
        int count = 0;
        for (Object item : log) {
            if (item.equals("Parent:enter")) count++;
        }
        if (count != 1) {
            System.out.println("FAIL: Expected exactly 1 Parent:enter, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.2.4: Return to child, parent enter count unchanged - PASS");

        System.out.println("PASS: HSM enter in parent only works correctly");
    }
}
