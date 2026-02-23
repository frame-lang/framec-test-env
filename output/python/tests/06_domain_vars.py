from typing import Any, Optional, List, Dict, Callable

class DomainVarsFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class DomainVarsFrameContext:
    def __init__(self, event: DomainVarsFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class DomainVarsCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'DomainVarsCompartment':
        c = DomainVarsCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class DomainVars:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.count = 0
        self.name = "counter"
        self.__compartment = DomainVarsCompartment("Counting")
        self.__next_compartment = None
        __frame_event = DomainVarsFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = DomainVarsFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = DomainVarsFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = DomainVarsFrameEvent("$>", self.__compartment.enter_args)
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

    def increment(self):
        __e = DomainVarsFrameEvent("increment", None)
        __ctx = DomainVarsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def decrement(self):
        __e = DomainVarsFrameEvent("decrement", None)
        __ctx = DomainVarsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def get_count(self) -> int:
        __e = DomainVarsFrameEvent("get_count", None)
        __ctx = DomainVarsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def set_count(self, value: int):
        __e = DomainVarsFrameEvent("set_count", {"value": value})
        __ctx = DomainVarsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def _state_Counting(self, __e):
        if __e._message == "decrement":
            self.count -= 1
            print(f"{self.name}: decremented to {self.count}")
        elif __e._message == "get_count":
            self._context_stack[-1]._return = self.count
            return
        elif __e._message == "increment":
            self.count += 1
            print(f"{self.name}: incremented to {self.count}")
        elif __e._message == "set_count":
            value = __e._parameters["value"]
            self.count = value
            print(f"{self.name}: set to {self.count}")


def main():
    print("=== Test 06: Domain Variables ===")
    s = DomainVars()

    # Initial value should be 0
    count = s.get_count()
    assert count == 0, f"Expected initial count=0, got {count}"
    print(f"Initial count: {count}")

    # Increment
    s.increment()
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"

    s.increment()
    count = s.get_count()
    assert count == 2, f"Expected count=2, got {count}"

    # Decrement
    s.decrement()
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"

    # Set directly
    s.set_count(100)
    count = s.get_count()
    assert count == 100, f"Expected count=100, got {count}"

    print(f"Final count: {count}")
    print("PASS: Domain variables work correctly")

if __name__ == '__main__':
    main()
