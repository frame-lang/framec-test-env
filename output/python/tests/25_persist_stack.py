from typing import Any, Optional, List, Dict, Callable

class PersistStackFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class PersistStackFrameContext:
    def __init__(self, event: PersistStackFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class PersistStackCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'PersistStackCompartment':
        c = PersistStackCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class PersistStack:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.depth = 0
        self.__compartment = PersistStackCompartment("Start")
        self.__next_compartment = None
        __frame_event = PersistStackFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = PersistStackFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = PersistStackFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = PersistStackFrameEvent("$>", self.__compartment.enter_args)
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

    def push_and_go(self):
        __e = PersistStackFrameEvent("push_and_go", None)
        __ctx = PersistStackFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def pop_back(self):
        __e = PersistStackFrameEvent("pop_back", None)
        __ctx = PersistStackFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def get_state(self) -> str:
        __e = PersistStackFrameEvent("get_state", None)
        __ctx = PersistStackFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def get_depth(self) -> int:
        __e = PersistStackFrameEvent("get_depth", None)
        __ctx = PersistStackFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Start(self, __e):
        if __e._message == "get_depth":
            self._context_stack[-1]._return = self.depth
            return
        elif __e._message == "get_state":
            self._context_stack[-1]._return = "start"
            return
        elif __e._message == "pop_back":
            pass  # nothing to pop
        elif __e._message == "push_and_go":
            self.depth = self.depth + 1
            self._state_stack.append(self.__compartment.copy())
            __compartment = PersistStackCompartment("Middle", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_Middle(self, __e):
        if __e._message == "get_depth":
            self._context_stack[-1]._return = self.depth
            return
        elif __e._message == "get_state":
            self._context_stack[-1]._return = "middle"
            return
        elif __e._message == "pop_back":
            self.depth = self.depth - 1
            self.__compartment = self._state_stack.pop()
            return
        elif __e._message == "push_and_go":
            self.depth = self.depth + 1
            self._state_stack.append(self.__compartment.copy())
            __compartment = PersistStackCompartment("End", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)

    def _state_End(self, __e):
        if __e._message == "get_depth":
            self._context_stack[-1]._return = self.depth
            return
        elif __e._message == "get_state":
            self._context_stack[-1]._return = "end"
            return
        elif __e._message == "pop_back":
            self.depth = self.depth - 1
            self.__compartment = self._state_stack.pop()
            return
        elif __e._message == "push_and_go":
            pass  # can't go further

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
