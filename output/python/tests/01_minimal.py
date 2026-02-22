from typing import Any, Optional, List, Dict, Callable

class MinimalFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class MinimalCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'MinimalCompartment':
        c = MinimalCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class Minimal:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = MinimalCompartment("Start")
        self.__next_compartment = None
        __frame_event = MinimalFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = MinimalFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = MinimalFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = MinimalFrameEvent("$>", self.__compartment.enter_args)
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

    def is_alive(self) -> bool:
        self._return_value = None
        __e = MinimalFrameEvent("is_alive", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Start(self, __e):
        if __e._message == "is_alive":
            self._return_value = True
            __e._return = self._return_value
            return


def main():
    print("=== Test 01: Minimal System ===")
    s = Minimal()

    # Test that system instantiates and responds
    result = s.is_alive()
    assert result == True, f"Expected True, got {result}"
    print(f"is_alive() = {result}")

    print("PASS: Minimal system works correctly")

if __name__ == '__main__':
    main()
