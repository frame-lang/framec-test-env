from typing import Any, Optional, List, Dict, Callable

class EventForwardTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class EventForwardTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'EventForwardTestCompartment':
        c = EventForwardTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class EventForwardTest:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.log =         []
        self.__compartment = EventForwardTestCompartment("Idle")
        self.__next_compartment = None
        __frame_event = EventForwardTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = EventForwardTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = EventForwardTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = EventForwardTestFrameEvent("$>", self.__compartment.enter_args)
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

    def process(self):
        __e = EventForwardTestFrameEvent("process", None)
        self.__kernel(__e)

    def get_log(self) -> list:
        self._return_value = None
        __e = EventForwardTestFrameEvent("get_log", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Working(self, __e):
        if __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "process":
            self.log.append("working:process")

    def _state_Idle(self, __e):
        if __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "process":
            self.log.append("idle:process:before")
            __compartment = EventForwardTestCompartment("Working")
            __compartment.forward_event = __e
            self.__transition(__compartment)
            return
            # This should NOT execute because -> => returns after dispatch
            self.log.append("idle:process:after")


def main():
    print("=== Test 19: Transition Forward ===")
    s = EventForwardTest()
    s.process()
    log = s.get_log()
    print(f"Log: {log}")

    # After transition-forward:
    # - Idle logs "idle:process:before"
    # - Transition to Working
    # - Working handles process(), logs "working:process"
    # - Return prevents "idle:process:after"
    assert "idle:process:before" in log, f"Expected 'idle:process:before' in log: {log}"
    assert "working:process" in log, f"Expected 'working:process' in log: {log}"
    assert "idle:process:after" not in log, f"Should NOT have 'idle:process:after' in log: {log}"

    print("PASS: Transition forward works correctly")

if __name__ == '__main__':
    main()
