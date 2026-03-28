
package main

import (
	"fmt"
	"os"
	"strconv"
)

type SystemReturnReentrantTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SystemReturnReentrantTestFrameContext struct {
    _event  SystemReturnReentrantTestFrameEvent
    _return any
    _data   map[string]any
}

type SystemReturnReentrantTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SystemReturnReentrantTestFrameEvent
    parentCompartment *SystemReturnReentrantTestCompartment
}

func newSystemReturnReentrantTestCompartment(state string) *SystemReturnReentrantTestCompartment {
    return &SystemReturnReentrantTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SystemReturnReentrantTestCompartment) copy() *SystemReturnReentrantTestCompartment {
    nc := &SystemReturnReentrantTestCompartment{
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

type SystemReturnReentrantTest struct {
    _state_stack []*SystemReturnReentrantTestCompartment
    __compartment *SystemReturnReentrantTestCompartment
    __next_compartment *SystemReturnReentrantTestCompartment
    _context_stack []SystemReturnReentrantTestFrameContext
}

func NewSystemReturnReentrantTest() *SystemReturnReentrantTest {
    s := &SystemReturnReentrantTest{}
    s._state_stack = make([]*SystemReturnReentrantTestCompartment, 0)
    s._context_stack = make([]SystemReturnReentrantTestFrameContext, 0)
    s.__compartment = newSystemReturnReentrantTestCompartment("Start")
    s.__next_compartment = nil
    __frame_event := SystemReturnReentrantTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SystemReturnReentrantTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *SystemReturnReentrantTest) __kernel(__e *SystemReturnReentrantTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SystemReturnReentrantTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SystemReturnReentrantTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SystemReturnReentrantTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *SystemReturnReentrantTest) __router(__e *SystemReturnReentrantTestFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    }
}

func (s *SystemReturnReentrantTest) __transition(next *SystemReturnReentrantTestCompartment) {
    s.__next_compartment = next
}

func (s *SystemReturnReentrantTest) OuterCall() string {
    __e := SystemReturnReentrantTestFrameEvent{_message: "OuterCall"}
    __ctx := SystemReturnReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnReentrantTest) InnerCall() string {
    __e := SystemReturnReentrantTestFrameEvent{_message: "InnerCall"}
    __ctx := SystemReturnReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnReentrantTest) NestedCall() string {
    __e := SystemReturnReentrantTestFrameEvent{_message: "NestedCall"}
    __ctx := SystemReturnReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnReentrantTest) GetLog() string {
    __e := SystemReturnReentrantTestFrameEvent{_message: "GetLog"}
    __ctx := SystemReturnReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnReentrantTest) _state_Start(__e *SystemReturnReentrantTestFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Start" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["log"]; !ok {
            __sv_comp.stateVars["log"] = ""
        }
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["log"].(string)
        return
    } else if __e._message == "InnerCall" {
        __sv_comp.stateVars["log"] = __sv_comp.stateVars["log"].(string) + "inner,"
        s._context_stack[len(s._context_stack)-1]._return = "inner_result"
        return
    } else if __e._message == "NestedCall" {
        __sv_comp.stateVars["log"] = __sv_comp.stateVars["log"].(string) + "nested_start,"
        // Two levels of nesting
        result1 := s.InnerCall()
        result2 := s.OuterCall()
        __sv_comp.stateVars["log"] = __sv_comp.stateVars["log"].(string) + "nested_end,"
        s._context_stack[len(s._context_stack)-1]._return = "nested:" + result1 + "+" + result2
        return
    } else if __e._message == "OuterCall" {
        __sv_comp.stateVars["log"] = __sv_comp.stateVars["log"].(string) + "outer_start,"
        // Call inner method - this creates nested return context
        inner_result := s.InnerCall()
        __sv_comp.stateVars["log"] = __sv_comp.stateVars["log"].(string) + "outer_after_inner,"
        // Our return should be independent of inner return
        s._context_stack[len(s._context_stack)-1]._return = "outer_result:" + inner_result
        return
    }
}

func main() {
	_ = strconv.Itoa // ensure import used
	fmt.Println("=== Test 16: System Return Reentrant (Nested Calls) ===")

	// Test 1: Simple inner call
	s1 := NewSystemReturnReentrantTest()
	result1 := s1.InnerCall()
	if result1 != "inner_result" {
		fmt.Printf("FAIL: Expected 'inner_result', got '%s'\n", result1)
		os.Exit(1)
	}
	fmt.Printf("1. InnerCall() = '%s'\n", result1)

	// Test 2: Outer calls inner - return contexts should be separate
	s2 := NewSystemReturnReentrantTest()
	result2 := s2.OuterCall()
	if result2 != "outer_result:inner_result" {
		fmt.Printf("FAIL: Expected 'outer_result:inner_result', got '%s'\n", result2)
		os.Exit(1)
	}
	fmt.Printf("2. OuterCall() = '%s'\n", result2)

	// Test 3: Deeply nested calls
	s3 := NewSystemReturnReentrantTest()
	result3 := s3.NestedCall()
	expected := "nested:inner_result+outer_result:inner_result"
	if result3 != expected {
		fmt.Printf("FAIL: Expected '%s', got '%s'\n", expected, result3)
		os.Exit(1)
	}
	fmt.Printf("3. NestedCall() = '%s'\n", result3)

	fmt.Println("PASS: System return reentrant (nested calls) works correctly")
}
