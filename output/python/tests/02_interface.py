from typing import Any, Optional, List, Dict, Callable

class WithInterfaceFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class WithInterfaceFrameContext:
    def __init__(self, event: WithInterfaceFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class WithInterfaceCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'WithInterfaceCompartment':
        c = WithInterfaceCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class WithInterface:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.call_count = 0
        self.__compartment = WithInterfaceCompartment("Ready")
        self.__next_compartment = None
        __frame_event = WithInterfaceFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = WithInterfaceFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = WithInterfaceFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = WithInterfaceFrameEvent("$>", self.__compartment.enter_args)
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

    def greet(self, name: str) -> str:
        __e = WithInterfaceFrameEvent("greet", {"name": name})
        __ctx = WithInterfaceFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_count(self) -> int:
        __e = WithInterfaceFrameEvent("get_count", None)
        __ctx = WithInterfaceFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Ready(self, __e):
        if __e._message == "get_count":
            self._context_stack[-1]._return = self.call_count
            return
        elif __e._message == "greet":
            name = __e._parameters["name"]
            self.call_count += 1
            self._context_stack[-1]._return = f"Hello, {name}!"
            return


def main():
    print("=== Test 02: Interface Methods ===")
    s = WithInterface()

    # Test interface method with parameter and return
    result = s.greet("World")
    assert result == "Hello, World!", f"Expected 'Hello, World!', got '{result}'"
    print(f"greet('World') = {result}")

    # Test domain variable access through interface
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"
    print(f"get_count() = {count}")

    # Call again to verify state
    s.greet("Frame")
    count2 = s.get_count()
    assert count2 == 2, f"Expected count=2, got {count2}"
    print(f"After second call: get_count() = {count2}")

    print("PASS: Interface methods work correctly")

if __name__ == '__main__':
    main()
