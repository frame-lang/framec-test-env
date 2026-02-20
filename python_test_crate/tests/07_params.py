from typing import Any, Optional, List, Dict, Callable

class WithParams:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.total = 0
        self._state = "Idle"
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

    def start(self, initial: int):
        self._dispatch_event("start", initial)

    def add(self, value: int):
        self._dispatch_event("add", value)

    def multiply(self, a: int, b: int) -> int:
        self._return_value = None
        self._dispatch_event("multiply", a, b)
        return self._return_value

    def get_total(self) -> int:
        self._return_value = None
        self._dispatch_event("get_total")
        return self._return_value

    def _s_Running_start(self, initial: int):
        print("Already running")

    def _s_Running_add(self, value: int):
        self.total += value
        print(f"Added {value}, total is now {self.total}")

    def _s_Running_multiply(self, a: int, b: int) -> int:
        result = a * b
        self.total += result
        print(f"Multiplied {a} * {b} = {result}, total is now {self.total}")
        self._return_value = result
        return

    def _s_Running_get_total(self) -> int:
        self._return_value = self.total
        return

    def _s_Idle_multiply(self, a: int, b: int) -> int:
        self._return_value = 0
        return

    def _s_Idle_add(self, value: int):
        print("Cannot add in Idle state")

    def _s_Idle_get_total(self) -> int:
        self._return_value = self.total
        return

    def _s_Idle_start(self, initial: int):
        self.total = initial
        print(f"Started with initial value: {initial}")
        self._transition("Running", None, None)


def main():
    print("=== Test 07: Handler Parameters ===")
    s = WithParams()

    # Initial total should be 0
    total = s.get_total()
    assert total == 0, f"Expected initial total=0, got {total}"

    # Start with initial value
    s.start(100)
    total = s.get_total()
    assert total == 100, f"Expected total=100, got {total}"
    print(f"After start(100): total = {total}")

    # Add value
    s.add(25)
    total = s.get_total()
    assert total == 125, f"Expected total=125, got {total}"
    print(f"After add(25): total = {total}")

    # Multiply with two params
    result = s.multiply(3, 5)
    assert result == 15, f"Expected multiply result=15, got {result}"
    total = s.get_total()
    assert total == 140, f"Expected total=140, got {total}"
    print(f"After multiply(3,5): result = {result}, total = {total}")

    print("PASS: Handler parameters work correctly")

if __name__ == '__main__':
    main()

