from typing import Any, Optional, List, Dict, Callable

class PersistTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class PersistTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'PersistTestCompartment':
        c = PersistTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class PersistTest:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.value = 0
        self.name = "default"
        self.__compartment = PersistTestCompartment("Idle")
        self.__next_compartment = None
        __frame_event = PersistTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = PersistTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = PersistTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = PersistTestFrameEvent("$>", self.__compartment.enter_args)
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

    def set_value(self, v: int):
        __e = PersistTestFrameEvent("set_value", {"0": v})
        self.__kernel(__e)

    def get_value(self) -> int:
        self._return_value = None
        __e = PersistTestFrameEvent("get_value", None)
        self.__kernel(__e)
        return self._return_value

    def go_active(self):
        __e = PersistTestFrameEvent("go_active", None)
        self.__kernel(__e)

    def go_idle(self):
        __e = PersistTestFrameEvent("go_idle", None)
        self.__kernel(__e)

    def _state_Active(self, __e):
        if __e._message == "get_value":
            self._return_value = self.value
            __e._return = self._return_value
            return
        elif __e._message == "go_active":
            pass  # Already active
        elif __e._message == "go_idle":
            __compartment = PersistTestCompartment("Idle", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "set_value":
            v = __e._parameters["0"]
            self.value = v * 2

    def _state_Idle(self, __e):
        if __e._message == "get_value":
            self._return_value = self.value
            __e._return = self._return_value
            return
        elif __e._message == "go_active":
            __compartment = PersistTestCompartment("Active", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)
        elif __e._message == "go_idle":
            pass  # Already idle
        elif __e._message == "set_value":
            v = __e._parameters["0"]
            self.value = v

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
