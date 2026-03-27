import java.util.*;


import java.util.*;

// =============================================================================
// Test 01: Interface Return
// =============================================================================
// Validates that event handler returns work correctly via the context stack.
// Tests both syntaxes:
//   - return value     (sugar - expands to @@:return = value)
//   - @@:return = value (explicit context assignment)
// =============================================================================

class InterfaceReturnFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    InterfaceReturnFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    InterfaceReturnFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class InterfaceReturnFrameContext {
    InterfaceReturnFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    InterfaceReturnFrameContext(InterfaceReturnFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class InterfaceReturnCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    InterfaceReturnFrameEvent forward_event;
    InterfaceReturnCompartment parent_compartment;

    InterfaceReturnCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    InterfaceReturnCompartment copy() {
        InterfaceReturnCompartment c = new InterfaceReturnCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class InterfaceReturn {
    private ArrayList<InterfaceReturnCompartment> _state_stack;
    private InterfaceReturnCompartment __compartment;
    private InterfaceReturnCompartment __next_compartment;
    private ArrayList<InterfaceReturnFrameContext> _context_stack;

    public InterfaceReturn() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new InterfaceReturnCompartment("Active");
        __next_compartment = null;
        InterfaceReturnFrameEvent __frame_event = new InterfaceReturnFrameEvent("$>");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Active")) {
            _state_Active(__e);
        }
    }

    private void __transition(InterfaceReturnCompartment next) {
        __next_compartment = next;
    }

    public Boolean bool_return() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("bool_return");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (Boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int int_return() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("int_return");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String string_return() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("string_return");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String conditional_return(int x) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("x", x);
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("conditional_return", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int computed_return(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("computed_return", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public Boolean explicit_bool() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_bool");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (Boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int explicit_int() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_int");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String explicit_string() {
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_string");
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String explicit_conditional(int x) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("x", x);
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_conditional", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int explicit_computed(int a, int b) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("a", a);
        __params.put("b", b);
        InterfaceReturnFrameEvent __e = new InterfaceReturnFrameEvent("explicit_computed", __params);
        InterfaceReturnFrameContext __ctx = new InterfaceReturnFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Active(InterfaceReturnFrameEvent __e) {
        if (__e._message.equals("bool_return")) {
            _context_stack.get(_context_stack.size() - 1)._return = true;
            return;
        } else if (__e._message.equals("computed_return")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            int result = a * b + 10;
            _context_stack.get(_context_stack.size() - 1)._return = result;
            return;
        } else if (__e._message.equals("conditional_return")) {
            var x = (int) __e._parameters.get("x");
            if (x < 0) {
                _context_stack.get(_context_stack.size() - 1)._return = "negative";
                return;
            } else if (x == 0) {
                _context_stack.get(_context_stack.size() - 1)._return = "zero";
                return;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = "positive";
                return;
            }
        } else if (__e._message.equals("explicit_bool")) {
            _context_stack.get(_context_stack.size() - 1)._return = true;
        } else if (__e._message.equals("explicit_computed")) {
            var a = (int) __e._parameters.get("a");
            var b = (int) __e._parameters.get("b");
            int result = a * b + 10;
            _context_stack.get(_context_stack.size() - 1)._return = result;
        } else if (__e._message.equals("explicit_conditional")) {
            var x = (int) __e._parameters.get("x");
            if (x < 0) {
                _context_stack.get(_context_stack.size() - 1)._return = "negative";
                return;
            } else if (x == 0) {
                _context_stack.get(_context_stack.size() - 1)._return = "zero";
                return;
            } else {
                _context_stack.get(_context_stack.size() - 1)._return = "positive";
            }
        } else if (__e._message.equals("explicit_int")) {
            _context_stack.get(_context_stack.size() - 1)._return = 42;
        } else if (__e._message.equals("explicit_string")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Frame";
        } else if (__e._message.equals("int_return")) {
            _context_stack.get(_context_stack.size() - 1)._return = 42;
            return;
        } else if (__e._message.equals("string_return")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Frame";
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 01: Interface Return (Java) ===");
        var s = new InterfaceReturn();
        ArrayList<String> errors = new ArrayList<>();

        System.out.println("-- Testing 'return value' sugar --");

        Boolean r1 = s.bool_return();
        if (r1 == null || !r1.equals(true)) {
            errors.add("bool_return: expected true, got " + r1);
        } else {
            System.out.println("1. bool_return() = " + r1);
        }

        int r2 = (int) s.int_return();
        if (r2 != 42) {
            errors.add("int_return: expected 42, got " + r2);
        } else {
            System.out.println("2. int_return() = " + r2);
        }

        String r3 = (String) s.string_return();
        if (!"Frame".equals(r3)) {
            errors.add("string_return: expected 'Frame', got '" + r3 + "'");
        } else {
            System.out.println("3. string_return() = '" + r3 + "'");
        }

        String r4 = (String) s.conditional_return(-5);
        if (!"negative".equals(r4)) {
            errors.add("conditional_return(-5): expected 'negative', got '" + r4 + "'");
        }
        r4 = (String) s.conditional_return(0);
        if (!"zero".equals(r4)) {
            errors.add("conditional_return(0): expected 'zero', got '" + r4 + "'");
        }
        r4 = (String) s.conditional_return(10);
        if (!"positive".equals(r4)) {
            errors.add("conditional_return(10): expected 'positive', got '" + r4 + "'");
        } else {
            System.out.println("4. conditional_return(-5,0,10) = 'negative','zero','positive'");
        }

        int r5 = (int) s.computed_return(3, 4);
        if (r5 != 22) {
            errors.add("computed_return(3,4): expected 22, got " + r5);
        } else {
            System.out.println("5. computed_return(3,4) = " + r5);
        }

        System.out.println("-- Testing '@@:return = value' explicit --");

        Boolean r6 = s.explicit_bool();
        if (r6 == null || !r6.equals(true)) {
            errors.add("explicit_bool: expected true, got " + r6);
        } else {
            System.out.println("6. explicit_bool() = " + r6);
        }

        int r7 = (int) s.explicit_int();
        if (r7 != 42) {
            errors.add("explicit_int: expected 42, got " + r7);
        } else {
            System.out.println("7. explicit_int() = " + r7);
        }

        String r8 = (String) s.explicit_string();
        if (!"Frame".equals(r8)) {
            errors.add("explicit_string: expected 'Frame', got '" + r8 + "'");
        } else {
            System.out.println("8. explicit_string() = '" + r8 + "'");
        }

        String r9 = (String) s.explicit_conditional(-5);
        if (!"negative".equals(r9)) {
            errors.add("explicit_conditional(-5): expected 'negative', got '" + r9 + "'");
        }
        r9 = (String) s.explicit_conditional(0);
        if (!"zero".equals(r9)) {
            errors.add("explicit_conditional(0): expected 'zero', got '" + r9 + "'");
        }
        r9 = (String) s.explicit_conditional(10);
        if (!"positive".equals(r9)) {
            errors.add("explicit_conditional(10): expected 'positive', got '" + r9 + "'");
        } else {
            System.out.println("9. explicit_conditional(-5,0,10) = 'negative','zero','positive'");
        }

        int r10 = (int) s.explicit_computed(3, 4);
        if (r10 != 22) {
            errors.add("explicit_computed(3,4): expected 22, got " + r10);
        } else {
            System.out.println("10. explicit_computed(3,4) = " + r10);
        }

        if (errors.size() > 0) {
            for (String e : errors) {
                System.out.println("FAIL: " + e);
            }
            throw new RuntimeException(errors.size() + " test(s) failed");
        } else {
            System.out.println("PASS: All interface return tests passed");
        }
    }
}
