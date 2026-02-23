from typing import Any, Optional, List, Dict, Callable

class WithTransitionFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class WithTransitionFrameContext:
    def __init__(self, event: WithTransitionFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class WithTransitionCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'WithTransitionCompartment':
        c = WithTransitionCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class WithTransition:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = WithTransitionCompartment("First")
        self.__next_compartment = None
        __frame_event = WithTransitionFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = WithTransitionFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = WithTransitionFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = WithTransitionFrameEvent("$>", self.__compartment.enter_args)
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

    def next(self):
        __e = WithTransitionFrameEvent("next", None)
        __ctx = WithTransitionFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def get_state(self) -> str:
        __e = WithTransitionFrameEvent("get_state", None)
        __ctx = WithTransitionFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_First(self, __e):
        if __e._message == "get_state":
            self._context_stack[-1]._return = "First"
            return
        elif __e._message == "next":
            print("Transitioning: First -> Second")
            __compartment = WithTransitionCompartment("Second", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_Second(self, __e):
        if __e._message == "get_state":
            self._context_stack[-1]._return = "Second"
            return
        elif __e._message == "next":
            print("Transitioning: Second -> First")
            __compartment = WithTransitionCompartment("First", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)


def main():
    print("=== Test 03: State Transitions ===")
    s = WithTransition()

    # Initial state should be First
    state = s.get_state()
    assert state == "First", f"Expected 'First', got '{state}'"
    print(f"Initial state: {state}")

    # Transition to Second
    s.next()
    state = s.get_state()
    assert state == "Second", f"Expected 'Second', got '{state}'"
    print(f"After first next(): {state}")

    # Transition back to First
    s.next()
    state = s.get_state()
    assert state == "First", f"Expected 'First', got '{state}'"
    print(f"After second next(): {state}")

    print("PASS: State transitions work correctly")

if __name__ == '__main__':
    main()
