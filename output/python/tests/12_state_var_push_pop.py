from typing import Any, Optional, List, Dict, Callable

class StateVarPushPopFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class StateVarPushPopCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'StateVarPushPopCompartment':
        c = StateVarPushPopCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class StateVarPushPop:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = StateVarPushPopCompartment("Counter")
        self.__next_compartment = None
        __frame_event = StateVarPushPopFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = StateVarPushPopFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = StateVarPushPopFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = StateVarPushPopFrameEvent("$>", self.__compartment.enter_args)
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
        self._return_value = None
        __e = StateVarPushPopFrameEvent("increment", None)
        self.__kernel(__e)
        return self._return_value

    def get_count(self) -> int:
        self._return_value = None
        __e = StateVarPushPopFrameEvent("get_count", None)
        self.__kernel(__e)
        return self._return_value

    def save_and_go(self):
        __e = StateVarPushPopFrameEvent("save_and_go", None)
        self.__kernel(__e)

    def restore(self):
        __e = StateVarPushPopFrameEvent("restore", None)
        self.__kernel(__e)

    def _state_Counter(self, __e):
        if __e._message == "$>":
            self.__compartment.state_vars["count"] = 0
        elif __e._message == "get_count":
            self._return_value = self.__compartment.state_vars["count"]
            __e._return = self._return_value
            return
        elif __e._message == "increment":
            self.__compartment.state_vars["count"] = self.__compartment.state_vars["count"] + 1
            self._return_value = self.__compartment.state_vars["count"]
            __e._return = self._return_value
            return
        elif __e._message == "save_and_go":
            self._state_stack.append(self.__compartment.copy())
            __compartment = StateVarPushPopCompartment("Other", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_Other(self, __e):
        if __e._message == "$>":
            self.__compartment.state_vars["other_count"] = 100
        elif __e._message == "get_count":
            self._return_value = self.__compartment.state_vars["other_count"]
            __e._return = self._return_value
            return
        elif __e._message == "increment":
            self.__compartment.state_vars["other_count"] = self.__compartment.state_vars["other_count"] + 1
            self._return_value = self.__compartment.state_vars["other_count"]
            __e._return = self._return_value
            return
        elif __e._message == "restore":
            self.__compartment = self._state_stack.pop()
            return


def main():
    print("=== Test 12: State Variable Push/Pop ===")
    s = StateVarPushPop()

    # Increment counter to 3
    s.increment()
    s.increment()
    s.increment()
    count = s.get_count()
    assert count == 3, f"Expected 3, got {count}"
    print(f"Counter before push: {count}")

    # Push and go to Other state
    s.save_and_go()
    print("Pushed and transitioned to Other")

    # In Other state, count should be 100 (Other's state var)
    count = s.get_count()
    assert count == 100, f"Expected 100 in Other state, got {count}"
    print(f"Other state count: {count}")

    # Increment in Other
    s.increment()
    count = s.get_count()
    assert count == 101, f"Expected 101 after increment, got {count}"
    print(f"Other state after increment: {count}")

    # Pop back - should restore Counter with count=3
    s.restore()
    print("Popped back to Counter")

    count = s.get_count()
    assert count == 3, f"Expected 3 after pop (preserved), got {count}"
    print(f"Counter after pop: {count}")

    # Increment to verify it works
    s.increment()
    count = s.get_count()
    assert count == 4, f"Expected 4, got {count}"
    print(f"Counter after increment: {count}")

    print("PASS: State variables preserved across push/pop")

if __name__ == '__main__':
    main()
