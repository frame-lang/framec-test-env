
# Test: Context Stack Reentrancy
# Validates that nested interface calls maintain separate contexts


from typing import Any, Optional, List, Dict, Callable

class ContextReentrantTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class ContextReentrantTestFrameContext:
    def __init__(self, event: ContextReentrantTestFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class ContextReentrantTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'ContextReentrantTestCompartment':
        c = ContextReentrantTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class ContextReentrantTest:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = ContextReentrantTestCompartment("Ready")
        self.__next_compartment = None
        __frame_event = ContextReentrantTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = ContextReentrantTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = ContextReentrantTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = ContextReentrantTestFrameEvent("$>", self.__compartment.enter_args)
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

    def outer(self, x: int) -> str:
        __e = ContextReentrantTestFrameEvent("outer", {"x": x})
        __ctx = ContextReentrantTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def inner(self, y: int) -> str:
        __e = ContextReentrantTestFrameEvent("inner", {"y": y})
        __ctx = ContextReentrantTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def deeply_nested(self, z: int) -> str:
        __e = ContextReentrantTestFrameEvent("deeply_nested", {"z": z})
        __ctx = ContextReentrantTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_both(self, a: int, b: int) -> str:
        __e = ContextReentrantTestFrameEvent("get_both", {"a": a, "b": b})
        __ctx = ContextReentrantTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Ready(self, __e):
        if __e._message == "deeply_nested":
            z = __e._parameters["z"]
            # 3 levels deep
            outer_result = self.outer(self._context_stack[-1].event._parameters["z"])
            self._context_stack[-1]._return = "deep:" + str(self._context_stack[-1].event._parameters["z"]) + "," + outer_result
        elif __e._message == "get_both":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            # Test that we can access multiple params
            result_a = self.inner(self._context_stack[-1].event._parameters["a"])
            result_b = self.inner(self._context_stack[-1].event._parameters["b"])
            # After both inner calls, @@.a and @@.b should still be our params
            self._context_stack[-1]._return = "a=" + str(self._context_stack[-1].event._parameters["a"]) + ",b=" + str(self._context_stack[-1].event._parameters["b"]) + ",results=" + result_a + "+" + result_b
        elif __e._message == "inner":
            y = __e._parameters["y"]
            # Inner has its own context
            # @@.y should be inner's param, not outer's
            self._context_stack[-1]._return = str(self._context_stack[-1].event._parameters["y"])
        elif __e._message == "outer":
            x = __e._parameters["x"]
            # Set our return before calling inner
            self._context_stack[-1]._return = "outer_initial"

            # Call inner - should NOT clobber our return
            inner_result = self.inner(self._context_stack[-1].event._parameters["x"] * 10)

            # Our return should still be accessible
            # Update it with combined result
            self._context_stack[-1]._return = "outer:" + str(self._context_stack[-1].event._parameters["x"]) + ",inner:" + inner_result


def main():
    print("=== Test 37: Context Reentrant ===")
    s = ContextReentrantTest()

    # Test 1: Simple nesting - outer calls inner
    result = s.outer(5)
    expected = "outer:5,inner:50"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"1. outer(5) = '{result}'")

    # Test 2: Inner alone
    result = s.inner(42)
    assert result == "42", f"Expected '42', got '{result}'"
    print(f"2. inner(42) = '{result}'")

    # Test 3: Deep nesting (3 levels)
    result = s.deeply_nested(3)
    expected = "deep:3,outer:3,inner:30"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"3. deeply_nested(3) = '{result}'")

    # Test 4: Multiple inner calls, params preserved
    result = s.get_both(10, 20)
    expected = "a=10,b=20,results=10+20"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"4. get_both(10, 20) = '{result}'")

    print("PASS: Context reentrant works correctly")

if __name__ == '__main__':
    main()
