from typing import Any, Optional, List, Dict, Callable

class SystemReturnReentrantTest:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self._state = "Start"
        self._enter()

    def _transition(self, target_state, exit_args = None, enter_args = None):
        if exit_args:
            self._exit(*exit_args)
        else:
            self._exit()
        self._state = target_state
        if enter_args:
            self._enter(*enter_args)
        else:
            self._enter()

    def _change_state(self, target_state):
        self._state = target_state

    def _dispatch_event(self, event, *args):
        handler_name = f"_s_{self._state}_{event}"
        handler = getattr(self, handler_name, None)
        if handler:
            return handler(*args)

    def _enter(self, *args):
        if self._state == "Start":
            self._state_context["log"] = ""


    def _exit(self, *args):
        # No exit handlers
        pass

    def outer_call(self) -> str:
        self._return_value = None
        self._dispatch_event("outer_call")
        return self._return_value

    def inner_call(self) -> str:
        self._return_value = None
        self._dispatch_event("inner_call")
        return self._return_value

    def nested_call(self) -> str:
        self._return_value = None
        self._dispatch_event("nested_call")
        return self._return_value

    def get_log(self) -> str:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_Start_outer_call(self) -> str:
        self._state_context["log"] = self._state_context["log"] + "outer_start,"
        # Call inner method - this creates nested return context
        inner_result = self.inner_call()
        self._state_context["log"] = self._state_context["log"] + "outer_after_inner,"
        # Our return should be independent of inner's return
        self._return_value = "outer_result:" + inner_result
        return

    def _s_Start_nested_call(self) -> str:
        self._state_context["log"] = self._state_context["log"] + "nested_start,"
        # Two levels of nesting
        result1 = self.inner_call()
        result2 = self.outer_call()
        self._state_context["log"] = self._state_context["log"] + "nested_end,"
        self._return_value = "nested:" + result1 + "+" + result2
        return

    def _s_Start_inner_call(self) -> str:
        self._state_context["log"] = self._state_context["log"] + "inner,"
        self._return_value = "inner_result"
        return

    def _s_Start_get_log(self) -> str:
        self._return_value = self._state_context["log"]
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

