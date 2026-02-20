from typing import Any, Optional, List, Dict, Callable

class StateVarReentry:
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

    def go_other(self):
        self._dispatch_event("go_other")

    def come_back(self):
        self._dispatch_event("come_back")

    def _s_Counter_go_other(self):
        self._transition("Other", None, None)

    def _s_Counter_increment(self) -> int:
        self._state_context["count"] = self._state_context["count"] + 1
        self._return_value = self._state_context["count"]
        return

    def _s_Counter_get_count(self) -> int:
        self._return_value = self._state_context["count"]
        return

    def _s_Other_come_back(self):
        self._transition("Counter", None, None)

    def _s_Other_increment(self) -> int:
        self._return_value = -1
        return

    def _s_Other_get_count(self) -> int:
        self._return_value = -1
        return


def main():
    print("=== Test 11: State Variable Reentry ===")
    s = StateVarReentry()

    # Increment a few times
    s.increment()
    s.increment()
    count = s.get_count()
    assert count == 2, f"Expected 2 after two increments, got {count}"
    print(f"Count before leaving: {count}")

    # Leave the state
    s.go_other()
    print("Transitioned to Other state")

    # Come back - state var should be reinitialized to 0
    s.come_back()
    count = s.get_count()
    assert count == 0, f"Expected 0 after re-entering Counter (state var reinit), got {count}"
    print(f"Count after re-entering Counter: {count}")

    # Increment again to verify it works
    result = s.increment()
    assert result == 1, f"Expected 1 after increment, got {result}"
    print(f"After increment: {result}")

    print("PASS: State variables reinitialize on state reentry")

if __name__ == '__main__':
    main()

