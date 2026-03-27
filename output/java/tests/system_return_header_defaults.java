import java.util.*;


import java.util.*;

// capability: @@:return header defaults and handler returns (Java).

class SystemReturnHeaderDefaultsJavaFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SystemReturnHeaderDefaultsJavaFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SystemReturnHeaderDefaultsJavaFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnHeaderDefaultsJavaFrameContext {
    SystemReturnHeaderDefaultsJavaFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SystemReturnHeaderDefaultsJavaFrameContext(SystemReturnHeaderDefaultsJavaFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SystemReturnHeaderDefaultsJavaCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SystemReturnHeaderDefaultsJavaFrameEvent forward_event;
    SystemReturnHeaderDefaultsJavaCompartment parent_compartment;

    SystemReturnHeaderDefaultsJavaCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SystemReturnHeaderDefaultsJavaCompartment copy() {
        SystemReturnHeaderDefaultsJavaCompartment c = new SystemReturnHeaderDefaultsJavaCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnHeaderDefaultsJava {
    private ArrayList<SystemReturnHeaderDefaultsJavaCompartment> _state_stack;
    private SystemReturnHeaderDefaultsJavaCompartment __compartment;
    private SystemReturnHeaderDefaultsJavaCompartment __next_compartment;
    private ArrayList<SystemReturnHeaderDefaultsJavaFrameContext> _context_stack;
    public int x = 3;

    public SystemReturnHeaderDefaultsJava() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SystemReturnHeaderDefaultsJavaCompartment("Idle");
        __next_compartment = null;
        SystemReturnHeaderDefaultsJavaFrameEvent __frame_event = new SystemReturnHeaderDefaultsJavaFrameEvent("$>");
        SystemReturnHeaderDefaultsJavaFrameContext __ctx = new SystemReturnHeaderDefaultsJavaFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SystemReturnHeaderDefaultsJavaFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnHeaderDefaultsJavaFrameEvent exit_event = new SystemReturnHeaderDefaultsJavaFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnHeaderDefaultsJavaFrameEvent enter_event = new SystemReturnHeaderDefaultsJavaFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SystemReturnHeaderDefaultsJavaFrameEvent enter_event = new SystemReturnHeaderDefaultsJavaFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnHeaderDefaultsJavaFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        }
    }

    private void __transition(SystemReturnHeaderDefaultsJavaCompartment next) {
        __next_compartment = next;
    }

    public int a1() {
        SystemReturnHeaderDefaultsJavaFrameEvent __e = new SystemReturnHeaderDefaultsJavaFrameEvent("a1");
        SystemReturnHeaderDefaultsJavaFrameContext __ctx = new SystemReturnHeaderDefaultsJavaFrameContext(__e, 10);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int a2(int a) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        SystemReturnHeaderDefaultsJavaFrameEvent __e = new SystemReturnHeaderDefaultsJavaFrameEvent("a2", __params);
        SystemReturnHeaderDefaultsJavaFrameContext __ctx = new SystemReturnHeaderDefaultsJavaFrameContext(__e, a);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int a3(int a) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        SystemReturnHeaderDefaultsJavaFrameEvent __e = new SystemReturnHeaderDefaultsJavaFrameEvent("a3", __params);
        SystemReturnHeaderDefaultsJavaFrameContext __ctx = new SystemReturnHeaderDefaultsJavaFrameContext(__e, x + a);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Idle(SystemReturnHeaderDefaultsJavaFrameEvent __e) {
        if (__e._message.equals("a1")) {
            if (x < 5) {
                return;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = 0;
                return;
            }
        } else if (__e._message.equals("a2")) {
            var a = (int) __e._parameters.get("a");
            return;
        } else if (__e._message.equals("a3")) {
            var a = (int) __e._parameters.get("a");
            _context_stack.get(_context_stack.size() - 1)._return = a;
            return;
        }
    }

    private void bump_x(int delta) {
                    x = x + delta;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..1");
        try {
            var s = new SystemReturnHeaderDefaultsJava();
            if (s.a1() != 10) { System.out.println("not ok 1 # a1 failed"); return; }
            if (s.a2(42) != 42) { System.out.println("not ok 1 # a2 failed"); return; }
            if (s.a3(7) != 7) { System.out.println("not ok 1 # a3 failed"); return; }
            System.out.println("ok 1 - system_return_header_defaults");
        } catch (Exception ex) {
            System.out.println("not ok 1 - system_return_header_defaults # " + ex);
        }
    }
}
