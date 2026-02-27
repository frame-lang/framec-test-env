
# Test: Context Data (@@:data)
# Validates call-scoped data that persists across handler -> <$ -> $> chain


from typing import Any, Optional, List, Dict, Callable

class ContextDataTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class ContextDataTestFrameContext:
    def __init__(self, event: ContextDataTestFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class ContextDataTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'ContextDataTestCompartment':
        c = ContextDataTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class ContextDataTest:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.__compartment = ContextDataTestCompartment("Start")
        self.__next_compartment = None
        __frame_event = ContextDataTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = ContextDataTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = ContextDataTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = ContextDataTestFrameEvent("$>", self.__compartment.enter_args)
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

    def process_with_data(self, value: int) -> str:
        __e = ContextDataTestFrameEvent("process_with_data", {"value": value})
        __ctx = ContextDataTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def check_data_isolation(self) -> str:
        __e = ContextDataTestFrameEvent("check_data_isolation", None)
        __ctx = ContextDataTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def transition_preserves_data(self, x: int) -> str:
        __e = ContextDataTestFrameEvent("transition_preserves_data", {"x": x})
        __ctx = ContextDataTestFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Start(self, __e):
        if __e._message == "<$":
            # Exit handler can access data set by event handler
            self._context_stack[-1]._data["exit_seen"] = "true"
        elif __e._message == "check_data_isolation":
            # Set data, call another method, verify our data preserved
            self._context_stack[-1]._data["outer"] = "outer_value"

            # This creates its own context with its own data
            inner_result = self.process_with_data(99)

            # Our data should still be here
            self._context_stack[-1]._return = "outer_data=" + self._context_stack[-1]._data["outer"] + ",inner=" + inner_result
        elif __e._message == "process_with_data":
            value = __e._parameters["value"]
            # Set data in handler
            self._context_stack[-1]._data["input"] = self._context_stack[-1].event._parameters["value"]
            self._context_stack[-1]._data["trace"] = ["handler"]

            self._context_stack[-1]._return = "processed:" + str(self._context_stack[-1]._data["input"])
        elif __e._message == "transition_preserves_data":
            x = __e._parameters["x"]
            # Set data, transition, verify data available in lifecycle handlers
            self._context_stack[-1]._data["started_in"] = "Start"
            self._context_stack[-1]._data["value"] = str(self._context_stack[-1].event._parameters["x"])
            __compartment = ContextDataTestCompartment("End", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_End(self, __e):
        if __e._message == "$>":
            # Enter handler can access data set by previous handlers
            self._context_stack[-1]._data["ended_in"] = "End"

            # Build final result from accumulated data
            self._context_stack[-1]._return = f"from={self._context_stack[-1]._data["started_in"]},to={self._context_stack[-1]._data["ended_in"]},value={self._context_stack[-1]._data["value"]},exit_seen={self._context_stack[-1]._data["exit_seen"]}"


def main():
    print("=== Test 38: Context Data ===")

    # Test 1: Basic data set/get
    s1 = ContextDataTest()
    result = s1.process_with_data(42)
    assert result == "processed:42", f"Expected 'processed:42', got '{result}'"
    print(f"1. process_with_data(42) = '{result}'")

    # Test 2: Data isolation between nested calls
    s2 = ContextDataTest()
    result = s2.check_data_isolation()
    expected = "outer_data=outer_value,inner=processed:99"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"2. check_data_isolation() = '{result}'")

    # Test 3: Data preserved across transition (handler -> <$ -> $>)
    s3 = ContextDataTest()
    result = s3.transition_preserves_data(100)
    # Data should flow: handler sets -> exit accesses -> enter accesses and returns
    assert "from=Start" in result, f"Expected 'from=Start' in '{result}'"
    assert "to=End" in result, f"Expected 'to=End' in '{result}'"
    assert "value=100" in result, f"Expected 'value=100' in '{result}'"
    assert "exit_seen=true" in result, f"Expected 'exit_seen=true' in '{result}'"
    print(f"3. transition_preserves_data(100) = '{result}'")

    print("PASS: Context data works correctly")

if __name__ == '__main__':
    main()
