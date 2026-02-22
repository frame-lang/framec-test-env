from typing import Any, Optional, List, Dict, Callable

class LampFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class LampCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'LampCompartment':
        c = LampCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class Lamp:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.color = "white"
        self.switch_closed = False
        self.__compartment = LampCompartment("Off")
        self.__next_compartment = None
        __frame_event = LampFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = LampFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = LampFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = LampFrameEvent("$>", self.__compartment.enter_args)
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

    def turnOn(self):
        __e = LampFrameEvent("turnOn", None)
        self.__kernel(__e)

    def turnOff(self):
        __e = LampFrameEvent("turnOff", None)
        self.__kernel(__e)

    def getColor(self) -> str:
        self._return_value = None
        __e = LampFrameEvent("getColor", None)
        self.__kernel(__e)
        return self._return_value

    def setColor(self, color: str):
        __e = LampFrameEvent("setColor", {"0": color})
        self.__kernel(__e)

    def _state_On(self, __e):
        if __e._message == "<$":
            self.openSwitch()
        elif __e._message == "$>":
            self.closeSwitch()
        elif __e._message == "getColor":
            self._return_value = self.color
            __e._return = self._return_value
            return
        elif __e._message == "setColor":
            color = __e._parameters["0"]
            self.color = color
        elif __e._message == "turnOff":
            __compartment = LampCompartment("Off", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_Off(self, __e):
        if __e._message == "getColor":
            self._return_value = self.color
            __e._return = self._return_value
            return
        elif __e._message == "setColor":
            color = __e._parameters["0"]
            self.color = color
        elif __e._message == "turnOn":
            __compartment = LampCompartment("On", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def closeSwitch(self):
        self.switch_closed = True

    def openSwitch(self):
        self.switch_closed = False


def main():
    print("=== Test 31: Doc Lamp Basic ===")
    lamp = Lamp()

    # Initially off
    assert lamp.switch_closed == False, "Switch should be open initially"

    # Turn on - should close switch
    lamp.turnOn()
    assert lamp.switch_closed == True, "Switch should be closed after turnOn"

    # Check color
    assert lamp.getColor() == "white", f"Expected 'white', got '{lamp.getColor()}'"

    # Set color
    lamp.setColor("blue")
    assert lamp.getColor() == "blue", f"Expected 'blue', got '{lamp.getColor()}'"

    # Turn off - should open switch
    lamp.turnOff()
    assert lamp.switch_closed == False, "Switch should be open after turnOff"

    print("PASS: Basic lamp works correctly")

if __name__ == '__main__':
    main()
