
package main

import "fmt"

type PFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type PFrameContext struct {
    _event  PFrameEvent
    _return any
    _data   map[string]any
}

type PCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *PFrameEvent
    parentCompartment *PCompartment
}

func newPCompartment(state string) *PCompartment {
    return &PCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *PCompartment) copy() *PCompartment {
    nc := &PCompartment{
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

type P struct {
    _state_stack []*PCompartment
    __compartment *PCompartment
    __next_compartment *PCompartment
    _context_stack []PFrameContext
}

func NewP() *P {
    s := &P{}
    s._state_stack = make([]*PCompartment, 0)
    s._context_stack = make([]PFrameContext, 0)
    s.__compartment = newPCompartment("A")
    s.__next_compartment = nil
    __frame_event := PFrameEvent{_message: "$>", _parameters: nil}
    __ctx := PFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *P) __kernel(__e *PFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &PFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &PFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &PFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *P) __router(__e *PFrameEvent) {
    switch s.__compartment.state {
    case "A":
        s._state_A(__e)
    case "B":
        s._state_B(__e)
    }
}

func (s *P) __transition(next *PCompartment) {
    s.__next_compartment = next
}

func (s *P) E() {
    __e := PFrameEvent{_message: "E"}
    __ctx := PFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *P) _state_B(__e *PFrameEvent) {
    if __e._message == "E" {
        ;
    }
}

func (s *P) _state_A(__e *PFrameEvent) {
    if __e._message == "E" {
        __compartment := newPCompartment("B")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	s := NewP()
	s.E()
	fmt.Println("ok 1 - basic_project")
}
