from typing import Any, Optional, List, Dict, Callable

class PersistStack:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self.depth = 0
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
        # No enter handlers
        pass

    def _exit(self, *args):
        # No exit handlers
        pass

    def push_and_go(self):
        self._dispatch_event("push_and_go")

    def pop_back(self):
        self._dispatch_event("pop_back")

    def get_state(self) -> str:
        self._return_value = None
        self._dispatch_event("get_state")
        return self._return_value

    def get_depth(self) -> int:
        self._return_value = None
        self._dispatch_event("get_depth")
        return self._return_value

    def _s_Start_get_state(self) -> str:
        self._return_value = "start"
        return

    def _s_Start_get_depth(self) -> int:
        self._return_value = self.depth
        return

    def _s_Start_push_and_go(self):
        self.depth = self.depth + 1
        self._state_stack.append((self._state, self._state_context.copy()))
        self._transition("Middle", None, None)

    def _s_Start_pop_back(self):
        pass  # nothing to pop

    def _s_End_get_depth(self) -> int:
        self._return_value = self.depth
        return

    def _s_End_get_state(self) -> str:
        self._return_value = "end"
        return

    def _s_End_push_and_go(self):
        pass  # can't go further

    def _s_End_pop_back(self):
        self.depth = self.depth - 1
        __saved = self._state_stack.pop()
        self._exit()
        self._state = __saved[0]
        self._state_context = __saved[1]
        return

    def _s_Middle_push_and_go(self):
        self.depth = self.depth + 1
        self._state_stack.append((self._state, self._state_context.copy()))
        self._transition("End", None, None)

    def _s_Middle_pop_back(self):
        self.depth = self.depth - 1
        __saved = self._state_stack.pop()
        self._exit()
        self._state = __saved[0]
        self._state_context = __saved[1]
        return

    def _s_Middle_get_depth(self) -> int:
        self._return_value = self.depth
        return

    def _s_Middle_get_state(self) -> str:
        self._return_value = "middle"
        return

    def save_state(self) -> bytes:
        import pickle
        return pickle.dumps(self)

    @staticmethod
    def restore_state(data: bytes) -> 'PersistStack':
        import pickle
        return pickle.loads(data)


def main():
    print("=== Test 25: Persist Stack (pickle) ===")

    # Test 1: Build up a stack
    s1 = PersistStack()
    assert s1.get_state() == "start", f"Expected start, got {s1.get_state()}"

    s1.push_and_go()  # Start -> Middle (push Start)
    assert s1.get_state() == "middle", f"Expected middle, got {s1.get_state()}"
    assert s1.get_depth() == 1, f"Expected depth 1, got {s1.get_depth()}"

    s1.push_and_go()  # Middle -> End (push Middle)
    assert s1.get_state() == "end", f"Expected end, got {s1.get_state()}"
    assert s1.get_depth() == 2, f"Expected depth 2, got {s1.get_depth()}"

    print(f"1. Built stack: state={s1.get_state()}, depth={s1.get_depth()}")

    # Test 2: Save state (should include stack)
    data = s1.save_state()
    assert isinstance(data, bytes), f"Expected bytes, got {type(data)}"
    print(f"2. Saved: {len(data)} bytes")

    # Test 3: Restore and verify stack works
    s2 = PersistStack.restore_state(data)
    assert s2.get_state() == "end", f"Restored: expected end, got {s2.get_state()}"
    assert s2.get_depth() == 2, f"Restored: expected depth 2, got {s2.get_depth()}"
    print(f"3. Restored: state={s2.get_state()}, depth={s2.get_depth()}")

    # Test 4: Pop should work after restore
    s2.pop_back()  # End -> Middle (pop)
    assert s2.get_state() == "middle", f"After pop: expected middle, got {s2.get_state()}"
    assert s2.get_depth() == 1, f"After pop: expected depth 1, got {s2.get_depth()}"
    print(f"4. After pop: state={s2.get_state()}, depth={s2.get_depth()}")

    # Test 5: Pop again
    s2.pop_back()  # Middle -> Start (pop)
    assert s2.get_state() == "start", f"After 2nd pop: expected start, got {s2.get_state()}"
    assert s2.get_depth() == 0, f"After 2nd pop: expected depth 0, got {s2.get_depth()}"
    print(f"5. After 2nd pop: state={s2.get_state()}, depth={s2.get_depth()}")

    print("PASS: Persist stack works correctly")

if __name__ == '__main__':
    main()

