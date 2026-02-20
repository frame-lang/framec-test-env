from typing import Any, Optional, List, Dict, Callable

class StateVarBasic:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self._state = "Counter"
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
        if self._state == "Counter":
            self._state_context["count"] = 0


    def _exit(self, *args):
        # No exit handlers
        pass

    def increment(self) -> int:
        self._return_value = None
        self._dispatch_event("increment")
        return self._return_value

    def get_count(self) -> int:
        self._return_value = None
        self._dispatch_event("get_count")
        return self._return_value

    def reset(self):
        self._dispatch_event("reset")

    def _s_Counter_get_count(self) -> int:
        self._return_value = self._state_context["count"]
        return

    def _s_Counter_reset(self):
        self._state_context["count"] = 0

    def _s_Counter_increment(self) -> int:
        self._state_context["count"] = self._state_context["count"] + 1
        self._return_value = self._state_context["count"]
        return


def main():
    print("=== Test 10: State Variable Basic ===")
    s = StateVarBasic()

    # Initial value should be 0
    assert s.get_count() == 0, f"Expected 0, got {s.get_count()}"
    print(f"Initial count: {s.get_count()}")

    # Increment should return new value
    result = s.increment()
    assert result == 1, f"Expected 1 after first increment, got {result}"
    print(f"After first increment: {result}")

    # Second increment
    result = s.increment()
    assert result == 2, f"Expected 2 after second increment, got {result}"
    print(f"After second increment: {result}")

    # Reset should set back to 0
    s.reset()
    assert s.get_count() == 0, f"Expected 0 after reset, got {s.get_count()}"
    print(f"After reset: {s.get_count()}")

    print("PASS: State variable basic operations work correctly")

if __name__ == '__main__':
    main()

