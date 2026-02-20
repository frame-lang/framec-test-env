from typing import Any, Optional, List, Dict, Callable

class WithTransition:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self._state = "First"
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

    def next(self):
        self._dispatch_event("next")

    def get_state(self) -> str:
        self._return_value = None
        self._dispatch_event("get_state")
        return self._return_value

    def _s_Second_next(self):
        print("Transitioning: Second -> First")
        self._transition("First", None, None)

    def _s_Second_get_state(self) -> str:
        self._return_value = "Second"
        return

    def _s_First_get_state(self) -> str:
        self._return_value = "First"
        return

    def _s_First_next(self):
        print("Transitioning: First -> Second")
        self._transition("Second", None, None)


def main():
    print("=== Test 03: State Transitions ===")
    s = WithTransition()

    # Initial state should be First
    state = s.get_state()
    assert state == "First", f"Expected 'First', got '{state}'"
    print(f"Initial state: {state}")

    # Transition to Second
    s.next()
    state = s.get_state()
    assert state == "Second", f"Expected 'Second', got '{state}'"
    print(f"After first next(): {state}")

    # Transition back to First
    s.next()
    state = s.get_state()
    assert state == "First", f"Expected 'First', got '{state}'"
    print(f"After second next(): {state}")

    print("PASS: State transitions work correctly")

if __name__ == '__main__':
    main()

