from typing import Any, Optional, List, Dict, Callable

class TransitionEnterArgsFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class TransitionEnterArgsFrameContext:
    def __init__(self, event: TransitionEnterArgsFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class TransitionEnterArgsCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'TransitionEnterArgsCompartment':
        c = TransitionEnterArgsCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class TransitionEnterArgs:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        self.log =         []
        self.__compartment = TransitionEnterArgsCompartment("Idle")
        self.__next_compartment = None
        __frame_event = TransitionEnterArgsFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = TransitionEnterArgsFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = TransitionEnterArgsFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = TransitionEnterArgsFrameEvent("$>", self.__compartment.enter_args)
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
        __e = TransitionEnterArgsFrameEvent("start", None)
        __ctx = TransitionEnterArgsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def get_log(self) -> list:
        __e = TransitionEnterArgsFrameEvent("get_log", None)
        __ctx = TransitionEnterArgsFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        return self._context_stack.pop()._return

    def _state_Active(self, __e):
        if __e._message == "$>":
            source = __e._parameters["source"]
            value = __e._parameters["value"]
            self.log.append(f"active:enter:{source}:{value}")
        elif __e._message == "get_log":
            self._context_stack[-1]._return = self.log
            return
        elif __e._message == "start":
            self.log.append("active:start")

    def _state_Idle(self, __e):
        if __e._message == "get_log":
            self._context_stack[-1]._return = self.log
            return
        elif __e._message == "start":
            self.log.append("idle:start")
            __compartment = TransitionEnterArgsCompartment("Active", parent_compartment=self.__compartment.copy())
            __compartment.enter_args = {str(i): v for i, v in enumerate(("from_idle", 42,))}
            self.__transition(__compartment)


def main():
    print("=== Test 17: Transition Enter Args ===")
    s = TransitionEnterArgs()

    # Initial state is Idle
    log = s.get_log()
    assert log == [], f"Expected empty log, got {log}"

    # Transition to Active with args
    s.start()
    log = s.get_log()
    assert "idle:start" in log, f"Expected 'idle:start' in log, got {log}"
    assert "active:enter:from_idle:42" in log, f"Expected 'active:enter:from_idle:42' in log, got {log}"
    print(f"Log after transition: {log}")

    print("PASS: Transition enter args work correctly")

if __name__ == '__main__':
    main()
