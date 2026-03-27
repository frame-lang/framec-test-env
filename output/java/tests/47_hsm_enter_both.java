import java.util.*;


import java.util.*;

class HSMEnterBothFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMEnterBothFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMEnterBothFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMEnterBothFrameContext {
    HSMEnterBothFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMEnterBothFrameContext(HSMEnterBothFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMEnterBothCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMEnterBothFrameEvent forward_event;
    HSMEnterBothCompartment parent_compartment;

    HSMEnterBothCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMEnterBothCompartment copy() {
        HSMEnterBothCompartment c = new HSMEnterBothCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMEnterBoth {
    private ArrayList<HSMEnterBothCompartment> _state_stack;
    private HSMEnterBothCompartment __compartment;
    private HSMEnterBothCompartment __next_compartment;
    private ArrayList<HSMEnterBothFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMEnterBoth() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new HSMEnterBothCompartment("Start");
        __next_compartment = null;
        HSMEnterBothFrameEvent __frame_event = new HSMEnterBothFrameEvent("$>");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMEnterBothFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMEnterBothFrameEvent exit_event = new HSMEnterBothFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMEnterBothFrameEvent enter_event = new HSMEnterBothFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMEnterBothFrameEvent enter_event = new HSMEnterBothFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMEnterBothFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMEnterBothCompartment next) {
        __next_compartment = next;
    }

    public void go_to_child() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("go_to_child");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_to_parent() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("go_to_parent");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("get_log");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMEnterBothFrameEvent __e = new HSMEnterBothFrameEvent("get_state");
        HSMEnterBothFrameContext __ctx = new HSMEnterBothFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMEnterBothFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log.add("Parent:enter");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        } else if (__e._message.equals("go_to_child")) {
            var __compartment = new HSMEnterBothCompartment("Child");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Start(HSMEnterBothFrameEvent __e) {
        if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Start";
            return;
        } else if (__e._message.equals("go_to_child")) {
            var __compartment = new HSMEnterBothCompartment("Child");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("go_to_parent")) {
            var __compartment = new HSMEnterBothCompartment("Parent");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Child(HSMEnterBothFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.log.add("Child:enter");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Child";
            return;
        } else if (__e._message.equals("go_to_parent")) {
            var __compartment = new HSMEnterBothCompartment("Parent");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 47: HSM Enter in Both ===");
        var s = new HSMEnterBoth();

        // TC2.3.1: Only child's enter fires when entering child
        s.go_to_child();
        ArrayList log = s.get_log();
        if (!log.contains("Child:enter")) {
            System.out.println("FAIL: Expected Child:enter, got " + log);
            System.exit(1);
        }
        if (log.contains("Parent:enter")) {
            System.out.println("FAIL: Parent:enter should NOT fire when entering child, got " + log);
            System.exit(1);
        }
        if (!s.get_state().equals("Child")) {
            System.out.println("FAIL: Expected Child, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC2.3.1: Only child's enter fires when entering child - PASS");

        // TC2.3.2: Parent's enter fires only when transitioning to parent
        s.go_to_parent();
        log = s.get_log();
        if (!log.contains("Parent:enter")) {
            System.out.println("FAIL: Expected Parent:enter, got " + log);
            System.exit(1);
        }
        if (!s.get_state().equals("Parent")) {
            System.out.println("FAIL: Expected Parent, got " + s.get_state());
            System.exit(1);
        }
        System.out.println("TC2.3.2: Parent's enter fires when transitioning to parent - PASS");

        // TC2.3.3: No implicit cascading - counts should be exactly 1 each
        int childCount = 0;
        int parentCount = 0;
        for (Object item : log) {
            if (item.equals("Child:enter")) childCount++;
            if (item.equals("Parent:enter")) parentCount++;
        }
        if (childCount != 1) {
            System.out.println("FAIL: Expected exactly 1 Child:enter, got " + log);
            System.exit(1);
        }
        if (parentCount != 1) {
            System.out.println("FAIL: Expected exactly 1 Parent:enter, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.3.3: No implicit cascading of enter handlers - PASS");

        // TC2.3.4: Going back to child fires child enter again
        s.go_to_child();
        log = s.get_log();
        int childCount2 = 0;
        int parentCount2 = 0;
        for (Object item : log) {
            if (item.equals("Child:enter")) childCount2++;
            if (item.equals("Parent:enter")) parentCount2++;
        }
        if (childCount2 != 2) {
            System.out.println("FAIL: Expected 2 Child:enter, got " + log);
            System.exit(1);
        }
        if (parentCount2 != 1) {
            System.out.println("FAIL: Expected still 1 Parent:enter, got " + log);
            System.exit(1);
        }
        System.out.println("TC2.3.4: Re-entering child fires child enter again - PASS");

        System.out.println("PASS: HSM enter in both works correctly");
    }
}
