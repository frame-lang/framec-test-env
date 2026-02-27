from typing import Any, Optional, List, Dict, Callable

class SystemReturnTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class SystemReturnTestFrameContext:
    def __init__(self, event: SystemReturnTestFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class SystemReturnTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'SystemReturnTestCompartment':
        c = SystemReturnTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class SystemReturnTest:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = SystemReturnTestCompartment("Calculator")
        self.__next_compartment = None
        __frame_event = SystemReturnTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = SystemReturnTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = SystemReturnTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = SystemReturnTestFrameEvent("$>", self.__compartment.enter_args)
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

    def add(self, a: int, b: int) -> int:
        __e = SystemReturnTestFrameEvent("add", {"a": a, "b": b})
        __ctx = SystemReturnTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def multiply(self, a: int, b: int) -> int:
        __e = SystemReturnTestFrameEvent("multiply", {"a": a, "b": b})
        __ctx = SystemReturnTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def greet(self, name: str) -> str:
        __e = SystemReturnTestFrameEvent("greet", {"name": name})
        __ctx = SystemReturnTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_value(self) -> int:
        __e = SystemReturnTestFrameEvent("get_value", None)
        __ctx = SystemReturnTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Calculator(self, __e):
        if __e._message == "$>":
            if "value" not in self.__compartment.state_vars:
                self.__compartment.state_vars["value"] = 0
        elif __e._message == "add":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            self._context_stack[-1]._return = a + b
            return
        elif __e._message == "get_value":
            self.__compartment.state_vars["value"] = 42
            self._context_stack[-1]._return = self.__compartment.state_vars["value"]
            return
        elif __e._message == "greet":
            name = __e._parameters["name"]
            self._context_stack[-1]._return = "Hello, " + name + "!"
            return
        elif __e._message == "multiply":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            self._context_stack[-1]._return = a * b


def main():
    print("=== Test 13: System Return ===")
    calc = SystemReturnTest()

    # Test return sugar
    result = calc.add(3, 5)
    assert result == 8, f"Expected 8, got {result}"
    print(f"add(3, 5) = {result}")

    # Test system.return = expr
    result = calc.multiply(4, 7)
    assert result == 28, f"Expected 28, got {result}"
    print(f"multiply(4, 7) = {result}")

    # Test string return
    greeting = calc.greet("World")
    assert greeting == "Hello, World!", f"Expected 'Hello, World!', got '{greeting}'"
    print(f"greet('World') = {greeting}")

    # Test return with state variable
    value = calc.get_value()
    assert value == 42, f"Expected 42, got {value}"
    print(f"get_value() = {value}")

    print("PASS: System return works correctly")

if __name__ == '__main__':
    main()
