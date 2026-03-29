from typing import Any, Optional, List, Dict, Callable

<?php

class SFrameEvent:
    def __init__(self, message: str, parameters):
        self._message = message
        self._parameters = parameters


class SFrameContext:
    def __init__(self, event: SFrameEvent, default_return):
        self.event = event
        self._return = default_return
        self._data = {}


class SCompartment:
    def __init__(self, state: str, parent_compartment = None):
        self.state = state
        self.state_args = {}
        self.state_vars = {}
        self.enter_args = {}
        self.exit_args = {}
        self.forward_event = None
        self.parent_compartment = parent_compartment

    def copy(self) -> 'SCompartment':
        c = SCompartment(self.state, self.parent_compartment)
        c.state_args = self.state_args.copy()
        c.state_vars = self.state_vars.copy()
        c.enter_args = self.enter_args.copy()
        c.exit_args = self.exit_args.copy()
        c.forward_event = self.forward_event
        return c


class S:
    def __init__(self):
        self._state_stack = []
        self._context_stack = []
        # HSM: Create parent compartment chain
        __parent_comp_0 = SCompartment("P", parent_compartment=None)
        self.__compartment = SCompartment("A", parent_compartment=__parent_comp_0)
        self.__next_compartment = None
        __frame_event = SFrameEvent("$>", None)
        self.__kernel(__frame_event)

    def __kernel(self, __e):
        # Route event to current state
        self.__router(__e)
        # Process any pending transition
        while self.__next_compartment is not None:
            next_compartment = self.__next_compartment
            self.__next_compartment = None
            # Exit current state
            exit_event = SFrameEvent("<$", self.__compartment.exit_args)
            self.__router(exit_event)
            # Switch to new compartment
            self.__compartment = next_compartment
            # Enter new state (or forward event)
            if next_compartment.forward_event is None:
                enter_event = SFrameEvent("$>", self.__compartment.enter_args)
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
                    enter_event = SFrameEvent("$>", self.__compartment.enter_args)
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

    def e1(self):
        __e = SFrameEvent("e1", None)
        __ctx = SFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def e2(self):
        __e = SFrameEvent("e2", None)
        __ctx = SFrameContext(__e, None)
        self._context_stack.append(__ctx)
        self.__kernel(__e)
        self._context_stack.pop()

    def _state_P(self, __e):
        pass

    def _state_A(self, __e):
        if __e._message == "e1":
            self._state_P(__e)
        elif __e._message == "e2":
            self._state_P(__e)

function native() {}
function x() {}

echo "TAP version 14" . "\n";
echo "1..1" . "\n";
try {
    $s = new S();
    if (method_exists($s, 'e')) { $s->e(); }
    echo "ok 1 - multiple_handlers" . "\n";
} catch (\Exception $ex) {
    echo "not ok 1 - multiple_handlers # " . $ex->getMessage() . "\n";
}

