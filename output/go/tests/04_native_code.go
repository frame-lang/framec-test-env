
package main

import (
	"fmt"
	"math"
	"os"
)

func helperFunction(x int) int {
	// Native helper function defined before system
	return x * 2
}

type NativeCodeFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type NativeCodeFrameContext struct {
    _event  NativeCodeFrameEvent
    _return any
    _data   map[string]any
}

type NativeCodeCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *NativeCodeFrameEvent
    parentCompartment *NativeCodeCompartment
}

func newNativeCodeCompartment(state string) *NativeCodeCompartment {
    return &NativeCodeCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *NativeCodeCompartment) copy() *NativeCodeCompartment {
    nc := &NativeCodeCompartment{
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

type NativeCode struct {
    _state_stack []*NativeCodeCompartment
    __compartment *NativeCodeCompartment
    __next_compartment *NativeCodeCompartment
    _context_stack []NativeCodeFrameContext
}

func NewNativeCode() *NativeCode {
    s := &NativeCode{}
    s._state_stack = make([]*NativeCodeCompartment, 0)
    s._context_stack = make([]NativeCodeFrameContext, 0)
    s.__compartment = newNativeCodeCompartment("Active")
    s.__next_compartment = nil
    __frame_event := NativeCodeFrameEvent{_message: "$>", _parameters: nil}
    __ctx := NativeCodeFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *NativeCode) __kernel(__e *NativeCodeFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &NativeCodeFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &NativeCodeFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &NativeCodeFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *NativeCode) __router(__e *NativeCodeFrameEvent) {
    switch s.__compartment.state {
    case "Active":
        s._state_Active(__e)
    }
}

func (s *NativeCode) __transition(next *NativeCodeCompartment) {
    s.__next_compartment = next
}

func (s *NativeCode) Compute(value int) int {
    __params := map[string]any{
        "value": value,
    }
    __e := NativeCodeFrameEvent{_message: "Compute", _parameters: __params}
    __ctx := NativeCodeFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *NativeCode) UseMath() float64 {
    __e := NativeCodeFrameEvent{_message: "UseMath"}
    __ctx := NativeCodeFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result float64
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(float64) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *NativeCode) _state_Active(__e *NativeCodeFrameEvent) {
    if __e._message == "Compute" {
        value := __e._parameters["value"].(int)
        _ = value
        // Native code with local variables
        temp := value + 10
        result := helperFunction(temp)
        fmt.Printf("Computed: %d -> %d\n", value, result)
        s._context_stack[len(s._context_stack)-1]._return = result
        return
    } else if __e._message == "UseMath" {
        // Using math module
        result := math.Sqrt(16) + math.Pi
        fmt.Printf("Math result: %f\n", result)
        s._context_stack[len(s._context_stack)-1]._return = result
        return
    }
}

func main() {
	fmt.Println("=== Test 04: Native Code Preservation ===")
	sm := NewNativeCode()

	// Test native code in handler with helper function
	result := sm.Compute(5)
	expected := (5 + 10) * 2 // 30
	if result != expected {
		fmt.Printf("FAIL: Expected %d, got %d\n", expected, result)
		os.Exit(1)
	}
	fmt.Printf("Compute(5) = %d\n", result)

	// Test math module usage
	mathResult := sm.UseMath()
	expectedMath := math.Sqrt(16) + math.Pi
	if math.Abs(mathResult-expectedMath) >= 0.001 {
		fmt.Printf("FAIL: Expected ~%f, got %f\n", expectedMath, mathResult)
		os.Exit(1)
	}
	fmt.Printf("UseMath() = %f\n", mathResult)

	fmt.Println("PASS: Native code preservation works correctly")
}
