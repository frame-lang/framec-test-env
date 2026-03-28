
package main

import "fmt"

type MixedBodyStringsCommentsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type MixedBodyStringsCommentsFrameContext struct {
    _event  MixedBodyStringsCommentsFrameEvent
    _return any
    _data   map[string]any
}

type MixedBodyStringsCommentsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *MixedBodyStringsCommentsFrameEvent
    parentCompartment *MixedBodyStringsCommentsCompartment
}

func newMixedBodyStringsCommentsCompartment(state string) *MixedBodyStringsCommentsCompartment {
    return &MixedBodyStringsCommentsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *MixedBodyStringsCommentsCompartment) copy() *MixedBodyStringsCommentsCompartment {
    nc := &MixedBodyStringsCommentsCompartment{
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

type MixedBodyStringsComments struct {
    _state_stack []*MixedBodyStringsCommentsCompartment
    __compartment *MixedBodyStringsCommentsCompartment
    __next_compartment *MixedBodyStringsCommentsCompartment
    _context_stack []MixedBodyStringsCommentsFrameContext
}

func NewMixedBodyStringsComments() *MixedBodyStringsComments {
    s := &MixedBodyStringsComments{}
    s._state_stack = make([]*MixedBodyStringsCommentsCompartment, 0)
    s._context_stack = make([]MixedBodyStringsCommentsFrameContext, 0)
    s.__compartment = newMixedBodyStringsCommentsCompartment("Init")
    s.__next_compartment = nil
    __frame_event := MixedBodyStringsCommentsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := MixedBodyStringsCommentsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *MixedBodyStringsComments) __kernel(__e *MixedBodyStringsCommentsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &MixedBodyStringsCommentsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &MixedBodyStringsCommentsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &MixedBodyStringsCommentsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *MixedBodyStringsComments) __router(__e *MixedBodyStringsCommentsFrameEvent) {
    switch s.__compartment.state {
    case "Init":
        s._state_Init(__e)
    case "Done":
        s._state_Done(__e)
    }
}

func (s *MixedBodyStringsComments) __transition(next *MixedBodyStringsCommentsCompartment) {
    s.__next_compartment = next
}

func (s *MixedBodyStringsComments) Start() {
    __e := MixedBodyStringsCommentsFrameEvent{_message: "Start"}
    __ctx := MixedBodyStringsCommentsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *MixedBodyStringsComments) _state_Init(__e *MixedBodyStringsCommentsFrameEvent) {
    if __e._message == "Start" {
        // Native Go with Frame-statement-like tokens in strings and comments
        text := "This mentions -> $Next and pop$ inside a string."
        // A comment that mentions => $^ and -> $Other should not be parsed as Frame
        fmt.Println(text)
        __compartment := newMixedBodyStringsCommentsCompartment("Done")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MixedBodyStringsComments) _state_Done(__e *MixedBodyStringsCommentsFrameEvent) {
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	_ = NewMixedBodyStringsComments()
	fmt.Println("ok 1 - test_mixed_body_strings_comments")
}
