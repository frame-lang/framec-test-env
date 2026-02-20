from typing import Any, Optional, List, Dict, Callable

class SystemReturnDefaultTest:
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
            self._state_context["count"] = 0


    def _exit(self, *args):
        # No exit handlers
        pass

    def handler_sets_value(self) -> str:
        self._return_value = None
        self._dispatch_event("handler_sets_value")
        return self._return_value

    def handler_no_return(self) -> str:
        self._return_value = None
        self._dispatch_event("handler_no_return")
        return self._return_value

    def get_count(self) -> int:
        self._return_value = None
        self._dispatch_event("get_count")
        return self._return_value

    def _s_Start_handler_sets_value(self) -> str:
        self._return_value = "set_by_handler"
        return

    def _s_Start_get_count(self) -> int:
        self._return_value = self._state_context["count"]
        return

    def _s_Start_handler_no_return(self) -> str:
        # Does not set return - should return None
        self._state_context["count"] = self._state_context["count"] + 1


def main():
    print("=== Test 14: System Return Default Behavior ===")
    s = SystemReturnDefaultTest()

    # Test 1: Handler explicitly sets return value
    result = s.handler_sets_value()
    assert result == "set_by_handler", f"Expected 'set_by_handler', got '{result}'"
    print(f"1. handler_sets_value() = '{result}'")

    # Test 2: Handler does NOT set return - should return None
    result = s.handler_no_return()
    assert result is None, f"Expected None, got '{result}'"
    print(f"2. handler_no_return() = {result}")

    # Test 3: Verify handler was called (side effect check)
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"
    print(f"3. Handler was called, count = {count}")

    # Test 4: Call again to verify idempotence
    result = s.handler_no_return()
    assert result is None, f"Expected None again, got '{result}'"
    count = s.get_count()
    assert count == 2, f"Expected count=2, got {count}"
    print(f"4. Second call: result={result}, count={count}")

    print("PASS: System return default behavior works correctly")

if __name__ == '__main__':
    main()

