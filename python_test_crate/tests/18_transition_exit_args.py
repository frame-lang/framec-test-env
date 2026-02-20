from typing import Any, Optional, List, Dict, Callable

class TransitionExitArgs:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.log =         []
        self._state = "Active"
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

    def leave(self):
        self._dispatch_event("leave")

    def get_log(self) -> list:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_Active_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Active_leave(self):
        self.log.append("leaving")
        self._transition("Done", ("cleanup", 42,), None)

    def _s_Active_exit(self, reason: str, code: int):
        self.log.append(f"exit:{reason}:{code}")

    def _s_Done_enter(self):
        self.log.append("enter:done")

    def _s_Done_get_log(self) -> list:
        self._return_value = self.log
        return


def main():
    print("=== Test 18: Transition Exit Args ===")
    s = TransitionExitArgs()

    # Initial state is Active
    log = s.get_log()
    assert log == [], f"Expected empty log, got {log}"

    # Leave - should call exit handler with args
    s.leave()
    log = s.get_log()
    assert "leaving" in log, f"Expected 'leaving' in log, got {log}"
    assert "exit:cleanup:42" in log, f"Expected 'exit:cleanup:42' in log, got {log}"
    assert "enter:done" in log, f"Expected 'enter:done' in log, got {log}"
    print(f"Log after transition: {log}")

    print("PASS: Transition exit args work correctly")

if __name__ == '__main__':
    main()

