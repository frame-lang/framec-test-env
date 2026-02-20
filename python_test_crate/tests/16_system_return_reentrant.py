from typing import Any, Optional, List, Dict, Callable

class SystemReturnReentrantTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class SystemReturnReentrantTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'SystemReturnReentrantTestCompartment':
        c = SystemReturnReentrantTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class SystemReturnReentrantTest:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.__compartment = SystemReturnReentrantTestCompartment("Start")
        self.__next_compartment = None
        __frame_event = SystemReturnReentrantTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = SystemReturnReentrantTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = SystemReturnReentrantTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = SystemReturnReentrantTestFrameEvent("$>", self.__compartment.enter_args)
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

    def outer_call(self) -> str:
        self._return_value = None
        __e = SystemReturnReentrantTestFrameEvent("outer_call", None)
        self.__kernel(__e)
        return self._return_value

    def inner_call(self) -> str:
        self._return_value = None
        __e = SystemReturnReentrantTestFrameEvent("inner_call", None)
        self.__kernel(__e)
        return self._return_value

    def nested_call(self) -> str:
        self._return_value = None
        __e = SystemReturnReentrantTestFrameEvent("nested_call", None)
        self.__kernel(__e)
        return self._return_value

    def get_log(self) -> str:
        self._return_value = None
        __e = SystemReturnReentrantTestFrameEvent("get_log", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Start(self, __e):
        if __e._message == "$>":
            self.__compartment.state_vars["log"] = ""
        elif __e._message == "get_log":
            self._return_value = self.__compartment.state_vars["log"]
            __e._return = self._return_value
            return
        elif __e._message == "inner_call":
            self.__compartment.state_vars["log"] = self.__compartment.state_vars["log"] + "inner,"
            self._return_value = "inner_result"
            __e._return = self._return_value
            return
        elif __e._message == "nested_call":
            self.__compartment.state_vars["log"] = self.__compartment.state_vars["log"] + "nested_start,"
            # Two levels of nesting
            result1 = self.inner_call()
            result2 = self.outer_call()
            self.__compartment.state_vars["log"] = self.__compartment.state_vars["log"] + "nested_end,"
            self._return_value = "nested:" + result1 + "+" + result2
            __e._return = self._return_value
            return
        elif __e._message == "outer_call":
            self.__compartment.state_vars["log"] = self.__compartment.state_vars["log"] + "outer_start,"
            # Call inner method - this creates nested return context
            inner_result = self.inner_call()
            self.__compartment.state_vars["log"] = self.__compartment.state_vars["log"] + "outer_after_inner,"
            # Our return should be independent of inner's return
            self._return_value = "outer_result:" + inner_result
            __e._return = self._return_value
            return


def main():
    print("=== Test 16: System Return Reentrant (Nested Calls) ===")

    # Test 1: Simple inner call
    s1 = SystemReturnReentrantTest()
    result = s1.inner_call()
    assert result == "inner_result", f"Expected 'inner_result', got '{result}'"
    print(f"1. inner_call() = '{result}'")

    # Test 2: Outer calls inner - return contexts should be separate
    s2 = SystemReturnReentrantTest()
    result = s2.outer_call()
    assert result == "outer_result:inner_result", f"Expected 'outer_result:inner_result', got '{result}'"
    log = s2.get_log()
    assert "outer_start" in log, f"Missing outer_start in log: {log}"
    assert "inner" in log, f"Missing inner in log: {log}"
    assert "outer_after_inner" in log, f"Missing outer_after_inner in log: {log}"
    print(f"2. outer_call() = '{result}'")
    print(f"   Log: '{log}'")

    # Test 3: Deeply nested calls
    s3 = SystemReturnReentrantTest()
    result = s3.nested_call()
    expected = "nested:inner_result+outer_result:inner_result"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"3. nested_call() = '{result}'")

    print("PASS: System return reentrant (nested calls) works correctly")

if __name__ == '__main__':
    main()
