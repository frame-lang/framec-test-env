from typing import Any, Optional, List, Dict, Callable

class PersistTest:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.value = 0
        self.name = "default"
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

    def set_value(self, v: int):
        self._dispatch_event("set_value", v)

    def get_value(self) -> int:
        self._return_value = None
        self._dispatch_event("get_value")
        return self._return_value

    def go_active(self):
        self._dispatch_event("go_active")

    def go_idle(self):
        self._dispatch_event("go_idle")

    def _s_Idle_set_value(self, v: int):
        self.value = v

    def _s_Idle_go_idle(self):
        pass  # Already idle

    def _s_Idle_get_value(self) -> int:
        self._return_value = self.value
        return

    def _s_Idle_go_active(self):
        self._transition("Active", None, None)

    def _s_Active_set_value(self, v: int):
        self.value = v * 2

    def _s_Active_get_value(self) -> int:
        self._return_value = self.value
        return

    def _s_Active_go_active(self):
        pass  # Already active

    def _s_Active_go_idle(self):
        self._transition("Idle", None, None)

    def save_state(self) -> bytes:
        import pickle
        return pickle.dumps(self)

    @staticmethod
    def restore_state(data: bytes) -> 'PersistTest':
        import pickle
        return pickle.loads(data)


def main():
    print("=== Test 23: Persist Basic (pickle) ===")

    # Test 1: Create and modify system
    s1 = PersistTest()
    s1.set_value(10)
    s1.go_active()
    s1.set_value(5)  # Should be doubled to 10 in Active state
    assert s1.get_value() == 10, f"Expected 10 after doubling, got {s1.get_value()}"

    # Test 2: Save state (returns bytes)
    data = s1.save_state()
    assert isinstance(data, bytes), f"Expected bytes, got {type(data)}"
    print(f"1. Saved state: {len(data)} bytes")

    # Test 3: Restore state
    s2 = PersistTest.restore_state(data)
    assert s2.get_value() == 10, f"Expected 10, got {s2.get_value()}"
    print(f"2. Restored value: {s2.get_value()}")

    # Test 4: Verify state is preserved (Active state doubles)
    s2.set_value(3)  # Should be doubled to 6 in Active state
    assert s2.get_value() == 6, f"Expected 6, got {s2.get_value()}"
    print(f"3. After set_value(3) in Active: {s2.get_value()}")

    # Test 5: Verify transitions work after restore
    s2.go_idle()
    s2.set_value(4)  # Should NOT be doubled in Idle state
    assert s2.get_value() == 4, f"Expected 4, got {s2.get_value()}"
    print(f"4. After go_idle, set_value(4): {s2.get_value()}")

    print("PASS: Persist basic works correctly")

if __name__ == '__main__':
    main()

