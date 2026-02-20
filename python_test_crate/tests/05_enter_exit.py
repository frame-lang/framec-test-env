from typing import Any, Optional, List, Dict, Callable

class EnterExit:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.log =         []
        self._state = "Off"
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

    def toggle(self):
        self._dispatch_event("toggle")

    def get_log(self) -> list:
        self._return_value = None
        self._dispatch_event("get_log")
        return self._return_value

    def _s_On_toggle(self):
        self._transition("Off", None, None)

    def _s_On_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_On_enter(self):
        self.log.append("enter:On")
        print("Entered On state")

    def _s_On_exit(self):
        self.log.append("exit:On")
        print("Exiting On state")

    def _s_Off_toggle(self):
        self._transition("On", None, None)

    def _s_Off_exit(self):
        self.log.append("exit:Off")
        print("Exiting Off state")

    def _s_Off_get_log(self) -> list:
        self._return_value = self.log
        return

    def _s_Off_enter(self):
        self.log.append("enter:Off")
        print("Entered Off state")


def main():
    print("=== Test 05: Enter/Exit Handlers ===")
    s = EnterExit()

    # Initial enter should have been called
    log = s.get_log()
    assert "enter:Off" in log, f"Expected 'enter:Off' in log, got {log}"
    print(f"After construction: {log}")

    # Toggle to On - should exit Off, enter On
    s.toggle()
    log = s.get_log()
    assert "exit:Off" in log, f"Expected 'exit:Off' in log, got {log}"
    assert "enter:On" in log, f"Expected 'enter:On' in log, got {log}"
    print(f"After toggle to On: {log}")

    # Toggle back to Off - should exit On, enter Off
    s.toggle()
    log = s.get_log()
    assert log.count("enter:Off") == 2, f"Expected 2 'enter:Off' entries, got {log}"
    assert "exit:On" in log, f"Expected 'exit:On' in log, got {log}"
    print(f"After toggle to Off: {log}")

    print("PASS: Enter/Exit handlers work correctly")

if __name__ == '__main__':
    main()

