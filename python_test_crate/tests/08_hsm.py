from typing import Any, Optional, List, Dict, Callable

class HSMForward:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.log =         []
        self._state = "Child"
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

    def event_a(self):
        self._dispatch_event("event_a")

    def event_b(self):
        self._dispatch_event("event_b")

    def get_log(self) -> list:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_Child_event_a(self):
        self.log.append("Child:event_a")

    def _s_Child_event_b(self):
        self.log.append("Child:event_b_forward")
        self._s_Parent_event_b()

    def _s_Child_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Parent_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Parent_event_a(self):
        self.log.append("Parent:event_a")

    def _s_Parent_event_b(self):
        self.log.append("Parent:event_b")


def main():
    print("=== Test 08: HSM Forward ===")
    s = HSMForward()

    # event_a should be handled by Child (no forward)
    s.event_a()
    log = s.get_log()
    assert "Child:event_a" in log, f"Expected 'Child:event_a' in log, got {log}"
    print(f"After event_a: {log}")

    # event_b should forward to Parent
    s.event_b()
    log = s.get_log()
    assert "Child:event_b_forward" in log, f"Expected 'Child:event_b_forward' in log, got {log}"
    assert "Parent:event_b" in log, f"Expected 'Parent:event_b' in log (forwarded), got {log}"
    print(f"After event_b (forwarded): {log}")

    print("PASS: HSM forward works correctly")

if __name__ == '__main__':
    main()

