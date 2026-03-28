
package main

import (
	"fmt"
	"os"
	"strconv"
)

type ContextReentrantTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type ContextReentrantTestFrameContext struct {
    _event  ContextReentrantTestFrameEvent
    _return any
    _data   map[string]any
}

type ContextReentrantTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *ContextReentrantTestFrameEvent
    parentCompartment *ContextReentrantTestCompartment
}

func newContextReentrantTestCompartment(state string) *ContextReentrantTestCompartment {
    return &ContextReentrantTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *ContextReentrantTestCompartment) copy() *ContextReentrantTestCompartment {
    nc := &ContextReentrantTestCompartment{
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

type ContextReentrantTest struct {
    _state_stack []*ContextReentrantTestCompartment
    __compartment *ContextReentrantTestCompartment
    __next_compartment *ContextReentrantTestCompartment
    _context_stack []ContextReentrantTestFrameContext
}

func NewContextReentrantTest() *ContextReentrantTest {
    s := &ContextReentrantTest{}
    s._state_stack = make([]*ContextReentrantTestCompartment, 0)
    s._context_stack = make([]ContextReentrantTestFrameContext, 0)
    s.__compartment = newContextReentrantTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := ContextReentrantTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := ContextReentrantTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *ContextReentrantTest) __kernel(__e *ContextReentrantTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &ContextReentrantTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &ContextReentrantTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &ContextReentrantTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *ContextReentrantTest) __router(__e *ContextReentrantTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *ContextReentrantTest) __transition(next *ContextReentrantTestCompartment) {
    s.__next_compartment = next
}

func (s *ContextReentrantTest) Outer(x int) string {
    __params := map[string]any{
        "x": x,
    }
    __e := ContextReentrantTestFrameEvent{_message: "Outer", _parameters: __params}
    __ctx := ContextReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextReentrantTest) Inner(y int) string {
    __params := map[string]any{
        "y": y,
    }
    __e := ContextReentrantTestFrameEvent{_message: "Inner", _parameters: __params}
    __ctx := ContextReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextReentrantTest) DeeplyNested(z int) string {
    __params := map[string]any{
        "z": z,
    }
    __e := ContextReentrantTestFrameEvent{_message: "DeeplyNested", _parameters: __params}
    __ctx := ContextReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextReentrantTest) GetBoth(a int, b int) string {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := ContextReentrantTestFrameEvent{_message: "GetBoth", _parameters: __params}
    __ctx := ContextReentrantTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextReentrantTest) _state_Ready(__e *ContextReentrantTestFrameEvent) {
    if __e._message == "DeeplyNested" {
        z := __e._parameters["z"].(int)
        _ = z
        // 3 levels deep
        outer_result := s.Outer(z)
        s._context_stack[len(s._context_stack)-1]._return = "deep:" + strconv.Itoa(z) + "," + outer_result
    } else if __e._message == "GetBoth" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        // Test that we can access multiple params
        result_a := s.Inner(a)
        result_b := s.Inner(b)
        // After both inner calls, a and b should still be our params
        s._context_stack[len(s._context_stack)-1]._return = "a=" + strconv.Itoa(a) + ",b=" + strconv.Itoa(b) + ",results=" + result_a + "+" + result_b
    } else if __e._message == "Inner" {
        y := __e._parameters["y"].(int)
        _ = y
        // Inner has its own context
        s._context_stack[len(s._context_stack)-1]._return = strconv.Itoa(y)
    } else if __e._message == "Outer" {
        x := __e._parameters["x"].(int)
        _ = x
        // Set our return before calling inner
        s._context_stack[len(s._context_stack)-1]._return = "outer_initial"

        // Call inner - should NOT clobber our return
        inner_result := s.Inner(x * 10)

        // Our return should still be accessible
        // Update it with combined result
        s._context_stack[len(s._context_stack)-1]._return = "outer:" + strconv.Itoa(x) + ",inner:" + inner_result
    }
}

func main() {
	fmt.Println("=== Test 37: Context Reentrant ===")
	sm := NewContextReentrantTest()

	// Test 1: Simple nesting - outer calls inner
	result := sm.Outer(5)
	expected := "outer:5,inner:50"
	if result != expected {
		fmt.Printf("FAIL: Expected '%s', got '%s'\n", expected, result)
		os.Exit(1)
	}
	fmt.Printf("1. Outer(5) = '%s'\n", result)

	// Test 2: Inner alone
	result = sm.Inner(42)
	if result != "42" {
		fmt.Printf("FAIL: Expected '42', got '%s'\n", result)
		os.Exit(1)
	}
	fmt.Printf("2. Inner(42) = '%s'\n", result)

	// Test 3: Deep nesting (3 levels)
	result = sm.DeeplyNested(3)
	expected = "deep:3,outer:3,inner:30"
	if result != expected {
		fmt.Printf("FAIL: Expected '%s', got '%s'\n", expected, result)
		os.Exit(1)
	}
	fmt.Printf("3. DeeplyNested(3) = '%s'\n", result)

	// Test 4: Multiple inner calls, params preserved
	result = sm.GetBoth(10, 20)
	expected = "a=10,b=20,results=10+20"
	if result != expected {
		fmt.Printf("FAIL: Expected '%s', got '%s'\n", expected, result)
		os.Exit(1)
	}
	fmt.Printf("4. GetBoth(10, 20) = '%s'\n", result)

	fmt.Println("PASS: Context reentrant works correctly")
}
