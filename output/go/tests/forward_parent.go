
package main

import "fmt"

func x() {}

type SFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SFrameContext struct {
    _event  SFrameEvent
    _return any
    _data   map[string]any
}

type SCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SFrameEvent
    parentCompartment *SCompartment
}

func newSCompartment(state string) *SCompartment {
    return &SCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SCompartment) copy() *SCompartment {
    nc := &SCompartment{
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

type S struct {
    _state_stack []*SCompartment
    __compartment *SCompartment
    __next_compartment *SCompartment
    _context_stack []SFrameContext
}

func NewS() *S {
    s := &S{}
    s._state_stack = make([]*SCompartment, 0)
    s._context_stack = make([]SFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newSCompartment("P")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newSCompartment("A")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := SFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *S) __kernel(__e *SFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *S) __router(__e *SFrameEvent) {
    switch s.__compartment.state {
    case "A":
        s._state_A(__e)
    case "P":
        s._state_P(__e)
    }
}

func (s *S) __transition(next *SCompartment) {
    s.__next_compartment = next
}

func (s *S) E() {
    __e := SFrameEvent{_message: "E"}
    __ctx := SFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *S) _state_A(__e *SFrameEvent) {
    if __e._message == "E" {
        s._state_P(__e)
        x()
    }
}

func (s *S) _state_P(__e *SFrameEvent) {
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	s := NewS()
	s.E()
	fmt.Println("ok 1 - forward_parent")
}
