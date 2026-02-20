from typing import Any, Optional, List, Dict, Callable

class WithInterface:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.call_count = 0
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

    def greet(self, name: str) -> str:
        self._return_value = None
        self._dispatch_event("greet", name)
        return self._return_value

    def get_count(self) -> int:
        self._return_value = None
        self._dispatch_event("get_count")
        return self._return_value

    def _s_Ready_greet(self, name: str) -> str:
        self.call_count += 1
        self._return_value = f"Hello, {name}!"
        return

    def _s_Ready_get_count(self) -> int:
        self._return_value = self.call_count
        return


def main():
    print("=== Test 02: Interface Methods ===")
    s = WithInterface()

    # Test interface method with parameter and return
    result = s.greet("World")
    assert result == "Hello, World!", f"Expected 'Hello, World!', got '{result}'"
    print(f"greet('World') = {result}")

    # Test domain variable access through interface
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"
    print(f"get_count() = {count}")

    # Call again to verify state
    s.greet("Frame")
    count2 = s.get_count()
    assert count2 == 2, f"Expected count=2, got {count2}"
    print(f"After second call: get_count() = {count2}")

    print("PASS: Interface methods work correctly")

if __name__ == '__main__':
    main()

