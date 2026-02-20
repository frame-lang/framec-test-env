from typing import Any, Optional, List, Dict, Callable

class ForwardEnterFirstFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters
        self._return = None


class ForwardEnterFirstCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'ForwardEnterFirstCompartment':
        c = ForwardEnterFirstCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class ForwardEnterFirst:
    def __init__(self):
        self._state_stack = []
        self._return_value = None
        self.log =         []
        self.__compartment = ForwardEnterFirstCompartment("Idle")
        self.__next_compartment = None
        __frame_event = ForwardEnterFirstFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = ForwardEnterFirstFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = ForwardEnterFirstFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = ForwardEnterFirstFrameEvent("$>", self.__compartment.enter_args)
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

    def process(self):
        __e = ForwardEnterFirstFrameEvent("process", None)
        self.__kernel(__e)

    def get_counter(self) -> int:
        self._return_value = None
        __e = ForwardEnterFirstFrameEvent("get_counter", None)
        self.__kernel(__e)
        return self._return_value

    def get_log(self) -> list:
        self._return_value = None
        __e = ForwardEnterFirstFrameEvent("get_log", None)
        self.__kernel(__e)
        return self._return_value

    def _state_Working(self, __e):
        if __e._message == "$>":
            self.__compartment.state_vars["counter"] = 100
            self.log.append("Working:enter")
        elif __e._message == "get_counter":
            self._return_value = self.__compartment.state_vars["counter"]
            __e._return = self._return_value
            return
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "process":
            self.log.append("Working:process:counter=" + str(self.__compartment.state_vars["counter"]))
            self.__compartment.state_vars["counter"] = self.__compartment.state_vars["counter"] + 1

    def _state_Idle(self, __e):
        if __e._message == "get_counter":
            self._return_value = -1
            __e._return = self._return_value
            return
        elif __e._message == "get_log":
            self._return_value = self.log
            __e._return = self._return_value
            return
        elif __e._message == "process":
            __compartment = ForwardEnterFirstCompartment("Working", parent_compartment=self.__compartment.copy())
            __compartment.forward_event = __e
            self.__transition(__compartment)
            return


def main():
    print("=== Test 29: Forward Enter First ===")
    s = ForwardEnterFirst()

    # Initial state is Idle
    assert s.get_counter() == -1, "Expected -1 in Idle"

    # Call process - should forward to Working
    # Correct behavior: $> runs first (inits counter=100, logs "Working:enter")
    # Then process runs (logs "Working:process:counter=100", increments to 101)
    s.process()

    # Check counter was initialized and incremented
    counter = s.get_counter()
    log = s.get_log()
    print(f"Counter after forward: {counter}")
    print(f"Log: {log}")

    # Verify $> ran first
    assert "Working:enter" in log, f"Expected 'Working:enter' in log: {log}"

    # Verify process ran after $>
    assert "Working:process:counter=100" in log, f"Expected 'Working:process:counter=100' in log: {log}"

    # Verify counter was incremented
    assert counter == 101, f"Expected counter=101, got {counter}"

    # Verify order: enter before process
    enter_idx = log.index("Working:enter")
    process_idx = log.index("Working:process:counter=100")
    assert enter_idx < process_idx, f"$> should run before process: {log}"

    print("PASS: Forward sends $> first for non-$> events")

if __name__ == '__main__':
    main()
