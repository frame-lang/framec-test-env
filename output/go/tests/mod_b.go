
package main

import "fmt"

type S2FrameEvent struct {
    _message    string
    _parameters map[string]any
}

type S2FrameContext struct {
    _event  S2FrameEvent
    _return any
    _data   map[string]any
}

type S2Compartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *S2FrameEvent
    parentCompartment *S2Compartment
}

func newS2Compartment(state string) *S2Compartment {
    return &S2Compartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *S2Compartment) copy() *S2Compartment {
    nc := &S2Compartment{
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

type S2 struct {
    _state_stack []*S2Compartment
    __compartment *S2Compartment
    __next_compartment *S2Compartment
    _context_stack []S2FrameContext
}

func NewS2() *S2 {
    s := &S2{}
    s._state_stack = make([]*S2Compartment, 0)
    s._context_stack = make([]S2FrameContext, 0)
    s.__compartment = newS2Compartment("A")
    s.__next_compartment = nil
    __frame_event := S2FrameEvent{_message: "$>", _parameters: nil}
    __ctx := S2FrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *S2) __kernel(__e *S2FrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &S2FrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &S2FrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &S2FrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *S2) __router(__e *S2FrameEvent) {
    switch s.__compartment.state {
    case "A":
        s._state_A(__e)
    }
}

func (s *S2) __transition(next *S2Compartment) {
    s.__next_compartment = next
}

func (s *S2) E() {
    __e := S2FrameEvent{_message: "E"}
    __ctx := S2FrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *S2) _state_A(__e *S2FrameEvent) {
    if __e._message == "E" {
        __compartment := newS2Compartment("A")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	s := NewS2()
	s.E()
	fmt.Println("ok 1 - mod_b")
}
