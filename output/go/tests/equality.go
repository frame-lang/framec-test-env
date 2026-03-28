
package main

import "fmt"

// Test: Equality operators in Frame handlers
// Tests: ==, !=

type EqualityTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type EqualityTestFrameContext struct {
    _event  EqualityTestFrameEvent
    _return any
    _data   map[string]any
}

type EqualityTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *EqualityTestFrameEvent
    parentCompartment *EqualityTestCompartment
}

func newEqualityTestCompartment(state string) *EqualityTestCompartment {
    return &EqualityTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *EqualityTestCompartment) copy() *EqualityTestCompartment {
    nc := &EqualityTestCompartment{
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

type EqualityTest struct {
    _state_stack []*EqualityTestCompartment
    __compartment *EqualityTestCompartment
    __next_compartment *EqualityTestCompartment
    _context_stack []EqualityTestFrameContext
    a int
    b int
}

func NewEqualityTest() *EqualityTest {
    s := &EqualityTest{}
    s._state_stack = make([]*EqualityTestCompartment, 0)
    s._context_stack = make([]EqualityTestFrameContext, 0)
    s.__compartment = newEqualityTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := EqualityTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := EqualityTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *EqualityTest) __kernel(__e *EqualityTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &EqualityTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &EqualityTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &EqualityTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *EqualityTest) __router(__e *EqualityTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *EqualityTest) __transition(next *EqualityTestCompartment) {
    s.__next_compartment = next
}

func (s *EqualityTest) TestEqual() bool {
    __e := EqualityTestFrameEvent{_message: "TestEqual"}
    __ctx := EqualityTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *EqualityTest) TestNotEqual() bool {
    __e := EqualityTestFrameEvent{_message: "TestNotEqual"}
    __ctx := EqualityTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *EqualityTest) SetValues(x int, y int) {
    __params := map[string]any{
        "x": x,
        "y": y,
    }
    __e := EqualityTestFrameEvent{_message: "SetValues", _parameters: __params}
    __ctx := EqualityTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *EqualityTest) _state_Ready(__e *EqualityTestFrameEvent) {
    if __e._message == "$>" {
        s.a = 5
        s.b = 5
    } else if __e._message == "SetValues" {
        x := __e._parameters["x"].(int)
        _ = x
        y := __e._parameters["y"].(int)
        _ = y
        s.a = x
        s.b = y
    } else if __e._message == "TestEqual" {
        if s.a == s.b {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    } else if __e._message == "TestNotEqual" {
        if s.a != s.b {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    }
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..4")

	s := NewEqualityTest()

	// a=5, b=5: 5 == 5 is true
	if s.TestEqual() {
		fmt.Println("ok 1 - 5 == 5 is true")
	} else {
		fmt.Println("not ok 1 - 5 == 5 is true")
	}

	// a=5, b=5: 5 != 5 is false
	if !s.TestNotEqual() {
		fmt.Println("ok 2 - 5 != 5 is false")
	} else {
		fmt.Println("not ok 2 - 5 != 5 is false")
	}

	// Change values: a=5, b=3
	s.SetValues(5, 3)

	// a=5, b=3: 5 == 3 is false
	if !s.TestEqual() {
		fmt.Println("ok 3 - 5 == 3 is false")
	} else {
		fmt.Println("not ok 3 - 5 == 3 is false")
	}

	// a=5, b=3: 5 != 3 is true
	if s.TestNotEqual() {
		fmt.Println("ok 4 - 5 != 3 is true")
	} else {
		fmt.Println("not ok 4 - 5 != 3 is true")
	}
}
