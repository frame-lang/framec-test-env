from typing import Any, Optional, List, Dict, Callable

class ActionsTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class ActionsTestFrameContext:
    def __init__(self, event: ActionsTestFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class ActionsTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'ActionsTestCompartment':
        c = ActionsTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class ActionsTest:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.log = ""
        self.__compartment = ActionsTestCompartment("Ready")
        self.__next_compartment = None
        __frame_event = ActionsTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = ActionsTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = ActionsTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = ActionsTestFrameEvent("$>", self.__compartment.enter_args)
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

    def process(self, value: int) -> int:
        __e = ActionsTestFrameEvent("process", {"value": value})
        __ctx = ActionsTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_log(self) -> str:
        __e = ActionsTestFrameEvent("get_log", None)
        __ctx = ActionsTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Ready(self, __e):
        if __e._message == "get_log":
            self._context_stack[-1]._return = self.log
            return
        elif __e._message == "process":
            value = __e._parameters["value"]
            self.__log_event("start")
            self.__validate_positive(value)
            self.__log_event("valid")
            result = value * 2
            self.__log_event("done")
            self._context_stack[-1]._return = result
            return

    def __log_event(self, msg: str):
        self.log = self.log + msg + ";"

    def __validate_positive(self, n: int):
        if n < 0:
            raise ValueError(f"Value must be positive: {n}")


def main():
    print("=== Test 21: Actions Basic ===")
    s = ActionsTest()

    # Test 1: Actions are called correctly
    result = s.process(5)
    assert result == 10, f"Expected 10, got {result}"
    print(f"1. process(5) = {result}")

    # Test 2: Log shows action calls
    log = s.get_log()
    assert "start" in log, f"Missing 'start' in log: {log}"
    assert "valid" in log, f"Missing 'valid' in log: {log}"
    assert "done" in log, f"Missing 'done' in log: {log}"
    print(f"2. Log: {log}")

    # Test 3: Action with validation
    try:
        s.process(-1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"3. Validation caught: {e}")

    print("PASS: Actions basic works correctly")

if __name__ == '__main__':
    main()
