from typing import Any, Optional, List, Dict, Callable

class OperationsTest:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.last_result = 0
        self._state = "Ready"
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

    def compute(self, a: int, b: int) -> int:
        self._return_value = None
        self._dispatch_event("compute", a, b)
        return self._return_value

    def get_last_result(self) -> int:
        self._return_value = None
        self._dispatch_event("get_last_result")
        return self._return_value

    def _s_Ready_compute(self, a: int, b: int) -> int:
        # Use instance operations
        sum_val = self.add(a, b)
        prod_val = self.multiply(a, b)
        last_result = sum_val + prod_val
        self._return_value = last_result
        return

    def _s_Ready_get_last_result(self) -> int:
        self._return_value = last_result
        return

    def add(self, x: int, y: int) -> int:
        return x + y

    def multiply(self, x: int, y: int) -> int:
        return x * y

    @staticmethod
    def factorial(n: int) -> int:
        if n <= 1:
            return 1
        return n * OperationsTest.factorial(n - 1)

    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0


def main():
    print("=== Test 22: Operations Basic ===")
    s = OperationsTest()

    # Test 1: Instance operations
    result = s.add(3, 4)
    assert result == 7, f"Expected 7, got {result}"
    print(f"1. add(3, 4) = {result}")

    result = s.multiply(3, 4)
    assert result == 12, f"Expected 12, got {result}"
    print(f"2. multiply(3, 4) = {result}")

    # Test 2: Operations used in handler
    result = s.compute(3, 4)
    # compute returns add(3,4) + multiply(3,4) = 7 + 12 = 19
    assert result == 19, f"Expected 19, got {result}"
    print(f"3. compute(3, 4) = {result}")

    # Test 3: Static operations
    result = OperationsTest.factorial(5)
    assert result == 120, f"Expected 120, got {result}"
    print(f"4. factorial(5) = {result}")

    result = OperationsTest.is_even(4)
    assert result == True, f"Expected True, got {result}"
    print(f"5. is_even(4) = {result}")

    result = OperationsTest.is_even(7)
    assert result == False, f"Expected False, got {result}"
    print(f"6. is_even(7) = {result}")

    # Test 4: Static can also be called on instance
    result = s.factorial(4)
    assert result == 24, f"Expected 24, got {result}"
    print(f"7. instance.factorial(4) = {result}")

    print("PASS: Operations basic works correctly")

if __name__ == '__main__':
    main()

