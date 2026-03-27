import java.util.*;


import java.util.*;

class HSMSingleParentFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMSingleParentFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMSingleParentFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMSingleParentFrameContext {
    HSMSingleParentFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMSingleParentFrameContext(HSMSingleParentFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMSingleParentCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMSingleParentFrameEvent forward_event;
    HSMSingleParentCompartment parent_compartment;

    HSMSingleParentCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMSingleParentCompartment copy() {
        HSMSingleParentCompartment c = new HSMSingleParentCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMSingleParent {
    private ArrayList<HSMSingleParentCompartment> _state_stack;
    private HSMSingleParentCompartment __compartment;
    private HSMSingleParentCompartment __next_compartment;
    private ArrayList<HSMSingleParentFrameContext> _context_stack;
    public ArrayList log = new ArrayList();

    public HSMSingleParent() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new HSMSingleParentCompartment("Parent");
        this.__compartment = new HSMSingleParentCompartment("Child");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        HSMSingleParentFrameEvent __frame_event = new HSMSingleParentFrameEvent("$>");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(HSMSingleParentFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMSingleParentFrameEvent exit_event = new HSMSingleParentFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMSingleParentFrameEvent enter_event = new HSMSingleParentFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    HSMSingleParentFrameEvent enter_event = new HSMSingleParentFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMSingleParentFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Child")) {
            _state_Child(__e);
        } else if (state_name.equals("Parent")) {
            _state_Parent(__e);
        }
    }

    private void __transition(HSMSingleParentCompartment next) {
        __next_compartment = next;
    }

    public void child_only() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("child_only");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void forward_to_parent() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("forward_to_parent");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public ArrayList get_log() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("get_log");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (ArrayList) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMSingleParentFrameEvent __e = new HSMSingleParentFrameEvent("get_state");
        HSMSingleParentFrameContext __ctx = new HSMSingleParentFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Child(HSMSingleParentFrameEvent __e) {
        if (__e._message.equals("child_only")) {
            this.log.add("Child:child_only");
        } else if (__e._message.equals("forward_to_parent")) {
            this.log.add("Child:before_forward");
            _state_Parent(__e);
            this.log.add("Child:after_forward");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Child";
            return;
        }
    }

    private void _state_Parent(HSMSingleParentFrameEvent __e) {
        if (__e._message.equals("forward_to_parent")) {
            this.log.add("Parent:forward_to_parent");
        } else if (__e._message.equals("get_log")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.log;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 41: HSM Single Parent ===");
        var s = new HSMSingleParent();

        // TC1.1.1: Child declares parent with `=> $Parent` syntax (verified by compilation)
        System.out.println("TC1.1.1: Child-Parent relationship compiles - PASS");

        // TC1.1.2: Child can forward events to parent
        s.forward_to_parent();
        ArrayList log = s.get_log();
        if (!log.contains("Child:before_forward")) {
            System.out.println("FAIL: Expected Child:before_forward in log, got " + log);
            System.exit(1);
        }
        if (!log.contains("Parent:forward_to_parent")) {
            System.out.println("FAIL: Expected Parent:forward_to_parent in log, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.1.2: Child forwards to parent - PASS (log: " + log + ")");

        // TC1.1.3: Child remains the current state (no transition occurs on forward)
        String state = s.get_state();
        if (!state.equals("Child")) {
            System.out.println("FAIL: Expected state 'Child', got '" + state + "'");
            System.exit(1);
        }
        System.out.println("TC1.1.3: Child remains current state after forward - PASS");

        // TC1.1.4: Parent handler executes and returns control
        if (!log.contains("Child:after_forward")) {
            System.out.println("FAIL: Expected Child:after_forward in log (after parent), got " + log);
            System.exit(1);
        }
        int idx_parent = log.indexOf("Parent:forward_to_parent");
        int idx_after = log.indexOf("Child:after_forward");
        if (idx_after <= idx_parent) {
            System.out.println("FAIL: Expected Child:after_forward after Parent handler");
            System.exit(1);
        }
        System.out.println("TC1.1.4: Parent executes and returns control - PASS");

        // TC1.1.5: Child-only event not forwarded
        s.child_only();
        log = s.get_log();
        int count = 0;
        for (Object item : log) {
            if (item.equals("Child:child_only")) count++;
        }
        if (count != 1) {
            System.out.println("FAIL: Expected exactly 1 Child:child_only, got " + log);
            System.exit(1);
        }
        System.out.println("TC1.1.5: Child-only event handled locally - PASS");

        System.out.println("PASS: HSM single parent relationship works correctly");
    }
}
