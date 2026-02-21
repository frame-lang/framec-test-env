from typing import Any, Optional, List, Dict, Callable

class HSMForwardFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class HSMForwardCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'HSMForwardCompartment':
        c = HSMForwardCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class HSMForward:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.log =         []
        self.__compartment = HSMForwardCompartment("Child")
        self.__next_compartment = None
        __frame_event = HSMForwardFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = HSMForwardFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = HSMForwardFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = HSMForwardFrameEvent("$>", self.__compartment.enter_args)
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

    def event_a(self):
        __e = HSMForwardFrameEvent("event_a", None)
        self.__kernel(__e)

    def event_b(self):
        __e = HSMForwardFrameEvent("event_b", None)
        self.__kernel(__e)

    def get_log(self) -> list:
        self._return_value = None
        __e = HSMForwardFrameEvent("get_log", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Child(self, __e):
        if __e._message == "event_a":
            self.log.append("Child:event_a")
        elif __e._message == "event_b":
            self.log.append("Child:event_b_forward")
            self._state_Parent(__e)
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return

    def _state_Parent(self, __e):
        if __e._message == "event_a":
            self.log.append("Parent:event_a")
        elif __e._message == "event_b":
            self.log.append("Parent:event_b")
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return


def main():
    print("=== Test 08: HSM Forward ===")
    s = HSMForward()

    # event_a should be handled by Child (no forward)
    s.event_a()
    log = s.get_log()
    assert "Child:event_a" in log, f"Expected 'Child:event_a' in log, got {log}"
    print(f"After event_a: {log}")

    # event_b should forward to Parent
    s.event_b()
    log = s.get_log()
    assert "Child:event_b_forward" in log, f"Expected 'Child:event_b_forward' in log, got {log}"
    assert "Parent:event_b" in log, f"Expected 'Parent:event_b' in log (forwarded), got {log}"
    print(f"After event_b (forwarded): {log}")

    print("PASS: HSM forward works correctly")

if __name__ == '__main__':
    main()
