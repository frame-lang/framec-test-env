from typing import Any, Optional, List, Dict, Callable

class DomainVars:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.count = 0
        self.name = "counter"
        self._state = "Counting"
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

    def increment(self):
        self._dispatch_event("increment")

    def decrement(self):
        self._dispatch_event("decrement")

    def get_count(self) -> int:
        self._return_value = None
        self._dispatch_event("get_count")
        return self._return_value

    def set_count(self, value: int):
        self._dispatch_event("set_count", value)

    def _s_Counting_get_count(self) -> int:
        self._return_value = self.count
        return

    def _s_Counting_set_count(self, value: int):
        self.count = value
        print(f"{self.name}: set to {self.count}")

    def _s_Counting_increment(self):
        self.count += 1
        print(f"{self.name}: incremented to {self.count}")

    def _s_Counting_decrement(self):
        self.count -= 1
        print(f"{self.name}: decremented to {self.count}")


def main():
    print("=== Test 06: Domain Variables ===")
    s = DomainVars()

    # Initial value should be 0
    count = s.get_count()
    assert count == 0, f"Expected initial count=0, got {count}"
    print(f"Initial count: {count}")

    # Increment
    s.increment()
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"

    s.increment()
    count = s.get_count()
    assert count == 2, f"Expected count=2, got {count}"

    # Decrement
    s.decrement()
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"

    # Set directly
    s.set_count(100)
    count = s.get_count()
    assert count == 100, f"Expected count=100, got {count}"

    print(f"Final count: {count}")
    print("PASS: Domain variables work correctly")

if __name__ == '__main__':
    main()

