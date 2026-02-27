from typing import Any, Optional, List, Dict, Callable

class StateVarReentryFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class StateVarReentryFrameContext:
    def __init__(self, event: StateVarReentryFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class StateVarReentryCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'StateVarReentryCompartment':
        c = StateVarReentryCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class StateVarReentry:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = StateVarReentryCompartment("Counter")
        self.__next_compartment = None
        __frame_event = StateVarReentryFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = StateVarReentryFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = StateVarReentryFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = StateVarReentryFrameEvent("$>", self.__compartment.enter_args)
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

    def increment(self) -> int:
        __e = StateVarReentryFrameEvent("increment", None)
        __ctx = StateVarReentryFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_count(self) -> int:
        __e = StateVarReentryFrameEvent("get_count", None)
        __ctx = StateVarReentryFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def go_other(self):
        __e = StateVarReentryFrameEvent("go_other", None)
        __ctx = StateVarReentryFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def come_back(self):
        __e = StateVarReentryFrameEvent("come_back", None)
        __ctx = StateVarReentryFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def _state_Other(self, __e):
        if __e._message == "come_back":
            __compartment = StateVarReentryCompartment("Counter", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "get_count":
            self._context_stack[-1]._return = -1
            return
        elif __e._message == "increment":
            self._context_stack[-1]._return = -1
            return

    def _state_Counter(self, __e):
        if __e._message == "$>":
            if "count" not in self.__compartment.state_vars:
                self.__compartment.state_vars["count"] = 0
        elif __e._message == "get_count":
            self._context_stack[-1]._return = self.__compartment.state_vars["count"]
            return
        elif __e._message == "go_other":
            __compartment = StateVarReentryCompartment("Other", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "increment":
            self.__compartment.state_vars["count"] = self.__compartment.state_vars["count"] + 1
            self._context_stack[-1]._return = self.__compartment.state_vars["count"]
            return


def main():
    print("=== Test 11: State Variable Reentry ===")
    s = StateVarReentry()

    # Increment a few times
    s.increment()
    s.increment()
    count = s.get_count()
    assert count == 2, f"Expected 2 after two increments, got {count}"
    print(f"Count before leaving: {count}")

    # Leave the state
    s.go_other()
    print("Transitioned to Other state")

    # Come back - state var should be reinitialized to 0
    s.come_back()
    count = s.get_count()
    assert count == 0, f"Expected 0 after re-entering Counter (state var reinit), got {count}"
    print(f"Count after re-entering Counter: {count}")

    # Increment again to verify it works
    result = s.increment()
    assert result == 1, f"Expected 1 after increment, got {result}"
    print(f"After increment: {result}")

    print("PASS: State variables reinitialize on state reentry")

if __name__ == '__main__':
    main()
