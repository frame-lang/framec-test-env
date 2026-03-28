using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// =============================================================================
// Test 01: Interface Return
// =============================================================================
// Validates that event handler returns work correctly via the context stack.
// Tests both syntaxes:
//   - return value     (sugar - expands to @@:return = value)
//   - @@:return = value (explicit context assignment)
// =============================================================================

class InterfaceReturnFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public InterfaceReturnFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public InterfaceReturnFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class InterfaceReturnFrameContext {
    public InterfaceReturnFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public InterfaceReturnFrameContext(InterfaceReturnFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class InterfaceReturnCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public InterfaceReturnFrameEvent forward_event;
    public InterfaceReturnCompartment parent_compartment;

    public InterfaceReturnCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public InterfaceReturnCompartment Copy() {
        InterfaceReturnCompartment c = new InterfaceReturnCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class InterfaceReturn {
    private List<InterfaceReturnCompartment> _state_stack;
    private InterfaceReturnCompartment __compartment;
    private InterfaceReturnCompartment __next_compartment;
    private List<InterfaceReturnFrameContext> _context_stack;

    public InterfaceReturn() {
        _state_stack = new List<InterfaceReturnCompartment>();
        _context_stack = new List<InterfaceReturnFrameContext>();
        __compartment = new InterfaceReturnCompartment("Active");
        __next_compartment = null;
        InterfaceReturnFrameEvent __frame_event = new InterfaceReturnFrameEvent("$>");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(InterfaceReturnFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            InterfaceReturnFrameEvent exit_event = new InterfaceReturnFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                InterfaceReturnFrameEvent enter_event = new InterfaceReturnFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    InterfaceReturnFrameEvent enter_event = new InterfaceReturnFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(InterfaceReturnFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    private void __transition(InterfaceReturnCompartment next) {
        __next_compartment = next;
    }

    public bool bool_return() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("bool_return");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int int_return() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("int_return");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string string_return() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("string_return");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string conditional_return(int x) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["x"] = x;
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("conditional_return", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int computed_return(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("computed_return", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public bool explicit_bool() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_bool");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int explicit_int() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_int");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string explicit_string() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_string");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string explicit_conditional(int x) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["x"] = x;
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_conditional", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int explicit_computed(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_computed", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Active(InterfaceReturnFrameEvent __e) {
        if (__e._message == "bool_return") {
            _context_stack[_context_stack.Count - 1]._return = true;
            return;
        } else if (__e._message == "computed_return") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            int result = a * b + 10;
            _context_stack[_context_stack.Count - 1]._return = result;
            return;
        } else if (__e._message == "conditional_return") {
            var x = (int) __e._parameters["x"];
            if (x < 0) {
                _context_stack[_context_stack.Count - 1]._return = "negative";
                return;
            } else if (x == 0) {
                _context_stack[_context_stack.Count - 1]._return = "zero";
                return;
            } else {
                _context_stack[_context_stack.Count - 1]._return = "positive";
                return;
            }
        } else if (__e._message == "explicit_bool") {
            _context_stack[_context_stack.Count - 1]._return = true;
        } else if (__e._message == "explicit_computed") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            int result = a * b + 10;
            _context_stack[_context_stack.Count - 1]._return = result;
        } else if (__e._message == "explicit_conditional") {
            var x = (int) __e._parameters["x"];
            if (x < 0) {
                _context_stack[_context_stack.Count - 1]._return = "negative";
                return;
            } else if (x == 0) {
                _context_stack[_context_stack.Count - 1]._return = "zero";
                return;
            } else {
                _context_stack[_context_stack.Count - 1]._return = "positive";
            }
        } else if (__e._message == "explicit_int") {
            _context_stack[_context_stack.Count - 1]._return = 42;
        } else if (__e._message == "explicit_string") {
            _context_stack[_context_stack.Count - 1]._return = "Frame";
        } else if (__e._message == "int_return") {
            _context_stack[_context_stack.Count - 1]._return = 42;
            return;
        } else if (__e._message == "string_return") {
            _context_stack[_context_stack.Count - 1]._return = "Frame";
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 01: Interface Return (C#) ===");
        var s = new InterfaceReturn();
        var errors = new List<string>();

        Console.WriteLine("-- Testing 'return value' sugar --");

        var r1 = (bool)s.bool_return();
        if (r1 != true) {
            errors.Add("bool_return: expected true, got " + r1);
        } else {
            Console.WriteLine("1. bool_return() = " + r1);
        }

        var r2 = (int)s.int_return();
        if (r2 != 42) {
            errors.Add("int_return: expected 42, got " + r2);
        } else {
            Console.WriteLine("2. int_return() = " + r2);
        }

        var r3 = (string)s.string_return();
        if (r3 != "Frame") {
            errors.Add("string_return: expected 'Frame', got '" + r3 + "'");
        } else {
            Console.WriteLine("3. string_return() = '" + r3 + "'");
        }

        var r4 = (string)s.conditional_return(-5);
        if (r4 != "negative") {
            errors.Add("conditional_return(-5): expected 'negative', got '" + r4 + "'");
        }
        r4 = (string)s.conditional_return(0);
        if (r4 != "zero") {
            errors.Add("conditional_return(0): expected 'zero', got '" + r4 + "'");
        }
        r4 = (string)s.conditional_return(10);
        if (r4 != "positive") {
            errors.Add("conditional_return(10): expected 'positive', got '" + r4 + "'");
        } else {
            Console.WriteLine("4. conditional_return(-5,0,10) = 'negative','zero','positive'");
        }

        var r5 = (int)s.computed_return(3, 4);
        if (r5 != 22) {
            errors.Add("computed_return(3,4): expected 22, got " + r5);
        } else {
            Console.WriteLine("5. computed_return(3,4) = " + r5);
        }

        Console.WriteLine("-- Testing '@@:return = value' explicit --");

        var r6 = (bool)s.explicit_bool();
        if (r6 != true) {
            errors.Add("explicit_bool: expected true, got " + r6);
        } else {
            Console.WriteLine("6. explicit_bool() = " + r6);
        }

        var r7 = (int)s.explicit_int();
        if (r7 != 42) {
            errors.Add("explicit_int: expected 42, got " + r7);
        } else {
            Console.WriteLine("7. explicit_int() = " + r7);
        }

        var r8 = (string)s.explicit_string();
        if (r8 != "Frame") {
            errors.Add("explicit_string: expected 'Frame', got '" + r8 + "'");
        } else {
            Console.WriteLine("8. explicit_string() = '" + r8 + "'");
        }

        var r9 = (string)s.explicit_conditional(-5);
        if (r9 != "negative") {
            errors.Add("explicit_conditional(-5): expected 'negative', got '" + r9 + "'");
        }
        r9 = (string)s.explicit_conditional(0);
        if (r9 != "zero") {
            errors.Add("explicit_conditional(0): expected 'zero', got '" + r9 + "'");
        }
        r9 = (string)s.explicit_conditional(10);
        if (r9 != "positive") {
            errors.Add("explicit_conditional(10): expected 'positive', got '" + r9 + "'");
        } else {
            Console.WriteLine("9. explicit_conditional(-5,0,10) = 'negative','zero','positive'");
        }

        var r10 = (int)s.explicit_computed(3, 4);
        if (r10 != 22) {
            errors.Add("explicit_computed(3,4): expected 22, got " + r10);
        } else {
            Console.WriteLine("10. explicit_computed(3,4) = " + r10);
        }

        if (errors.Count > 0) {
            foreach (var e in errors) {
                Console.WriteLine("FAIL: " + e);
            }
            throw new Exception(errors.Count + " test(s) failed");
        } else {
            Console.WriteLine("PASS: All interface return tests passed");
        }
    }
}
