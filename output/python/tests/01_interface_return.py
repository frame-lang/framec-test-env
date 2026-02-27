
# =============================================================================
# Test 01: Interface Return
# =============================================================================
# Validates that event handler returns work correctly via the context stack.
# Tests both syntaxes:
#   - return value     (sugar - expands to @@:return = value)
#   - @@:return = value (explicit context assignment)
# =============================================================================


from typing import Any, Optional, List, Dict, Callable

class InterfaceReturnFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class InterfaceReturnFrameContext:
    def __init__(self, event: InterfaceReturnFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class InterfaceReturnCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'InterfaceReturnCompartment':
        c = InterfaceReturnCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class InterfaceReturn:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = InterfaceReturnCompartment("Active")
        self.__next_compartment = None
        __frame_event = InterfaceReturnFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = InterfaceReturnFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = InterfaceReturnFrameEvent("$>", self.__compartment.enter_args)
                self.__router(enter_event)
            else:
                # Forward event to new state
                forward_event = next_compartment.forward_event
                next_compartment.forward_event = None
                if forward_event._message == "$>":
                    # Forwarding enter event - just send it
                    self.__router(forward_event)
                else:
                    # Forwarding other event - send $> first, then forward
                    enter_event = InterfaceReturnFrameEvent("$>", self.__compartment.enter_args)
                    self.__router(enter_event)
                    self.__router(forward_event)

    def __router(self, __e):
        state_name = self.__compartment.state
        handler_name = f"_state_{state_name}"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(__e)

    def __transition(self, next_compartment):
        self.__next_compartment = next_compartment

    def bool_return(self) -> bool:
        __e = InterfaceReturnFrameEvent("bool_return", None)
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def int_return(self) -> int:
        __e = InterfaceReturnFrameEvent("int_return", None)
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def string_return(self) -> str:
        __e = InterfaceReturnFrameEvent("string_return", None)
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def conditional_return(self, x: int) -> str:
        __e = InterfaceReturnFrameEvent("conditional_return", {"x": x})
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def computed_return(self, a: int, b: int) -> int:
        __e = InterfaceReturnFrameEvent("computed_return", {"a": a, "b": b})
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def explicit_bool(self) -> bool:
        __e = InterfaceReturnFrameEvent("explicit_bool", None)
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def explicit_int(self) -> int:
        __e = InterfaceReturnFrameEvent("explicit_int", None)
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def explicit_string(self) -> str:
        __e = InterfaceReturnFrameEvent("explicit_string", None)
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def explicit_conditional(self, x: int) -> str:
        __e = InterfaceReturnFrameEvent("explicit_conditional", {"x": x})
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def explicit_computed(self, a: int, b: int) -> int:
        __e = InterfaceReturnFrameEvent("explicit_computed", {"a": a, "b": b})
        __ctx = InterfaceReturnFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Active(self, __e):
        if __e._message == "bool_return":
            self._context_stack[-1]._return = True
            return
        elif __e._message == "computed_return":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            result = a * b + 10
            self._context_stack[-1]._return = result
            return
        elif __e._message == "conditional_return":
            x = __e._parameters["x"]
            if x < 0:
                self._context_stack[-1]._return = "negative"
                return
            elif x == 0:
                self._context_stack[-1]._return = "zero"
                return
            else:
                self._context_stack[-1]._return = "positive"
                return
        elif __e._message == "explicit_bool":
            self._context_stack[-1]._return = True
        elif __e._message == "explicit_computed":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            result = a * b + 10
            self._context_stack[-1]._return = result
        elif __e._message == "explicit_conditional":
            x = __e._parameters["x"]
            if x < 0:
                self._context_stack[-1]._return = "negative"
                return
            elif x == 0:
                self._context_stack[-1]._return = "zero"
                return
            else:
                self._context_stack[-1]._return = "positive"
        elif __e._message == "explicit_int":
            self._context_stack[-1]._return = 42
        elif __e._message == "explicit_string":
            self._context_stack[-1]._return = "Frame"
        elif __e._message == "int_return":
            self._context_stack[-1]._return = 42
            return
        elif __e._message == "string_return":
            self._context_stack[-1]._return = "Frame"
            return


def main():
    print("=== Test 01: Interface Return (Python) ===")
    s = InterfaceReturn()
    errors = []

    print("-- Testing 'return value' sugar --")

    r = s.bool_return()
    if r != True:
        errors.append(f"bool_return: expected True, got {r}")
    else:
        print(f"1. bool_return() = {r}")

    r = s.int_return()
    if r != 42:
        errors.append(f"int_return: expected 42, got {r}")
    else:
        print(f"2. int_return() = {r}")

    r = s.string_return()
    if r != "Frame":
        errors.append(f"string_return: expected 'Frame', got '{r}'")
    else:
        print(f"3. string_return() = '{r}'")

    r = s.conditional_return(-5)
    if r != "negative":
        errors.append(f"conditional_return(-5): expected 'negative', got '{r}'")
    r = s.conditional_return(0)
    if r != "zero":
        errors.append(f"conditional_return(0): expected 'zero', got '{r}'")
    r = s.conditional_return(10)
    if r != "positive":
        errors.append(f"conditional_return(10): expected 'positive', got '{r}'")
    else:
        print(f"4. conditional_return(-5,0,10) = 'negative','zero','positive'")

    r = s.computed_return(3, 4)
    if r != 22:
        errors.append(f"computed_return(3,4): expected 22, got {r}")
    else:
        print(f"5. computed_return(3,4) = {r}")

    print("-- Testing '@@:return = value' explicit --")

    r = s.explicit_bool()
    if r != True:
        errors.append(f"explicit_bool: expected True, got {r}")
    else:
        print(f"6. explicit_bool() = {r}")

    r = s.explicit_int()
    if r != 42:
        errors.append(f"explicit_int: expected 42, got {r}")
    else:
        print(f"7. explicit_int() = {r}")

    r = s.explicit_string()
    if r != "Frame":
        errors.append(f"explicit_string: expected 'Frame', got '{r}'")
    else:
        print(f"8. explicit_string() = '{r}'")

    r = s.explicit_conditional(-5)
    if r != "negative":
        errors.append(f"explicit_conditional(-5): expected 'negative', got '{r}'")
    r = s.explicit_conditional(0)
    if r != "zero":
        errors.append(f"explicit_conditional(0): expected 'zero', got '{r}'")
    r = s.explicit_conditional(10)
    if r != "positive":
        errors.append(f"explicit_conditional(10): expected 'positive', got '{r}'")
    else:
        print(f"9. explicit_conditional(-5,0,10) = 'negative','zero','positive'")

    r = s.explicit_computed(3, 4)
    if r != 22:
        errors.append(f"explicit_computed(3,4): expected 22, got {r}")
    else:
        print(f"10. explicit_computed(3,4) = {r}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        raise AssertionError(f"{len(errors)} test(s) failed")
    else:
        print("PASS: All interface return tests passed")

if __name__ == '__main__':
    main()
