
import math

def helper_function(x):
    """Native helper function defined before system"""
    return x * 2


from typing import Any, Optional, List, Dict, Callable

class NativeCode:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self._state = "Active"
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
        # No enter handlers
        pass

    def _exit(self, *args):
        # No exit handlers
        pass

    def compute(self, value: int) -> int:
        self._return_value = None
        self._dispatch_event("compute", value)
        return self._return_value

    def use_math(self) -> float:
        self._return_value = None
        self._dispatch_event("use_math")
        return self._return_value

    def _s_Active_use_math(self) -> float:
        # Using imported math module
        result = math.sqrt(16) + math.pi
        print(f"Math result: {result}")
        self._return_value = result
        return

    def _s_Active_compute(self, value: int) -> int:
        # Native code with local variables
        temp = value + 10
        result = helper_function(temp)
        print(f"Computed: {value} -> {result}")
        self._return_value = result
        return


def main():
    print("=== Test 04: Native Code Preservation ===")
    s = NativeCode()

    # Test native code in handler with helper function
    result = s.compute(5)
    expected = (5 + 10) * 2  # 30
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"compute(5) = {result}")

    # Test imported module usage
    math_result = s.use_math()
    expected_math = math.sqrt(16) + math.pi
    assert abs(math_result - expected_math) < 0.001, f"Expected ~{expected_math}, got {math_result}"
    print(f"use_math() = {math_result}")

    print("PASS: Native code preservation works correctly")

if __name__ == '__main__':
    main()

