import java.util.*;


import java.util.*;

// Tests that @@:return follows "last writer wins" across transition lifecycle

class SystemReturnChainTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    SystemReturnChainTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    SystemReturnChainTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnChainTestFrameContext {
    SystemReturnChainTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    SystemReturnChainTestFrameContext(SystemReturnChainTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class SystemReturnChainTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    SystemReturnChainTestFrameEvent forward_event;
    SystemReturnChainTestCompartment parent_compartment;

    SystemReturnChainTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    SystemReturnChainTestCompartment copy() {
        SystemReturnChainTestCompartment c = new SystemReturnChainTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnChainTest {
    private ArrayList<SystemReturnChainTestCompartment> _state_stack;
    private SystemReturnChainTestCompartment __compartment;
    private SystemReturnChainTestCompartment __next_compartment;
    private ArrayList<SystemReturnChainTestFrameContext> _context_stack;

    public SystemReturnChainTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new SystemReturnChainTestCompartment("Start");
        __next_compartment = null;
        SystemReturnChainTestFrameEvent __frame_event = new SystemReturnChainTestFrameEvent("$>");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(SystemReturnChainTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            SystemReturnChainTestFrameEvent exit_event = new SystemReturnChainTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                SystemReturnChainTestFrameEvent enter_event = new SystemReturnChainTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    SystemReturnChainTestFrameEvent enter_event = new SystemReturnChainTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(SystemReturnChainTestFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("EnterSetter")) {
            _state_EnterSetter(__e);
        } else if (state_name.equals("BothSet")) {
            _state_BothSet(__e);
        }
    }

    private void __transition(SystemReturnChainTestCompartment next) {
        __next_compartment = next;
    }

    public String test_enter_sets() {
        SystemReturnChainTestFrameEvent __e = new SystemReturnChainTestFrameEvent("test_enter_sets");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String test_exit_then_enter() {
        SystemReturnChainTestFrameEvent __e = new SystemReturnChainTestFrameEvent("test_exit_then_enter");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        SystemReturnChainTestFrameEvent __e = new SystemReturnChainTestFrameEvent("get_state");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Start(SystemReturnChainTestFrameEvent __e) {
        if (__e._message.equals("<$")) {
            // Exit handler sets initial value
            _context_stack.get(_context_stack.size() - 1)._return = "from_exit";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Start";
            return;
        } else if (__e._message.equals("test_enter_sets")) {
            var __compartment = new SystemReturnChainTestCompartment("EnterSetter");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("test_exit_then_enter")) {
            var __compartment = new SystemReturnChainTestCompartment("BothSet");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_EnterSetter(SystemReturnChainTestFrameEvent __e) {
        if (__e._message.equals("$>")) {
            // Enter handler sets return value
            _context_stack.get(_context_stack.size() - 1)._return = "from_enter";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "EnterSetter";
            return;
        }
    }

    private void _state_BothSet(SystemReturnChainTestFrameEvent __e) {
        if (__e._message.equals("$>")) {
            // Enter handler sets return - should overwrite exit's value
            _context_stack.get(_context_stack.size() - 1)._return = "enter_wins";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "BothSet";
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 15: System Return Chain (Last Writer Wins) ===");

        // Test 1: Start exit + EnterSetter enter
        // Start's exit sets "from_exit", EnterSetter's enter sets "from_enter"
        // Enter should win (last writer)
        var s1 = new SystemReturnChainTest();
        String result1 = (String) s1.test_enter_sets();
        if (!"from_enter".equals(result1)) {
            throw new RuntimeException("Expected 'from_enter', got '" + result1 + "'");
        }
        String state1 = (String) s1.get_state();
        if (!"EnterSetter".equals(state1)) {
            throw new RuntimeException("Expected state 'EnterSetter'");
        }
        System.out.println("1. Exit set then enter set - enter wins: '" + result1 + "'");

        // Test 2: Both handlers set, enter wins
        var s2 = new SystemReturnChainTest();
        String result2 = (String) s2.test_exit_then_enter();
        if (!"enter_wins".equals(result2)) {
            throw new RuntimeException("Expected 'enter_wins', got '" + result2 + "'");
        }
        String state2 = (String) s2.get_state();
        if (!"BothSet".equals(state2)) {
            throw new RuntimeException("Expected state 'BothSet'");
        }
        System.out.println("2. Both set - enter wins: '" + result2 + "'");

        System.out.println("PASS: System return chain (last writer wins) works correctly");
    }
}
