from typing import Any, Optional, List, Dict, Callable

class SystemReturnDefaultTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class SystemReturnDefaultTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'SystemReturnDefaultTestCompartment':
        c = SystemReturnDefaultTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class SystemReturnDefaultTest:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = SystemReturnDefaultTestCompartment("Start")
        self.__next_compartment = None
        __frame_event = SystemReturnDefaultTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = SystemReturnDefaultTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = SystemReturnDefaultTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = SystemReturnDefaultTestFrameEvent("$>", self.__compartment.enter_args)
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

    def handler_sets_value(self) -> str:
        self._return_value = None
        __e = SystemReturnDefaultTestFrameEvent("handler_sets_value", None)
        self.__kernel(__e)
        return self._return_value

    def handler_no_return(self) -> str:
        self._return_value = None
        __e = SystemReturnDefaultTestFrameEvent("handler_no_return", None)
        self.__kernel(__e)
        return self._return_value

    def get_count(self) -> int:
        self._return_value = None
        __e = SystemReturnDefaultTestFrameEvent("get_count", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Start(self, __e):
        if __e._message == "$>":
            self.__compartment.state_vars["count"] = 0
        elif __e._message == "get_count":
            self._return_value = self.__compartment.state_vars["count"]
            __e._return = self._return_value
            return
        elif __e._message == "handler_no_return":
            # Does not set return - should return None
            self.__compartment.state_vars["count"] = self.__compartment.state_vars["count"] + 1
        elif __e._message == "handler_sets_value":
            self._return_value = "set_by_handler"
            __e._return = self._return_value
            return


def main():
    print("=== Test 14: System Return Default Behavior ===")
    s = SystemReturnDefaultTest()

    # Test 1: Handler explicitly sets return value
    result = s.handler_sets_value()
    assert result == "set_by_handler", f"Expected 'set_by_handler', got '{result}'"
    print(f"1. handler_sets_value() = '{result}'")

    # Test 2: Handler does NOT set return - should return None
    result = s.handler_no_return()
    assert result is None, f"Expected None, got '{result}'"
    print(f"2. handler_no_return() = {result}")

    # Test 3: Verify handler was called (side effect check)
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"
    print(f"3. Handler was called, count = {count}")

    # Test 4: Call again to verify idempotence
    result = s.handler_no_return()
    assert result is None, f"Expected None again, got '{result}'"
    count = s.get_count()
    assert count == 2, f"Expected count=2, got {count}"
    print(f"4. Second call: result={result}, count={count}")

    print("PASS: System return default behavior works correctly")

if __name__ == '__main__':
    main()
