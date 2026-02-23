from typing import Any, Optional, List, Dict, Callable

class PersistRoundtripFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class PersistRoundtripFrameContext:
    def __init__(self, event: PersistRoundtripFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class PersistRoundtripCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'PersistRoundtripCompartment':
        c = PersistRoundtripCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class PersistRoundtrip:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.counter = 0
        self.history =         []
        self.mode = "normal"
        self.__compartment = PersistRoundtripCompartment("Idle")
        self.__next_compartment = None
        __frame_event = PersistRoundtripFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = PersistRoundtripFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = PersistRoundtripFrameEvent("$>", self.__compartment.enter_args)
                self.__router(enter_event)
            else:
                # Forward event to new state
                forward_event = next_compartment.forward_event
                next_compartment.forward_event = None
                if forward_event._message == "$>":
                    # Forwarding enter event - just send it
                    self.__router(forward_event)
                else:
                    # Forwarding other event - send $> first, then forward
                    enter_event = PersistRoundtripFrameEvent("$>", self.__compartment.enter_args)
                    self.__router(enter_event)
                    self.__router(forward_event)

    def __router(self, __e):
        state_name = self.__compartment.state
        handler_name = f"_state_{state_name}"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(__e)

    def __transition(self, next_compartment):
        self.__next_compartment = next_compartment

    def go_active(self):
        __e = PersistRoundtripFrameEvent("go_active", None)
        __ctx = PersistRoundtripFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def go_idle(self):
        __e = PersistRoundtripFrameEvent("go_idle", None)
        __ctx = PersistRoundtripFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def get_state(self) -> str:
        __e = PersistRoundtripFrameEvent("get_state", None)
        __ctx = PersistRoundtripFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def set_counter(self, n: int):
        __e = PersistRoundtripFrameEvent("set_counter", {"n": n})
        __ctx = PersistRoundtripFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def get_counter(self) -> int:
        __e = PersistRoundtripFrameEvent("get_counter", None)
        __ctx = PersistRoundtripFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def add_history(self, msg: str):
        __e = PersistRoundtripFrameEvent("add_history", {"msg": msg})
        __ctx = PersistRoundtripFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def _state_Idle(self, __e):
        if __e._message == "add_history":
            msg = __e._parameters["msg"]
            self.history.append("idle:" + msg)
        elif __e._message == "get_counter":
            self._context_stack[-1]._return = self.counter
            return
        elif __e._message == "get_state":
            self._context_stack[-1]._return = "idle"
            return
        elif __e._message == "go_active":
            self.history.append("idle->active")
            __compartment = PersistRoundtripCompartment("Active", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "go_idle":
            pass  # already idle
        elif __e._message == "set_counter":
            n = __e._parameters["n"]
            self.counter = n

    def _state_Active(self, __e):
        if __e._message == "add_history":
            msg = __e._parameters["msg"]
            self.history.append("active:" + msg)
        elif __e._message == "get_counter":
            self._context_stack[-1]._return = self.counter
            return
        elif __e._message == "get_state":
            self._context_stack[-1]._return = "active"
            return
        elif __e._message == "go_active":
            pass  # already active
        elif __e._message == "go_idle":
            self.history.append("active->idle")
            __compartment = PersistRoundtripCompartment("Idle", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "set_counter":
            n = __e._parameters["n"]
            self.counter = n * 2

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
