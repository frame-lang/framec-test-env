
package main

import "fmt"

type SimpleDockerFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SimpleDockerFrameContext struct {
    _event  SimpleDockerFrameEvent
    _return any
    _data   map[string]any
}

type SimpleDockerCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SimpleDockerFrameEvent
    parentCompartment *SimpleDockerCompartment
}

func newSimpleDockerCompartment(state string) *SimpleDockerCompartment {
    return &SimpleDockerCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SimpleDockerCompartment) copy() *SimpleDockerCompartment {
    nc := &SimpleDockerCompartment{
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

type SimpleDocker struct {
    _state_stack []*SimpleDockerCompartment
    __compartment *SimpleDockerCompartment
    __next_compartment *SimpleDockerCompartment
    _context_stack []SimpleDockerFrameContext
}

func NewSimpleDocker() *SimpleDocker {
    s := &SimpleDocker{}
    s._state_stack = make([]*SimpleDockerCompartment, 0)
    s._context_stack = make([]SimpleDockerFrameContext, 0)
    s.__compartment = newSimpleDockerCompartment("Start")
    s.__next_compartment = nil
    __frame_event := SimpleDockerFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SimpleDockerFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *SimpleDocker) __kernel(__e *SimpleDockerFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SimpleDockerFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SimpleDockerFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SimpleDockerFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *SimpleDocker) __router(__e *SimpleDockerFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "End":
        s._state_End(__e)
    }
}

func (s *SimpleDocker) __transition(next *SimpleDockerCompartment) {
    s.__next_compartment = next
}

func (s *SimpleDocker) Run() {
    __e := SimpleDockerFrameEvent{_message: "Run"}
    __ctx := SimpleDockerFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *SimpleDocker) _state_Start(__e *SimpleDockerFrameEvent) {
    if __e._message == "Run" {
        fmt.Println("SUCCESS: Hello from Docker")
        __compartment := newSimpleDockerCompartment("End")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *SimpleDocker) _state_End(__e *SimpleDockerFrameEvent) {
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	_ = NewSimpleDocker()
	fmt.Println("ok 1 - simple_test")
}
