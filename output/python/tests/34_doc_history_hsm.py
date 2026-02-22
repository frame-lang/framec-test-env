from typing import Any, Optional, List, Dict, Callable

class HistoryHSMFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class HistoryHSMCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'HistoryHSMCompartment':
        c = HistoryHSMCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class HistoryHSM:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.log =         []
        self.__compartment = HistoryHSMCompartment("Waiting")
        self.__next_compartment = None
        __frame_event = HistoryHSMFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = HistoryHSMFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = HistoryHSMFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = HistoryHSMFrameEvent("$>", self.__compartment.enter_args)
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

    def gotoA(self):
        __e = HistoryHSMFrameEvent("gotoA", None)
        self.__kernel(__e)

    def gotoB(self):
        __e = HistoryHSMFrameEvent("gotoB", None)
        self.__kernel(__e)

    def gotoC(self):
        __e = HistoryHSMFrameEvent("gotoC", None)
        self.__kernel(__e)

    def goBack(self):
        __e = HistoryHSMFrameEvent("goBack", None)
        self.__kernel(__e)

    def get_state(self) -> str:
        self._return_value = None
        __e = HistoryHSMFrameEvent("get_state", None)
        self.__kernel(__e)
        return self._return_value

    def get_log(self) -> list:
        self._return_value = None
        __e = HistoryHSMFrameEvent("get_log", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Waiting(self, __e):
        if __e._message == "$>":
            self.log_msg("In $Waiting")
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "Waiting"
            __e._return = self._return_value
            return
        elif __e._message == "gotoA":
            self.log_msg("gotoA")
            __compartment = HistoryHSMCompartment("A", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "gotoB":
            self.log_msg("gotoB")
            __compartment = HistoryHSMCompartment("B", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_B(self, __e):
        if __e._message == "$>":
            self.log_msg("In $B")
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "B"
            __e._return = self._return_value
            return
        elif __e._message == "gotoA":
            self.log_msg("gotoA")
            __compartment = HistoryHSMCompartment("A", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        else:
            self._state_AB(__e)

    def _state_C(self, __e):
        if __e._message == "$>":
            self.log_msg("In $C")
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "C"
            __e._return = self._return_value
            return
        elif __e._message == "goBack":
            self.log_msg("goBack")
            self.__compartment = self._state_stack.pop()
            return

    def _state_A(self, __e):
        if __e._message == "$>":
            self.log_msg("In $A")
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "A"
            __e._return = self._return_value
            return
        elif __e._message == "gotoB":
            self.log_msg("gotoB")
            __compartment = HistoryHSMCompartment("B", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        else:
            self._state_AB(__e)

    def _state_AB(self, __e):
        if __e._message == "gotoC":
            self.log_msg("gotoC in $AB")
            self._state_stack.append(self.__compartment.copy())
            __compartment = HistoryHSMCompartment("C", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def log_msg(self, msg: str):
        self.log.append(msg)


def main():
    print("=== Test 34: Doc History HSM ===")
    h = HistoryHSM()

    # Start in Waiting
    assert h.get_state() == "Waiting", f"Expected 'Waiting', got '{h.get_state()}'"
    assert "In $Waiting" in h.get_log(), f"Expected enter log, got {h.get_log()}"

    # Go to A
    h.gotoA()
    assert h.get_state() == "A", f"Expected 'A', got '{h.get_state()}'"

    # Go to C (using inherited gotoC from $AB)
    h.gotoC()
    assert h.get_state() == "C", f"Expected 'C', got '{h.get_state()}'"
    assert "gotoC in $AB" in h.get_log(), f"Expected gotoC log, got {h.get_log()}"

    # Go back (should pop to A)
    h.goBack()
    assert h.get_state() == "A", f"Expected 'A' after goBack, got '{h.get_state()}'"

    # Go to B
    h.gotoB()
    assert h.get_state() == "B", f"Expected 'B', got '{h.get_state()}'"

    # Go to C (again using inherited gotoC)
    h.gotoC()
    assert h.get_state() == "C", f"Expected 'C', got '{h.get_state()}'"

    # Go back (should pop to B)
    h.goBack()
    assert h.get_state() == "B", f"Expected 'B' after goBack, got '{h.get_state()}'"

    print(f"Log: {h.get_log()}")
    print("PASS: HSM with history works correctly")

if __name__ == '__main__':
    main()
