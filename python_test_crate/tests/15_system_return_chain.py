from typing import Any, Optional, List, Dict, Callable

class SystemReturnChainTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class SystemReturnChainTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'SystemReturnChainTestCompartment':
        c = SystemReturnChainTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class SystemReturnChainTest:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = SystemReturnChainTestCompartment("Start")
        self.__next_compartment = None
        __frame_event = SystemReturnChainTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = SystemReturnChainTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = SystemReturnChainTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = SystemReturnChainTestFrameEvent("$>", self.__compartment.enter_args)
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

    def test_enter_sets(self) -> str:
        self._return_value = None
        __e = SystemReturnChainTestFrameEvent("test_enter_sets", None)
        self.__kernel(__e)
        return self._return_value

    def test_exit_then_enter(self) -> str:
        self._return_value = None
        __e = SystemReturnChainTestFrameEvent("test_exit_then_enter", None)
        self.__kernel(__e)
        return self._return_value

    def get_state(self) -> str:
        self._return_value = None
        __e = SystemReturnChainTestFrameEvent("get_state", None)
        self.__kernel(__e)
        return self._return_value

    def _state_EnterSetter(self, __e):
        if __e._message == "$>":
            # Enter handler sets return value
            self._return_value = "from_enter"
        elif __e._message == "get_state":
            self._return_value = "EnterSetter"
            __e._return = self._return_value
            return

    def _state_BothSet(self, __e):
        if __e._message == "$>":
            # Enter handler sets return - should overwrite exit's value
            self._return_value = "enter_wins"
        elif __e._message == "get_state":
            self._return_value = "BothSet"
            __e._return = self._return_value
            return

    def _state_Start(self, __e):
        if __e._message == "<$":
            # Exit handler sets initial value
            self._return_value = "from_exit"
        elif __e._message == "get_state":
            self._return_value = "Start"
            __e._return = self._return_value
            return
        elif __e._message == "test_enter_sets":
            __compartment = SystemReturnChainTestCompartment("EnterSetter")
            self.__transition(__compartment)
        elif __e._message == "test_exit_then_enter":
            __compartment = SystemReturnChainTestCompartment("BothSet")
            self.__transition(__compartment)


def main():
    print("=== Test 15: System Return Chain (Last Writer Wins) ===")

    # Test 1: Start exit + EnterSetter enter
    # Start's exit sets "from_exit", EnterSetter's enter sets "from_enter"
    # Enter should win (last writer)
    s1 = SystemReturnChainTest()
    result = s1.test_enter_sets()
    assert result == "from_enter", f"Expected 'from_enter', got '{result}'"
    assert s1.get_state() == "EnterSetter", f"Expected state 'EnterSetter'"
    print(f"1. Exit set then enter set - enter wins: '{result}'")

    # Test 2: Both handlers set, enter wins
    s2 = SystemReturnChainTest()
    result = s2.test_exit_then_enter()
    assert result == "enter_wins", f"Expected 'enter_wins', got '{result}'"
    assert s2.get_state() == "BothSet", f"Expected state 'BothSet'"
    print(f"2. Both set - enter wins: '{result}'")

    print("PASS: System return chain (last writer wins) works correctly")

if __name__ == '__main__':
    main()
