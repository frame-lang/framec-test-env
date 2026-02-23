from typing import Any, Optional, List, Dict, Callable

class WithParamsFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class WithParamsFrameContext:
    def __init__(self, event: WithParamsFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class WithParamsCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'WithParamsCompartment':
        c = WithParamsCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class WithParams:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.total = 0
        self.__compartment = WithParamsCompartment("Idle")
        self.__next_compartment = None
        __frame_event = WithParamsFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = WithParamsFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = WithParamsFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = WithParamsFrameEvent("$>", self.__compartment.enter_args)
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

    def start(self, initial: int):
        __e = WithParamsFrameEvent("start", {"initial": initial})
        __ctx = WithParamsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def add(self, value: int):
        __e = WithParamsFrameEvent("add", {"value": value})
        __ctx = WithParamsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def multiply(self, a: int, b: int) -> int:
        __e = WithParamsFrameEvent("multiply", {"a": a, "b": b})
        __ctx = WithParamsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_total(self) -> int:
        __e = WithParamsFrameEvent("get_total", None)
        __ctx = WithParamsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Idle(self, __e):
        if __e._message == "add":
            value = __e._parameters["value"]
            print("Cannot add in Idle state")
        elif __e._message == "get_total":
            self._context_stack[-1]._return = self.total
            return
        elif __e._message == "multiply":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            self._context_stack[-1]._return = 0
            return
        elif __e._message == "start":
            initial = __e._parameters["initial"]
            self.total = initial
            print(f"Started with initial value: {initial}")
            __compartment = WithParamsCompartment("Running", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_Running(self, __e):
        if __e._message == "add":
            value = __e._parameters["value"]
            self.total += value
            print(f"Added {value}, total is now {self.total}")
        elif __e._message == "get_total":
            self._context_stack[-1]._return = self.total
            return
        elif __e._message == "multiply":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            result = a * b
            self.total += result
            print(f"Multiplied {a} * {b} = {result}, total is now {self.total}")
            self._context_stack[-1]._return = result
            return
        elif __e._message == "start":
            initial = __e._parameters["initial"]
            print("Already running")


def main():
    print("=== Test 07: Handler Parameters ===")
    s = WithParams()

    # Initial total should be 0
    total = s.get_total()
    assert total == 0, f"Expected initial total=0, got {total}"

    # Start with initial value
    s.start(100)
    total = s.get_total()
    assert total == 100, f"Expected total=100, got {total}"
    print(f"After start(100): total = {total}")

    # Add value
    s.add(25)
    total = s.get_total()
    assert total == 125, f"Expected total=125, got {total}"
    print(f"After add(25): total = {total}")

    # Multiply with two params
    result = s.multiply(3, 5)
    assert result == 15, f"Expected multiply result=15, got {result}"
    total = s.get_total()
    assert total == 140, f"Expected total=140, got {total}"
    print(f"After multiply(3,5): result = {result}, total = {total}")

    print("PASS: Handler parameters work correctly")

if __name__ == '__main__':
    main()
