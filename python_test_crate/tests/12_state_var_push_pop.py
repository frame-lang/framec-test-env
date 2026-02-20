from typing import Any, Optional, List, Dict, Callable

class StateVarPushPop:
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
        elif self._state == "Other":
            self._state_context["other_count"] = 100


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

    def save_and_go(self):
        self._dispatch_event("save_and_go")

    def restore(self):
        self._dispatch_event("restore")

    def _s_Counter_save_and_go(self):
        self._state_stack.append((self._state, self._state_context.copy()))
        self._transition("Other", None, None)

    def _s_Counter_increment(self) -> int:
        self._state_context["count"] = self._state_context["count"] + 1
        self._return_value = self._state_context["count"]
        return

    def _s_Counter_get_count(self) -> int:
        self._return_value = self._state_context["count"]
        return

    def _s_Other_restore(self):
        __saved = self._state_stack.pop()
        self._exit()
        self._state = __saved[0]
        self._state_context = __saved[1]
        return

    def _s_Other_get_count(self) -> int:
        self._return_value = self._state_context["other_count"]
        return

    def _s_Other_increment(self) -> int:
        self._state_context["other_count"] = self._state_context["other_count"] + 1
        self._return_value = self._state_context["other_count"]
        return


def main():
    print("=== Test 12: State Variable Push/Pop ===")
    s = StateVarPushPop()

    # Increment counter to 3
    s.increment()
    s.increment()
    s.increment()
    count = s.get_count()
    assert count == 3, f"Expected 3, got {count}"
    print(f"Counter before push: {count}")

    # Push and go to Other state
    s.save_and_go()
    print("Pushed and transitioned to Other")

    # In Other state, count should be 100 (Other's state var)
    count = s.get_count()
    assert count == 100, f"Expected 100 in Other state, got {count}"
    print(f"Other state count: {count}")

    # Increment in Other
    s.increment()
    count = s.get_count()
    assert count == 101, f"Expected 101 after increment, got {count}"
    print(f"Other state after increment: {count}")

    # Pop back - should restore Counter with count=3
    s.restore()
    print("Popped back to Counter")

    count = s.get_count()
    assert count == 3, f"Expected 3 after pop (preserved), got {count}"
    print(f"Counter after pop: {count}")

    # Increment to verify it works
    s.increment()
    count = s.get_count()
    assert count == 4, f"Expected 4, got {count}"
    print(f"Counter after increment: {count}")

    print("PASS: State variables preserved across push/pop")

if __name__ == '__main__':
    main()

