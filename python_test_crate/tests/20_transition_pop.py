from typing import Any, Optional, List, Dict, Callable

class TransitionPopTestFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class TransitionPopTestCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'TransitionPopTestCompartment':
        c = TransitionPopTestCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class TransitionPopTest:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.log =         []
        self.__compartment = TransitionPopTestCompartment("Idle")
        self.__next_compartment = None
        __frame_event = TransitionPopTestFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = TransitionPopTestFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = TransitionPopTestFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = TransitionPopTestFrameEvent("$>", self.__compartment.enter_args)
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

    def start(self):
        __e = TransitionPopTestFrameEvent("start", None)
        self.__kernel(__e)

    def process(self):
        __e = TransitionPopTestFrameEvent("process", None)
        self.__kernel(__e)

    def get_state(self) -> str:
        self._return_value = None
        __e = TransitionPopTestFrameEvent("get_state", None)
        self.__kernel(__e)
        return self._return_value

    def get_log(self) -> list:
        self._return_value = None
        __e = TransitionPopTestFrameEvent("get_log", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Working(self, __e):
        if __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "Working"
            __e._return = self._return_value
            return
        elif __e._message == "process":
            self.log.append("working:process:before_pop")
            self.__compartment = self._state_stack.pop()
            return
            # This should NOT execute because pop transitions away
            self.log.append("working:process:after_pop")

    def _state_Idle(self, __e):
        if __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "get_state":
            self._return_value = "Idle"
            __e._return = self._return_value
            return
        elif __e._message == "process":
            self.log.append("idle:process")
        elif __e._message == "start":
            self.log.append("idle:start:push")
            self._state_stack.append(self.__compartment.copy())
            __compartment = TransitionPopTestCompartment("Working", parent_compartment=self.__compartment.copy())
            self.__transition(__compartment)


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
