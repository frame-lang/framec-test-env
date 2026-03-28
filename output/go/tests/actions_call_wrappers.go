
package main

import "fmt"

type CallMismatchFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type CallMismatchFrameContext struct {
    _event  CallMismatchFrameEvent
    _return any
    _data   map[string]any
}

type CallMismatchCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *CallMismatchFrameEvent
    parentCompartment *CallMismatchCompartment
}

func newCallMismatchCompartment(state string) *CallMismatchCompartment {
    return &CallMismatchCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *CallMismatchCompartment) copy() *CallMismatchCompartment {
    nc := &CallMismatchCompartment{
        state: c.state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
        forwardEvent:     c.forwardEvent,
        parentCompartment: c.parentCompartment,
    }
    for k, v := range c.stateArgs { nc.stateArgs[k] = v }
    for k, v := range c.stateVars { nc.stateVars[k] = v }
    for k, v := range c.enterArgs { nc.enterArgs[k] = v }
    for k, v := range c.exitArgs { nc.exitArgs[k] = v }
    return nc
}

type CallMismatch struct {
    _state_stack []*CallMismatchCompartment
    __compartment *CallMismatchCompartment
    __next_compartment *CallMismatchCompartment
    _context_stack []CallMismatchFrameContext
    last string
}

func NewCallMismatch() *CallMismatch {
    s := &CallMismatch{}
    s._state_stack = make([]*CallMismatchCompartment, 0)
    s._context_stack = make([]CallMismatchFrameContext, 0)
    s.__compartment = newCallMismatchCompartment("S")
    s.__next_compartment = nil
    __frame_event := CallMismatchFrameEvent{_message: "$>", _parameters: nil}
    __ctx := CallMismatchFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *CallMismatch) __kernel(__e *CallMismatchFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &CallMismatchFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &CallMismatchFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &CallMismatchFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *CallMismatch) __router(__e *CallMismatchFrameEvent) {
    switch s.__compartment.state {
    case "S":
        s._state_S(__e)
    }
}

func (s *CallMismatch) __transition(next *CallMismatchCompartment) {
    s.__next_compartment = next
}

func (s *CallMismatch) E() {
    __e := CallMismatchFrameEvent{_message: "E"}
    __ctx := CallMismatchFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *CallMismatch) _state_S(__e *CallMismatchFrameEvent) {
    if __e._message == "E" {
        s.handle()
    }
}

func (s *CallMismatch) log(message string) {
                // log sink
                s.last = message
}

func (s *CallMismatch) handle() {
                // Calls 'log' without _action_ prefix; wrappers should preserve FRM names
                s.log("hello")
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	s := NewCallMismatch()
	s.E()
	fmt.Println("ok 1 - actions_call_wrappers")
}
