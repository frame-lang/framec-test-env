from typing import Any, Optional, List, Dict, Callable

class OperationsTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class OperationsTestFrameContext:
    def __init__(self, event: OperationsTestFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class OperationsTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'OperationsTestCompartment':
        c = OperationsTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class OperationsTest:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.last_result = 0
        self.__compartment = OperationsTestCompartment("Ready")
        self.__next_compartment = None
        __frame_event = OperationsTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = OperationsTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = OperationsTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = OperationsTestFrameEvent("$>", self.__compartment.enter_args)
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

    def compute(self, a: int, b: int) -> int:
        __e = OperationsTestFrameEvent("compute", {"a": a, "b": b})
        __ctx = OperationsTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_last_result(self) -> int:
        __e = OperationsTestFrameEvent("get_last_result", None)
        __ctx = OperationsTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Ready(self, __e):
        if __e._message == "compute":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            # Use instance operations
            sum_val = self.add(a, b)
            prod_val = self.multiply(a, b)
            last_result = sum_val + prod_val
            self._context_stack[-1]._return = last_result
            return
        elif __e._message == "get_last_result":
            self._context_stack[-1]._return = last_result
            return

    def add(self, x: int, y: int) -> int:
        return x + y

    def multiply(self, x: int, y: int) -> int:
        return x * y

    @staticmethod
    def factorial(n: int) -> int:
        if n <= 1:
            return 1
        return n * OperationsTest.factorial(n - 1)

    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0


def main():
    print("=== Test 22: Operations Basic ===")
    s = OperationsTest()

    # Test 1: Instance operations
    result = s.add(3, 4)
    assert result == 7, f"Expected 7, got {result}"
    print(f"1. add(3, 4) = {result}")

    result = s.multiply(3, 4)
    assert result == 12, f"Expected 12, got {result}"
    print(f"2. multiply(3, 4) = {result}")

    # Test 2: Operations used in handler
    result = s.compute(3, 4)
    # compute returns add(3,4) + multiply(3,4) = 7 + 12 = 19
    assert result == 19, f"Expected 19, got {result}"
    print(f"3. compute(3, 4) = {result}")

    # Test 3: Static operations
    result = OperationsTest.factorial(5)
    assert result == 120, f"Expected 120, got {result}"
    print(f"4. factorial(5) = {result}")

    result = OperationsTest.is_even(4)
    assert result == True, f"Expected True, got {result}"
    print(f"5. is_even(4) = {result}")

    result = OperationsTest.is_even(7)
    assert result == False, f"Expected False, got {result}"
    print(f"6. is_even(7) = {result}")

    # Test 4: Static can also be called on instance
    result = s.factorial(4)
    assert result == 24, f"Expected 24, got {result}"
    print(f"7. instance.factorial(4) = {result}")

    print("PASS: Operations basic works correctly")

if __name__ == '__main__':
    main()
