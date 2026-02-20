from typing import Any, Optional, List, Dict, Callable

class SystemReturnChainTest:
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
        handler_name = f"_s_{self._state}_enter"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(*args)

    def _exit(self, *args):
        handler_name = f"_s_{self._state}_exit"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(*args)

    def test_enter_sets(self) -> str:
        self._return_value = None
        self._dispatch_event("test_enter_sets")
        return self._return_value

    def test_exit_then_enter(self) -> str:
        self._return_value = None
        self._dispatch_event("test_exit_then_enter")
        return self._return_value

    def get_state(self) -> str:
        self._return_value = None
        self._dispatch_event("get_state")
        return self._return_value

    def _s_BothSet_enter(self):
        # Enter handler sets return - should overwrite exit's value
        self._return_value = "enter_wins"

    def _s_BothSet_get_state(self) -> str:
        self._return_value = "BothSet"
        return

    def _s_Start_get_state(self) -> str:
        self._return_value = "Start"
        return

    def _s_Start_test_enter_sets(self) -> str:
        self._transition("EnterSetter", None, None)

    def _s_Start_test_exit_then_enter(self) -> str:
        self._transition("BothSet", None, None)

    def _s_Start_exit(self):
        # Exit handler sets initial value
        self._return_value = "from_exit"

    def _s_EnterSetter_get_state(self) -> str:
        self._return_value = "EnterSetter"
        return

    def _s_EnterSetter_enter(self):
        # Enter handler sets return value
        self._return_value = "from_enter"


def main():
    print("=== Test 15: System Return Chain (Last Writer Wins) ===")

    # Test 1: Start exit + EnterSetter enter
    # Start's exit sets "from_exit", EnterSetter's enter sets "from_enter"
    # Enter should win (last writer)
    s1 = SystemReturnChainTest()
    result = s1.test_enter_sets()
    assert result == "from_enter", f"Expected 'from_enter', got '{result}'"
    assert s1.get_state() == "EnterSetter", f"Expected state 'EnterSetter'"
    print(f"1. Exit set then enter set - enter wins: '{result}'")

    # Test 2: Both handlers set, enter wins
    s2 = SystemReturnChainTest()
    result = s2.test_exit_then_enter()
    assert result == "enter_wins", f"Expected 'enter_wins', got '{result}'"
    assert s2.get_state() == "BothSet", f"Expected state 'BothSet'"
    print(f"2. Both set - enter wins: '{result}'")

    print("PASS: System return chain (last writer wins) works correctly")

if __name__ == '__main__':
    main()

