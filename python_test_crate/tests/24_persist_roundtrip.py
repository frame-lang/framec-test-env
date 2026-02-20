from typing import Any, Optional, List, Dict, Callable

class PersistRoundtrip:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.counter = 0
        self.history =         []
        self.mode = "normal"
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

    def go_active(self):
        self._dispatch_event("go_active")

    def go_idle(self):
        self._dispatch_event("go_idle")

    def get_state(self) -> str:
        self._return_value = None
        self._dispatch_event("get_state")
        return self._return_value

    def set_counter(self, n: int):
        self._dispatch_event("set_counter", n)

    def get_counter(self) -> int:
        self._return_value = None
        self._dispatch_event("get_counter")
        return self._return_value

    def add_history(self, msg: str):
        self._dispatch_event("add_history", msg)

    def _s_Idle_add_history(self, msg: str):
        self.history.append("idle:" + msg)

    def _s_Idle_get_counter(self) -> int:
        self._return_value = self.counter
        return

    def _s_Idle_go_active(self):
        self.history.append("idle->active")
        self._transition("Active", None, None)

    def _s_Idle_go_idle(self):
        pass  # already idle

    def _s_Idle_get_state(self) -> str:
        self._return_value = "idle"
        return

    def _s_Idle_set_counter(self, n: int):
        self.counter = n

    def _s_Active_set_counter(self, n: int):
        self.counter = n * 2

    def _s_Active_add_history(self, msg: str):
        self.history.append("active:" + msg)

    def _s_Active_get_counter(self) -> int:
        self._return_value = self.counter
        return

    def _s_Active_go_active(self):
        pass  # already active

    def _s_Active_go_idle(self):
        self.history.append("active->idle")
        self._transition("Idle", None, None)

    def _s_Active_get_state(self) -> str:
        self._return_value = "active"
        return

    def save_state(self) -> bytes:
        import pickle
        return pickle.dumps(self)

    @staticmethod
    def restore_state(data: bytes) -> 'PersistRoundtrip':
        import pickle
        return pickle.loads(data)


def main():
    print("=== Test 24: Persist Roundtrip (pickle) ===")

    # Test 1: Create system and build up state
    s1 = PersistRoundtrip()
    s1.set_counter(5)
    s1.add_history("start")
    s1.go_active()
    s1.set_counter(3)  # Should be 6 in Active (doubled)
    s1.add_history("work")

    assert s1.get_state() == "active", f"Expected active, got {s1.get_state()}"
    assert s1.get_counter() == 6, f"Expected 6, got {s1.get_counter()}"
    print(f"1. State before save: state={s1.get_state()}, counter={s1.get_counter()}")
    print(f"   History: {s1.history}")

    # Test 2: Save state (returns bytes)
    data = s1.save_state()
    assert isinstance(data, bytes), f"Expected bytes, got {type(data)}"
    print(f"2. Saved: {len(data)} bytes")

    # Test 3: Restore to new instance
    s2 = PersistRoundtrip.restore_state(data)

    # Verify restored state matches
    assert s2.get_state() == "active", f"Expected active, got {s2.get_state()}"
    assert s2.get_counter() == 6, f"Expected 6, got {s2.get_counter()}"
    print(f"3. Restored state: state={s2.get_state()}, counter={s2.get_counter()}")

    # Test 4: State machine continues to work after restore
    s2.set_counter(2)  # Should be 4 in Active (doubled)
    assert s2.get_counter() == 4, f"Expected 4, got {s2.get_counter()}"
    print(f"4. Counter after set_counter(2): {s2.get_counter()}")

    # Test 5: Verify history was preserved
    assert s2.history == s1.history, f"History mismatch: {s2.history} vs {s1.history}"
    print(f"5. History preserved: {s2.history}")

    # Test 6: Transitions work after restore
    s2.go_idle()
    assert s2.get_state() == "idle", f"Expected idle after go_idle"
    s2.set_counter(10)  # Not doubled in Idle
    assert s2.get_counter() == 10, f"Expected 10, got {s2.get_counter()}"
    print(f"6. After go_idle: state={s2.get_state()}, counter={s2.get_counter()}")

    print("PASS: Persist roundtrip works correctly")

if __name__ == '__main__':
    main()

