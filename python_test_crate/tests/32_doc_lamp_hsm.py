from typing import Any, Optional, List, Dict, Callable

class LampHSMFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class LampHSMCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'LampHSMCompartment':
        c = LampHSMCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class LampHSM:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.color = "white"
        self.lamp_on = False
        self.__compartment = LampHSMCompartment("Off")
        self.__next_compartment = None
        __frame_event = LampHSMFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = LampHSMFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = LampHSMFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = LampHSMFrameEvent("$>", self.__compartment.enter_args)
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
        __e = LampHSMFrameEvent("turnOn", None)
        self.__kernel(__e)

    def turnOff(self):
        __e = LampHSMFrameEvent("turnOff", None)
        self.__kernel(__e)

    def getColor(self) -> str:
        self._return_value = None
        __e = LampHSMFrameEvent("getColor", None)
        self.__kernel(__e)
        return self._return_value

    def setColor(self, color: str):
        __e = LampHSMFrameEvent("setColor", {"0": color})
        self.__kernel(__e)

    def _state_ColorBehavior(self, __e):
        if __e._message == "getColor":
            self._return_value = self.color
            __e._return = self._return_value
            return
        elif __e._message == "setColor":
            color = __e._parameters["0"]
            self.color = color

    def _state_On(self, __e):
        if __e._message == "<$":
            self.turnOffLamp()
        elif __e._message == "$>":
            self.turnOnLamp()
        elif __e._message == "turnOff":
            __compartment = LampHSMCompartment("Off", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        else:
            self._state_ColorBehavior(__e)

    def _state_Off(self, __e):
        if __e._message == "turnOn":
            __compartment = LampHSMCompartment("On", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        else:
            self._state_ColorBehavior(__e)

    def turnOnLamp(self):
        self.lamp_on = True

    def turnOffLamp(self):
        self.lamp_on = False


def main():
    print("=== Test 32: Doc Lamp HSM ===")
    lamp = LampHSM()

    # Color behavior available in both states
    assert lamp.getColor() == "white", f"Expected 'white', got '{lamp.getColor()}'"
    lamp.setColor("red")
    assert lamp.getColor() == "red", f"Expected 'red', got '{lamp.getColor()}'"

    # Turn on
    lamp.turnOn()
    assert lamp.lamp_on == True, "Lamp should be on"

    # Color still works when on
    lamp.setColor("green")
    assert lamp.getColor() == "green", f"Expected 'green', got '{lamp.getColor()}'"

    # Turn off
    lamp.turnOff()
    assert lamp.lamp_on == False, "Lamp should be off"

    # Color still works when off
    assert lamp.getColor() == "green", f"Expected 'green', got '{lamp.getColor()}'"

    print("PASS: HSM lamp works correctly")

if __name__ == '__main__':
    main()
