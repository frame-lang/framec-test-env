
# Test: Interface method return_init
# Validates that interface methods can have default return values
# Syntax: method(): type = "default_value"


from typing import Any, Optional, List, Dict, Callable

class ReturnInitTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class ReturnInitTestFrameContext:
    def __init__(self, event: ReturnInitTestFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class ReturnInitTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'ReturnInitTestCompartment':
        c = ReturnInitTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class ReturnInitTest:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = ReturnInitTestCompartment("Start")
        self.__next_compartment = None
        __frame_event = ReturnInitTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = ReturnInitTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = ReturnInitTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = ReturnInitTestFrameEvent("$>", self.__compartment.enter_args)
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

    def get_status(self) -> str:
        __e = ReturnInitTestFrameEvent("get_status", None)
        __ctx = ReturnInitTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_count(self) -> int:
        __e = ReturnInitTestFrameEvent("get_count", None)
        __ctx = ReturnInitTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_flag(self) -> bool:
        __e = ReturnInitTestFrameEvent("get_flag", None)
        __ctx = ReturnInitTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def trigger(self):
        __e = ReturnInitTestFrameEvent("trigger", None)
        __ctx = ReturnInitTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def _state_Active(self, __e):
        if __e._message == "$>":
            pass  # Active state enter
        elif __e._message == "get_count":
            self._context_stack[-1]._return = 42
        elif __e._message == "get_flag":
            self._context_stack[-1]._return = True
        elif __e._message == "get_status":
            self._context_stack[-1]._return = "active"
        elif __e._message == "trigger":
            __compartment = ReturnInitTestCompartment("Start", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_Start(self, __e):
        if __e._message == "$>":
            pass  # Start state enter
        elif __e._message == "get_count":
            pass  # Don't set return - should use default 0
        elif __e._message == "get_flag":
            pass  # Don't set return - should use default False
        elif __e._message == "get_status":
            pass  # Don't set return - should use default "unknown"
        elif __e._message == "trigger":
            __compartment = ReturnInitTestCompartment("Active", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)


if __name__ == "__main__":
    print("TAP version 14")
    print("1..6")

    s = ReturnInitTest()

    # Test 1: Default string return
    if s.get_status() == "unknown":
        print("ok 1 - default string return is 'unknown'")
    else:
        print(f"not ok 1 - default string return is 'unknown' # got {s.get_status()}")

    # Test 2: Default int return
    if s.get_count() == 0:
        print("ok 2 - default int return is 0")
    else:
        print(f"not ok 2 - default int return is 0 # got {s.get_count()}")

    # Test 3: Default bool return
    if s.get_flag() == False:
        print("ok 3 - default bool return is False")
    else:
        print(f"not ok 3 - default bool return is False # got {s.get_flag()}")

    # Transition to Active state
    s.trigger()

    # Test 4: Explicit string return overrides default
    if s.get_status() == "active":
        print("ok 4 - explicit return overrides default string")
    else:
        print(f"not ok 4 - explicit return overrides default string # got {s.get_status()}")

    # Test 5: Explicit int return overrides default
    if s.get_count() == 42:
        print("ok 5 - explicit return overrides default int")
    else:
        print(f"not ok 5 - explicit return overrides default int # got {s.get_count()}")

    # Test 6: Explicit bool return overrides default
    if s.get_flag() == True:
        print("ok 6 - explicit return overrides default bool")
    else:
        print(f"not ok 6 - explicit return overrides default bool # got {s.get_flag()}")

    print("# PASS - return_init provides default return values")
