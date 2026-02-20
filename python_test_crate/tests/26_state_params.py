from typing import Any, Optional, List, Dict, Callable

class StateParamsFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class StateParamsCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'StateParamsCompartment':
        c = StateParamsCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class StateParams:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = StateParamsCompartment("Idle")
        self.__next_compartment = None
        __frame_event = StateParamsFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = StateParamsFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = StateParamsFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = StateParamsFrameEvent("$>", self.__compartment.enter_args)
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

    def start(self, val: int):
        __e = StateParamsFrameEvent("start", {"0": val})
        self.__kernel(__e)

    def get_value(self) -> int:
        self._return_value = None
        __e = StateParamsFrameEvent("get_value", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Counter(self, __e):
        if __e._message == "$>":
            self.__compartment.state_vars["count"] = 0
            # Access state param via compartment - using string key "0"
            # Note: double underscore for __compartment to match generated class field
            self.__compartment.state_vars["count"] = self.__compartment.state_args["0"]
            count_val = self.__compartment.state_vars["count"]
            print(f"Counter entered with initial={count_val}")
        elif __e._message == "get_value":
            self._return_value = self.__compartment.state_vars["count"]
            __e._return = self._return_value
            return

    def _state_Idle(self, __e):
        if __e._message == "get_value":
            self._return_value = 0
            __e._return = self._return_value
            return
        elif __e._message == "start":
            val = __e._parameters["0"]
            __compartment = StateParamsCompartment("Counter")
            __compartment.state_args = {"0": val}
            self.__transition(__compartment)


def main():
    print("=== Test 26: State Parameters ===")
    s = StateParams()

    val = s.get_value()
    assert val == 0, f"Expected 0 in Idle, got {val}"
    print(f"Initial value: {val}")

    s.start(42)
    val = s.get_value()
    assert val == 42, f"Expected 42 in Counter from state param, got {val}"
    print(f"Value after transition: {val}")

    print("PASS: State parameters work correctly")

if __name__ == '__main__':
    main()
