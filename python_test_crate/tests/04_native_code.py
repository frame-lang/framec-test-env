
import math

def helper_function(x):
    """Native helper function defined before system"""
    return x * 2


from typing import Any, Optional, List, Dict, Callable

class NativeCodeFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class NativeCodeCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'NativeCodeCompartment':
        c = NativeCodeCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class NativeCode:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = NativeCodeCompartment("Active")
        self.__next_compartment = None
        __frame_event = NativeCodeFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = NativeCodeFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = NativeCodeFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = NativeCodeFrameEvent("$>", self.__compartment.enter_args)
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

    def compute(self, value: int) -> int:
        self._return_value = None
        __e = NativeCodeFrameEvent("compute", {"0": value})
        self.__kernel(__e)
        return self._return_value

    def use_math(self) -> float:
        self._return_value = None
        __e = NativeCodeFrameEvent("use_math", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Active(self, __e):
        if __e._message == "compute":
            value = __e._parameters["0"]
            # Native code with local variables
            temp = value + 10
            result = helper_function(temp)
            print(f"Computed: {value} -> {result}")
            self._return_value = result
            __e._return = self._return_value
            return
        elif __e._message == "use_math":
            # Using imported math module
            result = math.sqrt(16) + math.pi
            print(f"Math result: {result}")
            self._return_value = result
            __e._return = self._return_value
            return


def main():
    print("=== Test 04: Native Code Preservation ===")
    s = NativeCode()

    # Test native code in handler with helper function
    result = s.compute(5)
    expected = (5 + 10) * 2  # 30
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"compute(5) = {result}")

    # Test imported module usage
    math_result = s.use_math()
    expected_math = math.sqrt(16) + math.pi
    assert abs(math_result - expected_math) < 0.001, f"Expected ~{expected_math}, got {math_result}"
    print(f"use_math() = {math_result}")

    print("PASS: Native code preservation works correctly")

if __name__ == '__main__':
    main()
