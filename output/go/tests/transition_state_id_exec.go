
package main

import "fmt"

type SysXFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SysXFrameContext struct {
    _event  SysXFrameEvent
    _return any
    _data   map[string]any
}

type SysXCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SysXFrameEvent
    parentCompartment *SysXCompartment
}

func newSysXCompartment(state string) *SysXCompartment {
    return &SysXCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SysXCompartment) copy() *SysXCompartment {
    nc := &SysXCompartment{
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

type SysX struct {
    _state_stack []*SysXCompartment
    __compartment *SysXCompartment
    __next_compartment *SysXCompartment
    _context_stack []SysXFrameContext
}

func NewSysX() *SysX {
    s := &SysX{}
    s._state_stack = make([]*SysXCompartment, 0)
    s._context_stack = make([]SysXFrameContext, 0)
    s.__compartment = newSysXCompartment("A")
    s.__next_compartment = nil
    __frame_event := SysXFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SysXFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *SysX) __kernel(__e *SysXFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SysXFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SysXFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SysXFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *SysX) __router(__e *SysXFrameEvent) {
    switch s.__compartment.state {
    case "A":
        s._state_A(__e)
    case "B":
        s._state_B(__e)
    }
}

func (s *SysX) __transition(next *SysXCompartment) {
    s.__next_compartment = next
}

func (s *SysX) E() {
    __e := SysXFrameEvent{_message: "E"}
    __ctx := SysXFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *SysX) _state_B(__e *SysXFrameEvent) {
}

func (s *SysX) _state_A(__e *SysXFrameEvent) {
    if __e._message == "E" {
        __compartment := newSysXCompartment("B")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return;
    }
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	s := NewSysX()
	s.E()
	fmt.Println("ok 1 - transition_state_id_exec")
}
