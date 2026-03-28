
package main

import "fmt"
import "os"

type WithTransitionFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type WithTransitionFrameContext struct {
    _event  WithTransitionFrameEvent
    _return any
    _data   map[string]any
}

type WithTransitionCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *WithTransitionFrameEvent
    parentCompartment *WithTransitionCompartment
}

func newWithTransitionCompartment(state string) *WithTransitionCompartment {
    return &WithTransitionCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *WithTransitionCompartment) copy() *WithTransitionCompartment {
    nc := &WithTransitionCompartment{
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

type WithTransition struct {
    _state_stack []*WithTransitionCompartment
    __compartment *WithTransitionCompartment
    __next_compartment *WithTransitionCompartment
    _context_stack []WithTransitionFrameContext
}

func NewWithTransition() *WithTransition {
    s := &WithTransition{}
    s._state_stack = make([]*WithTransitionCompartment, 0)
    s._context_stack = make([]WithTransitionFrameContext, 0)
    s.__compartment = newWithTransitionCompartment("First")
    s.__next_compartment = nil
    __frame_event := WithTransitionFrameEvent{_message: "$>", _parameters: nil}
    __ctx := WithTransitionFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *WithTransition) __kernel(__e *WithTransitionFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &WithTransitionFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &WithTransitionFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &WithTransitionFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *WithTransition) __router(__e *WithTransitionFrameEvent) {
    switch s.__compartment.state {
    case "First":
        s._state_First(__e)
    case "Second":
        s._state_Second(__e)
    }
}

func (s *WithTransition) __transition(next *WithTransitionCompartment) {
    s.__next_compartment = next
}

func (s *WithTransition) Next() {
    __e := WithTransitionFrameEvent{_message: "Next"}
    __ctx := WithTransitionFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *WithTransition) GetState() string {
    __e := WithTransitionFrameEvent{_message: "GetState"}
    __ctx := WithTransitionFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *WithTransition) _state_Second(__e *WithTransitionFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Second"
        return
    } else if __e._message == "Next" {
        __compartment := newWithTransitionCompartment("First")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *WithTransition) _state_First(__e *WithTransitionFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "First"
        return
    } else if __e._message == "Next" {
        __compartment := newWithTransitionCompartment("Second")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func main() {
	fmt.Println("=== Test 03: State Transitions ===")
	s := NewWithTransition()

	state := s.GetState()
	if state != "First" {
		fmt.Printf("FAIL: Expected 'First', got '%s'\n", state)
		os.Exit(1)
	}
	fmt.Printf("Initial state: %s\n", state)

	s.Next()
	state = s.GetState()
	if state != "Second" {
		fmt.Printf("FAIL: Expected 'Second', got '%s'\n", state)
		os.Exit(1)
	}
	fmt.Printf("After first Next(): %s\n", state)

	s.Next()
	state = s.GetState()
	if state != "First" {
		fmt.Printf("FAIL: Expected 'First', got '%s'\n", state)
		os.Exit(1)
	}
	fmt.Printf("After second Next(): %s\n", state)

	fmt.Println("PASS: State transitions work correctly")
}
