
package main

import "fmt"

// Test: Ternary/conditional expressions in Frame handlers
// Go does not have ternary; use if/else in native code

type TernaryTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type TernaryTestFrameContext struct {
    _event  TernaryTestFrameEvent
    _return any
    _data   map[string]any
}

type TernaryTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *TernaryTestFrameEvent
    parentCompartment *TernaryTestCompartment
}

func newTernaryTestCompartment(state string) *TernaryTestCompartment {
    return &TernaryTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *TernaryTestCompartment) copy() *TernaryTestCompartment {
    nc := &TernaryTestCompartment{
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

type TernaryTest struct {
    _state_stack []*TernaryTestCompartment
    __compartment *TernaryTestCompartment
    __next_compartment *TernaryTestCompartment
    _context_stack []TernaryTestFrameContext
    cond bool
}

func NewTernaryTest() *TernaryTest {
    s := &TernaryTest{}
    s._state_stack = make([]*TernaryTestCompartment, 0)
    s._context_stack = make([]TernaryTestFrameContext, 0)
    s.__compartment = newTernaryTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := TernaryTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := TernaryTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *TernaryTest) __kernel(__e *TernaryTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &TernaryTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &TernaryTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &TernaryTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *TernaryTest) __router(__e *TernaryTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *TernaryTest) __transition(next *TernaryTestCompartment) {
    s.__next_compartment = next
}

func (s *TernaryTest) GetValue() int {
    __e := TernaryTestFrameEvent{_message: "GetValue"}
    __ctx := TernaryTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *TernaryTest) SetCondition(c bool) {
    __params := map[string]any{
        "c": c,
    }
    __e := TernaryTestFrameEvent{_message: "SetCondition", _parameters: __params}
    __ctx := TernaryTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TernaryTest) _state_Ready(__e *TernaryTestFrameEvent) {
    if __e._message == "$>" {
        s.cond = true
    } else if __e._message == "GetValue" {
        var result int
        if s.cond {
            result = 100
        } else {
            result = 200
        }
        s._context_stack[len(s._context_stack)-1]._return = result
    } else if __e._message == "SetCondition" {
        c := __e._parameters["c"].(bool)
        _ = c
        s.cond = c
    }
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..2")

	s := NewTernaryTest()

	// cond=true: should return 100
	v1 := s.GetValue()
	if v1 == 100 {
		fmt.Println("ok 1 - cond=true returns 100")
	} else {
		fmt.Printf("not ok 1 - cond=true returns 100 # got %d\n", v1)
	}

	// cond=false: should return 200
	s.SetCondition(false)
	v2 := s.GetValue()
	if v2 == 200 {
		fmt.Println("ok 2 - cond=false returns 200")
	} else {
		fmt.Printf("not ok 2 - cond=false returns 200 # got %d\n", v2)
	}
}
