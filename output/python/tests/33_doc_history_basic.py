from typing import Any, Optional, List, Dict, Callable

class HistoryBasicFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class HistoryBasicFrameContext:
    def __init__(self, event: HistoryBasicFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class HistoryBasicCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'HistoryBasicCompartment':
        c = HistoryBasicCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class HistoryBasic:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = HistoryBasicCompartment("A")
        self.__next_compartment = None
        __frame_event = HistoryBasicFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = HistoryBasicFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = HistoryBasicFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = HistoryBasicFrameEvent("$>", self.__compartment.enter_args)
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

    def gotoC_from_A(self):
        __e = HistoryBasicFrameEvent("gotoC_from_A", None)
        __ctx = HistoryBasicFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def gotoC_from_B(self):
        __e = HistoryBasicFrameEvent("gotoC_from_B", None)
        __ctx = HistoryBasicFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def gotoB(self):
        __e = HistoryBasicFrameEvent("gotoB", None)
        __ctx = HistoryBasicFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def return_back(self):
        __e = HistoryBasicFrameEvent("return_back", None)
        __ctx = HistoryBasicFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def get_state(self) -> str:
        __e = HistoryBasicFrameEvent("get_state", None)
        __ctx = HistoryBasicFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_A(self, __e):
        if __e._message == "get_state":
            self._context_stack[-1]._return = "A"
            return
        elif __e._message == "gotoB":
            __compartment = HistoryBasicCompartment("B", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "gotoC_from_A":
            self._state_stack.append(self.__compartment.copy())
            __compartment = HistoryBasicCompartment("C", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_C(self, __e):
        if __e._message == "get_state":
            self._context_stack[-1]._return = "C"
            return
        elif __e._message == "return_back":
            self.__compartment = self._state_stack.pop()
            return

    def _state_B(self, __e):
        if __e._message == "get_state":
            self._context_stack[-1]._return = "B"
            return
        elif __e._message == "gotoC_from_B":
            self._state_stack.append(self.__compartment.copy())
            __compartment = HistoryBasicCompartment("C", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)


def main():
    print("=== Test 33: Doc History Basic ===")
    h = HistoryBasic()

    # Start in A
    assert h.get_state() == "A", f"Expected 'A', got '{h.get_state()}'"

    # Go to C from A (push A)
    h.gotoC_from_A()
    assert h.get_state() == "C", f"Expected 'C', got '{h.get_state()}'"

    # Return back (pop to A)
    h.return_back()
    assert h.get_state() == "A", f"Expected 'A' after pop, got '{h.get_state()}'"

    # Now go to B
    h.gotoB()
    assert h.get_state() == "B", f"Expected 'B', got '{h.get_state()}'"

    # Go to C from B (push B)
    h.gotoC_from_B()
    assert h.get_state() == "C", f"Expected 'C', got '{h.get_state()}'"

    # Return back (pop to B)
    h.return_back()
    assert h.get_state() == "B", f"Expected 'B' after pop, got '{h.get_state()}'"

    print("PASS: History push/pop works correctly")

if __name__ == '__main__':
    main()
