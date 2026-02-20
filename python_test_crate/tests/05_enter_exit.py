from typing import Any, Optional, List, Dict, Callable

class EnterExitFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class EnterExitCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'EnterExitCompartment':
        c = EnterExitCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class EnterExit:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.log =         []
        self.__compartment = EnterExitCompartment("Off")
        self.__next_compartment = None
        __frame_event = EnterExitFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = EnterExitFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = EnterExitFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = EnterExitFrameEvent("$>", self.__compartment.enter_args)
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

    def toggle(self):
        __e = EnterExitFrameEvent("toggle", None)
        self.__kernel(__e)

    def get_log(self) -> list:
        self._return_value = None
        __e = EnterExitFrameEvent("get_log", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Off(self, __e):
        if __e._message == "<$":
            self.log.append("exit:Off")
            print("Exiting Off state")
        elif __e._message == "$>":
            self.log.append("enter:Off")
            print("Entered Off state")
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "toggle":
            __compartment = EnterExitCompartment("On", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_On(self, __e):
        if __e._message == "<$":
            self.log.append("exit:On")
            print("Exiting On state")
        elif __e._message == "$>":
            self.log.append("enter:On")
            print("Entered On state")
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "toggle":
            __compartment = EnterExitCompartment("Off", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)


def main():
    print("=== Test 05: Enter/Exit Handlers ===")
    s = EnterExit()

    # Initial enter should have been called
    log = s.get_log()
    assert "enter:Off" in log, f"Expected 'enter:Off' in log, got {log}"
    print(f"After construction: {log}")

    # Toggle to On - should exit Off, enter On
    s.toggle()
    log = s.get_log()
    assert "exit:Off" in log, f"Expected 'exit:Off' in log, got {log}"
    assert "enter:On" in log, f"Expected 'enter:On' in log, got {log}"
    print(f"After toggle to On: {log}")

    # Toggle back to Off - should exit On, enter Off
    s.toggle()
    log = s.get_log()
    assert log.count("enter:Off") == 2, f"Expected 2 'enter:Off' entries, got {log}"
    assert "exit:On" in log, f"Expected 'exit:On' in log, got {log}"
    print(f"After toggle to Off: {log}")

    print("PASS: Enter/Exit handlers work correctly")

if __name__ == '__main__':
    main()
