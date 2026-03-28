using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// Tests that @@:return follows "last writer wins" across transition lifecycle

class SystemReturnChainTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public SystemReturnChainTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public SystemReturnChainTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class SystemReturnChainTestFrameContext {
    public SystemReturnChainTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public SystemReturnChainTestFrameContext(SystemReturnChainTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class SystemReturnChainTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public SystemReturnChainTestFrameEvent forward_event;
    public SystemReturnChainTestCompartment parent_compartment;

    public SystemReturnChainTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public SystemReturnChainTestCompartment Copy() {
        SystemReturnChainTestCompartment c = new SystemReturnChainTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class SystemReturnChainTest {
    private List<SystemReturnChainTestCompartment> _state_stack;
    private SystemReturnChainTestCompartment __compartment;
    private SystemReturnChainTestCompartment __next_compartment;
    private List<SystemReturnChainTestFrameContext> _context_stack;

    public SystemReturnChainTest() {
        _state_stack = new List<SystemReturnChainTestCompartment>();
        _context_stack = new List<SystemReturnChainTestFrameContext>();
        __compartment = new SystemReturnChainTestCompartment("Start");
        __next_compartment = null;
        SystemReturnChainTestFrameEvent __frame_event = new SystemReturnChainTestFrameEvent("$>");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
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
                if (forward_event._message == "$>") {
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
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "EnterSetter") {
            _state_EnterSetter(__e);
        } else if (state_name == "BothSet") {
            _state_BothSet(__e);
        }
    }

    private void __transition(SystemReturnChainTestCompartment next) {
        __next_compartment = next;
    }

    public string test_enter_sets() {
        SystemReturnChainTestFrameEvent __e = new SystemReturnChainTestFrameEvent("test_enter_sets");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string test_exit_then_enter() {
        SystemReturnChainTestFrameEvent __e = new SystemReturnChainTestFrameEvent("test_exit_then_enter");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        SystemReturnChainTestFrameEvent __e = new SystemReturnChainTestFrameEvent("get_state");
        SystemReturnChainTestFrameContext __ctx = new SystemReturnChainTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Start(SystemReturnChainTestFrameEvent __e) {
        if (__e._message == "<$") {
            // Exit handler sets initial value
            _context_stack[_context_stack.Count - 1]._return = "from_exit";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Start";
            return;
        } else if (__e._message == "test_enter_sets") {
            { var __new_compartment = new SystemReturnChainTestCompartment("EnterSetter");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "test_exit_then_enter") {
            { var __new_compartment = new SystemReturnChainTestCompartment("BothSet");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_EnterSetter(SystemReturnChainTestFrameEvent __e) {
        if (__e._message == "$>") {
            // Enter handler sets return value
            _context_stack[_context_stack.Count - 1]._return = "from_enter";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "EnterSetter";
            return;
        }
    }

    private void _state_BothSet(SystemReturnChainTestFrameEvent __e) {
        if (__e._message == "$>") {
            // Enter handler sets return - should overwrite exit's value
            _context_stack[_context_stack.Count - 1]._return = "enter_wins";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "BothSet";
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 15: System Return Chain (Last Writer Wins) ===");

        // Test 1: Start exit + EnterSetter enter
        // Start's exit sets "from_exit", EnterSetter's enter sets "from_enter"
        // Enter should win (last writer)
        var s1 = new SystemReturnChainTest();
        var result1 = (string)s1.test_enter_sets();
        if (result1 != "from_enter") {
            throw new Exception("Expected 'from_enter', got '" + result1 + "'");
        }
        var state1 = (string)s1.get_state();
        if (state1 != "EnterSetter") {
            throw new Exception("Expected state 'EnterSetter'");
        }
        Console.WriteLine("1. Exit set then enter set - enter wins: '" + result1 + "'");

        // Test 2: Both handlers set, enter wins
        var s2 = new SystemReturnChainTest();
        var result2 = (string)s2.test_exit_then_enter();
        if (result2 != "enter_wins") {
            throw new Exception("Expected 'enter_wins', got '" + result2 + "'");
        }
        var state2 = (string)s2.get_state();
        if (state2 != "BothSet") {
            throw new Exception("Expected state 'BothSet'");
        }
        Console.WriteLine("2. Both set - enter wins: '" + result2 + "'");

        Console.WriteLine("PASS: System return chain (last writer wins) works correctly");
    }
}
