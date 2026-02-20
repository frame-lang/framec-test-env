from typing import Any, Optional, List, Dict, Callable

class StateVarBasicFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class StateVarBasicCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'StateVarBasicCompartment':
        c = StateVarBasicCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class StateVarBasic:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = StateVarBasicCompartment("Counter")
        self.__next_compartment = None
        __frame_event = StateVarBasicFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = StateVarBasicFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = StateVarBasicFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = StateVarBasicFrameEvent("$>", self.__compartment.enter_args)
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

    def increment(self) -> int:
        self._return_value = None
        __e = StateVarBasicFrameEvent("increment", None)
        self.__kernel(__e)
        return self._return_value

    def get_count(self) -> int:
        self._return_value = None
        __e = StateVarBasicFrameEvent("get_count", None)
        self.__kernel(__e)
        return self._return_value

    def reset(self):
        __e = StateVarBasicFrameEvent("reset", None)
        self.__kernel(__e)

    def _state_Counter(self, __e):
        if __e._message == "$>":
            self.__compartment.state_vars["count"] = 0
        elif __e._message == "get_count":
            self._return_value = self.__compartment.state_vars["count"]
            __e._return = self._return_value
            return
        elif __e._message == "increment":
            self.__compartment.state_vars["count"] = self.__compartment.state_vars["count"] + 1
            self._return_value = self.__compartment.state_vars["count"]
            __e._return = self._return_value
            return
        elif __e._message == "reset":
            self.__compartment.state_vars["count"] = 0


def main():
    print("=== Test 10: State Variable Basic ===")
    s = StateVarBasic()

    # Initial value should be 0
    assert s.get_count() == 0, f"Expected 0, got {s.get_count()}"
    print(f"Initial count: {s.get_count()}")

    # Increment should return new value
    result = s.increment()
    assert result == 1, f"Expected 1 after first increment, got {result}"
    print(f"After first increment: {result}")

    # Second increment
    result = s.increment()
    assert result == 2, f"Expected 2 after second increment, got {result}"
    print(f"After second increment: {result}")

    # Reset should set back to 0
    s.reset()
    assert s.get_count() == 0, f"Expected 0 after reset, got {s.get_count()}"
    print(f"After reset: {s.get_count()}")

    print("PASS: State variable basic operations work correctly")

if __name__ == '__main__':
    main()
