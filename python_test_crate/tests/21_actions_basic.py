from typing import Any, Optional, List, Dict, Callable

class ActionsTest:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.log = ""
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

    def process(self, value: int) -> int:
        self._return_value = None
        self._dispatch_event("process", value)
        return self._return_value

    def get_log(self) -> str:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_Ready_process(self, value: int) -> int:
        self.__log_event("start")
        self.__validate_positive(value)
        self.__log_event("valid")
        result = value * 2
        self.__log_event("done")
        self._return_value = result
        return

    def _s_Ready_get_log(self) -> str:
        self._return_value = self.log
        return

    def __log_event(self, msg: str):
        self.log = self.log + msg + ";"

    def __validate_positive(self, n: int):
        if n < 0:
            raise ValueError(f"Value must be positive: {n}")


def main():
    print("=== Test 21: Actions Basic ===")
    s = ActionsTest()

    # Test 1: Actions are called correctly
    result = s.process(5)
    assert result == 10, f"Expected 10, got {result}"
    print(f"1. process(5) = {result}")

    # Test 2: Log shows action calls
    log = s.get_log()
    assert "start" in log, f"Missing 'start' in log: {log}"
    assert "valid" in log, f"Missing 'valid' in log: {log}"
    assert "done" in log, f"Missing 'done' in log: {log}"
    print(f"2. Log: {log}")

    # Test 3: Action with validation
    try:
        s.process(-1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"3. Validation caught: {e}")

    print("PASS: Actions basic works correctly")

if __name__ == '__main__':
    main()

