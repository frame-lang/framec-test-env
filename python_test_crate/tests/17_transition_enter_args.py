from typing import Any, Optional, List, Dict, Callable

class TransitionEnterArgs:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.log =         []
        self._state = "Idle"
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
        # No exit handlers
        pass

    def start(self):
        self._dispatch_event("start")

    def get_log(self) -> list:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_Active_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Active_start(self):
        self.log.append("active:start")

    def _s_Active_enter(self, source: str, value: int):
        self.log.append(f"active:enter:{source}:{value}")

    def _s_Idle_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Idle_start(self):
        self.log.append("idle:start")
        self._transition("Active", None, ("from_idle", 42,))


def main():
    print("=== Test 17: Transition Enter Args ===")
    s = TransitionEnterArgs()

    # Initial state is Idle
    log = s.get_log()
    assert log == [], f"Expected empty log, got {log}"

    # Transition to Active with args
    s.start()
    log = s.get_log()
    assert "idle:start" in log, f"Expected 'idle:start' in log, got {log}"
    assert "active:enter:from_idle:42" in log, f"Expected 'active:enter:from_idle:42' in log, got {log}"
    print(f"Log after transition: {log}")

    print("PASS: Transition enter args work correctly")

if __name__ == '__main__':
    main()

