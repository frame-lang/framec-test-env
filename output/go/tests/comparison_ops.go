
package main

import "fmt"

// Test: Comparison operators in Frame handlers
// Tests: >, <, >=, <=, ==, !=

type ComparisonTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type ComparisonTestFrameContext struct {
    _event  ComparisonTestFrameEvent
    _return any
    _data   map[string]any
}

type ComparisonTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *ComparisonTestFrameEvent
    parentCompartment *ComparisonTestCompartment
}

func newComparisonTestCompartment(state string) *ComparisonTestCompartment {
    return &ComparisonTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *ComparisonTestCompartment) copy() *ComparisonTestCompartment {
    nc := &ComparisonTestCompartment{
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

type ComparisonTest struct {
    _state_stack []*ComparisonTestCompartment
    __compartment *ComparisonTestCompartment
    __next_compartment *ComparisonTestCompartment
    _context_stack []ComparisonTestFrameContext
    a int
    b int
}

func NewComparisonTest() *ComparisonTest {
    s := &ComparisonTest{}
    s._state_stack = make([]*ComparisonTestCompartment, 0)
    s._context_stack = make([]ComparisonTestFrameContext, 0)
    s.__compartment = newComparisonTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := ComparisonTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := ComparisonTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *ComparisonTest) __kernel(__e *ComparisonTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &ComparisonTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &ComparisonTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &ComparisonTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *ComparisonTest) __router(__e *ComparisonTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *ComparisonTest) __transition(next *ComparisonTestCompartment) {
    s.__next_compartment = next
}

func (s *ComparisonTest) TestGreater() bool {
    __e := ComparisonTestFrameEvent{_message: "TestGreater"}
    __ctx := ComparisonTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ComparisonTest) TestLess() bool {
    __e := ComparisonTestFrameEvent{_message: "TestLess"}
    __ctx := ComparisonTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ComparisonTest) TestGreaterEqual() bool {
    __e := ComparisonTestFrameEvent{_message: "TestGreaterEqual"}
    __ctx := ComparisonTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ComparisonTest) TestLessEqual() bool {
    __e := ComparisonTestFrameEvent{_message: "TestLessEqual"}
    __ctx := ComparisonTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ComparisonTest) TestEqual() bool {
    __e := ComparisonTestFrameEvent{_message: "TestEqual"}
    __ctx := ComparisonTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ComparisonTest) TestNotEqual() bool {
    __e := ComparisonTestFrameEvent{_message: "TestNotEqual"}
    __ctx := ComparisonTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ComparisonTest) SetValues(x int, y int) {
    __params := map[string]any{
        "x": x,
        "y": y,
    }
    __e := ComparisonTestFrameEvent{_message: "SetValues", _parameters: __params}
    __ctx := ComparisonTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *ComparisonTest) _state_Ready(__e *ComparisonTestFrameEvent) {
    if __e._message == "$>" {
        s.a = 5
        s.b = 3
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
    } else if __e._message == "TestGreater" {
        if s.a > s.b {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    } else if __e._message == "TestGreaterEqual" {
        if s.a >= s.b {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    } else if __e._message == "TestLess" {
        if s.a < s.b {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    } else if __e._message == "TestLessEqual" {
        if s.a <= s.b {
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
	fmt.Println("1..6")

	s := NewComparisonTest()

	// a=5, b=3: 5 > 3 is true
	if s.TestGreater() {
		fmt.Println("ok 1 - 5 > 3 is true")
	} else {
		fmt.Println("not ok 1 - 5 > 3 is true")
	}

	// a=5, b=3: 5 < 3 is false
	if !s.TestLess() {
		fmt.Println("ok 2 - 5 < 3 is false")
	} else {
		fmt.Println("not ok 2 - 5 < 3 is false")
	}

	// a=5, b=3: 5 >= 3 is true
	if s.TestGreaterEqual() {
		fmt.Println("ok 3 - 5 >= 3 is true")
	} else {
		fmt.Println("not ok 3 - 5 >= 3 is true")
	}

	// a=5, b=3: 5 <= 3 is false
	if !s.TestLessEqual() {
		fmt.Println("ok 4 - 5 <= 3 is false")
	} else {
		fmt.Println("not ok 4 - 5 <= 3 is false")
	}

	// a=5, b=3: 5 == 3 is false
	if !s.TestEqual() {
		fmt.Println("ok 5 - 5 == 3 is false")
	} else {
		fmt.Println("not ok 5 - 5 == 3 is false")
	}

	// a=5, b=3: 5 != 3 is true
	if s.TestNotEqual() {
		fmt.Println("ok 6 - 5 != 3 is true")
	} else {
		fmt.Println("not ok 6 - 5 != 3 is true")
	}
}
