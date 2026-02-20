from typing import Any, Optional, List, Dict, Callable

class TransitionPopTest:
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

    def start(self):
        self._dispatch_event("start")

    def process(self):
        self._dispatch_event("process")

    def get_state(self) -> str:
        self._return_value = None
        self._dispatch_event("get_state")
        return self._return_value

    def get_log(self) -> list:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_Working_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Working_get_state(self) -> str:
        self._return_value = "Working"
        return

    def _s_Working_process(self):
        self.log.append("working:process:before_pop")
        __saved = self._state_stack.pop()
        self._exit()
        self._state = __saved[0]
        self._state_context = __saved[1]
        return
        # This should NOT execute because pop transitions away
        self.log.append("working:process:after_pop")

    def _s_Idle_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Idle_process(self):
        self.log.append("idle:process")

    def _s_Idle_get_state(self) -> str:
        self._return_value = "Idle"
        return

    def _s_Idle_start(self):
        self.log.append("idle:start:push")
        self._state_stack.append((self._state, self._state_context.copy()))
        self._transition("Working", None, None)


def main():
    print("=== Test 20: Transition Pop ===")
    s = TransitionPopTest()

    # Initial state should be Idle
    assert s.get_state() == "Idle", f"Expected 'Idle', got '{s.get_state()}'"
    print(f"Initial state: {s.get_state()}")

    # start() pushes Idle, transitions to Working
    s.start()
    assert s.get_state() == "Working", f"Expected 'Working', got '{s.get_state()}'"
    print(f"After start(): {s.get_state()}")

    # process() in Working does pop transition back to Idle
    s.process()
    assert s.get_state() == "Idle", f"Expected 'Idle' after pop, got '{s.get_state()}'"
    print(f"After process() with pop: {s.get_state()}")

    log = s.get_log()
    print(f"Log: {log}")

    # Verify log contents
    assert "idle:start:push" in log, f"Expected 'idle:start:push' in log"
    assert "working:process:before_pop" in log, f"Expected 'working:process:before_pop' in log"
    assert "working:process:after_pop" not in log, f"Should NOT have 'working:process:after_pop' in log"

    print("PASS: Transition pop works correctly")

if __name__ == '__main__':
    main()

