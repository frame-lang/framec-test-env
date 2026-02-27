
# Test: Basic System Context Access
# Validates @@.param, @@:return, @@:event syntax


from typing import Any, Optional, List, Dict, Callable

class ContextBasicTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class ContextBasicTestFrameContext:
    def __init__(self, event: ContextBasicTestFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class ContextBasicTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'ContextBasicTestCompartment':
        c = ContextBasicTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class ContextBasicTest:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = ContextBasicTestCompartment("Ready")
        self.__next_compartment = None
        __frame_event = ContextBasicTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = ContextBasicTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = ContextBasicTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = ContextBasicTestFrameEvent("$>", self.__compartment.enter_args)
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
        __e = ContextBasicTestFrameEvent("add", {"a": a, "b": b})
        __ctx = ContextBasicTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_event_name(self) -> str:
        __e = ContextBasicTestFrameEvent("get_event_name", None)
        __ctx = ContextBasicTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def greet(self, name: str) -> str:
        __e = ContextBasicTestFrameEvent("greet", {"name": name})
        __ctx = ContextBasicTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Ready(self, __e):
        if __e._message == "add":
            a = __e._parameters["a"]
            b = __e._parameters["b"]
            # Access params via @@ shorthand
            self._context_stack[-1]._return = self._context_stack[-1].event._parameters["a"] + self._context_stack[-1].event._parameters["b"]
        elif __e._message == "get_event_name":
            # Access event name
            self._context_stack[-1]._return = self._context_stack[-1].event._message
        elif __e._message == "greet":
            name = __e._parameters["name"]
            # Mix param access and return
            result = "Hello, " + self._context_stack[-1].event._parameters["name"] + "!"
            self._context_stack[-1]._return = result


def main():
    print("=== Test 36: Context Basic ===")
    s = ContextBasicTest()

    # Test 1: @@.a and @@.b param access, @@:return
    result = s.add(3, 5)
    assert result == 8, f"Expected 8, got {result}"
    print(f"1. add(3, 5) = {result}")

    # Test 2: @@:event access
    event_name = s.get_event_name()
    assert event_name == "get_event_name", f"Expected 'get_event_name', got '{event_name}'"
    print(f"2. @@:event = '{event_name}'")

    # Test 3: @@.name param access with string
    greeting = s.greet("World")
    assert greeting == "Hello, World!", f"Expected 'Hello, World!', got '{greeting}'"
    print(f"3. greet('World') = '{greeting}'")

    print("PASS: Context basic access works correctly")

if __name__ == '__main__':
    main()
