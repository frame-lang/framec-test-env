
package main

import "fmt"

// Test: Logical operators in Frame handlers
// Tests: &&, ||, !

type LogicalTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type LogicalTestFrameContext struct {
    _event  LogicalTestFrameEvent
    _return any
    _data   map[string]any
}

type LogicalTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *LogicalTestFrameEvent
    parentCompartment *LogicalTestCompartment
}

func newLogicalTestCompartment(state string) *LogicalTestCompartment {
    return &LogicalTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *LogicalTestCompartment) copy() *LogicalTestCompartment {
    nc := &LogicalTestCompartment{
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

type LogicalTest struct {
    _state_stack []*LogicalTestCompartment
    __compartment *LogicalTestCompartment
    __next_compartment *LogicalTestCompartment
    _context_stack []LogicalTestFrameContext
    a bool
    b bool
}

func NewLogicalTest() *LogicalTest {
    s := &LogicalTest{}
    s._state_stack = make([]*LogicalTestCompartment, 0)
    s._context_stack = make([]LogicalTestFrameContext, 0)
    s.__compartment = newLogicalTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := LogicalTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := LogicalTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *LogicalTest) __kernel(__e *LogicalTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &LogicalTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &LogicalTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &LogicalTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *LogicalTest) __router(__e *LogicalTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *LogicalTest) __transition(next *LogicalTestCompartment) {
    s.__next_compartment = next
}

func (s *LogicalTest) TestAnd() bool {
    __e := LogicalTestFrameEvent{_message: "TestAnd"}
    __ctx := LogicalTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *LogicalTest) TestOr() bool {
    __e := LogicalTestFrameEvent{_message: "TestOr"}
    __ctx := LogicalTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *LogicalTest) TestNot() bool {
    __e := LogicalTestFrameEvent{_message: "TestNot"}
    __ctx := LogicalTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *LogicalTest) SetValues(x bool, y bool) {
    __params := map[string]any{
        "x": x,
        "y": y,
    }
    __e := LogicalTestFrameEvent{_message: "SetValues", _parameters: __params}
    __ctx := LogicalTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *LogicalTest) _state_Ready(__e *LogicalTestFrameEvent) {
    if __e._message == "$>" {
        s.a = true
        s.b = false
    } else if __e._message == "SetValues" {
        x := __e._parameters["x"].(bool)
        _ = x
        y := __e._parameters["y"].(bool)
        _ = y
        s.a = x
        s.b = y
    } else if __e._message == "TestAnd" {
        if s.a && s.b {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    } else if __e._message == "TestNot" {
        if !s.a {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    } else if __e._message == "TestOr" {
        if s.a || s.b {
            s._context_stack[len(s._context_stack)-1]._return = true
        } else {
            s._context_stack[len(s._context_stack)-1]._return = false
        }
    }
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..6")

	s := NewLogicalTest()

	// a=true, b=false: true && false = false
	if !s.TestAnd() {
		fmt.Println("ok 1 - true && false is false")
	} else {
		fmt.Println("not ok 1 - true && false is false")
	}

	// a=true, b=false: true || false = true
	if s.TestOr() {
		fmt.Println("ok 2 - true || false is true")
	} else {
		fmt.Println("not ok 2 - true || false is true")
	}

	// a=true: !true = false
	if !s.TestNot() {
		fmt.Println("ok 3 - !true is false")
	} else {
		fmt.Println("not ok 3 - !true is false")
	}

	// Change values: a=true, b=true
	s.SetValues(true, true)

	// true && true = true
	if s.TestAnd() {
		fmt.Println("ok 4 - true && true is true")
	} else {
		fmt.Println("not ok 4 - true && true is true")
	}

	// Change values: a=false, b=false
	s.SetValues(false, false)

	// false || false = false
	if !s.TestOr() {
		fmt.Println("ok 5 - false || false is false")
	} else {
		fmt.Println("not ok 5 - false || false is false")
	}

	// !false = true
	if s.TestNot() {
		fmt.Println("ok 6 - !false is true")
	} else {
		fmt.Println("not ok 6 - !false is true")
	}
}
