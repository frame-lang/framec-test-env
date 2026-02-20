from typing import Any, Optional, List, Dict, Callable

class EventForwardTest:
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
        # No enter handlers
        pass

    def _exit(self, *args):
        # No exit handlers
        pass

    def process(self):
        self._dispatch_event("process")

    def get_log(self) -> list:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_Idle_process(self):
        self.log.append("idle:process:before")
        self._transition("Working", None, None)
        return self._dispatch_event("process")
        # This should NOT execute because -> => returns after dispatch
        self.log.append("idle:process:after")

    def _s_Idle_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Working_process(self):
        self.log.append("working:process")

    def _s_Working_get_log(self) -> list:
        self._return_value = self.log
        return


def main():
    print("=== Test 19: Transition Forward ===")
    s = EventForwardTest()
    s.process()
    log = s.get_log()
    print(f"Log: {log}")

    # After transition-forward:
    # - Idle logs "idle:process:before"
    # - Transition to Working
    # - Working handles process(), logs "working:process"
    # - Return prevents "idle:process:after"
    assert "idle:process:before" in log, f"Expected 'idle:process:before' in log: {log}"
    assert "working:process" in log, f"Expected 'working:process' in log: {log}"
    assert "idle:process:after" not in log, f"Should NOT have 'idle:process:after' in log: {log}"

    print("PASS: Transition forward works correctly")

if __name__ == '__main__':
    main()

