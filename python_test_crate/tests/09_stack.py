from typing import Any, Optional, List, Dict, Callable

class StackOpsFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class StackOpsCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'StackOpsCompartment':
        c = StackOpsCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class StackOps:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = StackOpsCompartment("Main")
        self.__next_compartment = None
        __frame_event = StackOpsFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = StackOpsFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = StackOpsFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = StackOpsFrameEvent("$>", self.__compartment.enter_args)
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

    def push_and_go(self):
        __e = StackOpsFrameEvent("push_and_go", None)
        self.__kernel(__e)

    def pop_back(self):
        __e = StackOpsFrameEvent("pop_back", None)
        self.__kernel(__e)

    def do_work(self) -> str:
        self._return_value = None
        __e = StackOpsFrameEvent("do_work", None)
        self.__kernel(__e)
        return self._return_value

    def get_state(self) -> str:
        self._return_value = None
        __e = StackOpsFrameEvent("get_state", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Main(self, __e):
        if __e._message == "do_work":
            self._return_value = "Working in Main"
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "Main"
            __e._return = self._return_value
            return
        elif __e._message == "pop_back":
            print("Cannot pop - nothing on stack in Main")
        elif __e._message == "push_and_go":
            print("Pushing Main to stack, going to Sub")
            self._state_stack.append(self.__compartment.copy())
            __compartment = StackOpsCompartment("Sub", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_Sub(self, __e):
        if __e._message == "do_work":
            self._return_value = "Working in Sub"
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "Sub"
            __e._return = self._return_value
            return
        elif __e._message == "pop_back":
            print("Popping back to previous state")
            self.__compartment = self._state_stack.pop()
            return
        elif __e._message == "push_and_go":
            print("Already in Sub")


def main():
    print("=== Test 09: Stack Push/Pop ===")
    s = StackOps()

    # Initial state should be Main
    state = s.get_state()
    assert state == "Main", f"Expected 'Main', got '{state}'"
    print(f"Initial state: {state}")

    # Do work in Main
    work = s.do_work()
    assert work == "Working in Main", f"Expected 'Working in Main', got '{work}'"
    print(f"do_work(): {work}")

    # Push and go to Sub
    s.push_and_go()
    state = s.get_state()
    assert state == "Sub", f"Expected 'Sub', got '{state}'"
    print(f"After push_and_go(): {state}")

    # Do work in Sub
    work = s.do_work()
    assert work == "Working in Sub", f"Expected 'Working in Sub', got '{work}'"
    print(f"do_work(): {work}")

    # Pop back to Main
    s.pop_back()
    state = s.get_state()
    assert state == "Main", f"Expected 'Main' after pop, got '{state}'"
    print(f"After pop_back(): {state}")

    print("PASS: Stack push/pop works correctly")

if __name__ == '__main__':
    main()
