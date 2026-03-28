
package main

import "fmt"
import "os"

// NOTE: Default return value syntax (method(): type = default) not yet implemented.
// This test validates behavior when handler does not set @@:return.

type SystemReturnDefaultTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SystemReturnDefaultTestFrameContext struct {
    _event  SystemReturnDefaultTestFrameEvent
    _return any
    _data   map[string]any
}

type SystemReturnDefaultTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SystemReturnDefaultTestFrameEvent
    parentCompartment *SystemReturnDefaultTestCompartment
}

func newSystemReturnDefaultTestCompartment(state string) *SystemReturnDefaultTestCompartment {
    return &SystemReturnDefaultTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SystemReturnDefaultTestCompartment) copy() *SystemReturnDefaultTestCompartment {
    nc := &SystemReturnDefaultTestCompartment{
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

type SystemReturnDefaultTest struct {
    _state_stack []*SystemReturnDefaultTestCompartment
    __compartment *SystemReturnDefaultTestCompartment
    __next_compartment *SystemReturnDefaultTestCompartment
    _context_stack []SystemReturnDefaultTestFrameContext
}

func NewSystemReturnDefaultTest() *SystemReturnDefaultTest {
    s := &SystemReturnDefaultTest{}
    s._state_stack = make([]*SystemReturnDefaultTestCompartment, 0)
    s._context_stack = make([]SystemReturnDefaultTestFrameContext, 0)
    s.__compartment = newSystemReturnDefaultTestCompartment("Start")
    s.__next_compartment = nil
    __frame_event := SystemReturnDefaultTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SystemReturnDefaultTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *SystemReturnDefaultTest) __kernel(__e *SystemReturnDefaultTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SystemReturnDefaultTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SystemReturnDefaultTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SystemReturnDefaultTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *SystemReturnDefaultTest) __router(__e *SystemReturnDefaultTestFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    }
}

func (s *SystemReturnDefaultTest) __transition(next *SystemReturnDefaultTestCompartment) {
    s.__next_compartment = next
}

func (s *SystemReturnDefaultTest) HandlerSetsValue() string {
    __e := SystemReturnDefaultTestFrameEvent{_message: "HandlerSetsValue"}
    __ctx := SystemReturnDefaultTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnDefaultTest) HandlerNoReturn() string {
    __e := SystemReturnDefaultTestFrameEvent{_message: "HandlerNoReturn"}
    __ctx := SystemReturnDefaultTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnDefaultTest) GetCount() int {
    __e := SystemReturnDefaultTestFrameEvent{_message: "GetCount"}
    __ctx := SystemReturnDefaultTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnDefaultTest) _state_Start(__e *SystemReturnDefaultTestFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Start" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["count"]; !ok {
            __sv_comp.stateVars["count"] = 0
        }
    } else if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["count"].(int)
        return
    } else if __e._message == "HandlerNoReturn" {
        // Does not set return - should return nil/zero
        __sv_comp.stateVars["count"] = __sv_comp.stateVars["count"].(int) + 1
    } else if __e._message == "HandlerSetsValue" {
        s._context_stack[len(s._context_stack)-1]._return = "set_by_handler"
        return
    }
}

func main() {
	fmt.Println("=== Test 14: System Return Default Behavior ===")
	sm := NewSystemReturnDefaultTest()

	// Test 1: Handler explicitly sets return value
	result1 := sm.HandlerSetsValue()
	if result1 != "set_by_handler" {
		fmt.Printf("FAIL: Expected 'set_by_handler', got '%s'\n", result1)
		os.Exit(1)
	}
	fmt.Printf("1. HandlerSetsValue() = '%s'\n", result1)

	// Test 2: Handler does NOT set return - should return empty string (Go zero value)
	result2 := sm.HandlerNoReturn()
	if result2 != "" {
		fmt.Printf("FAIL: Expected empty string, got '%s'\n", result2)
		os.Exit(1)
	}
	fmt.Printf("2. HandlerNoReturn() = '%s'\n", result2)

	// Test 3: Verify handler was called (side effect check)
	count := sm.GetCount()
	if count != 1 {
		fmt.Printf("FAIL: Expected count=1, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("3. Handler was called, count = %d\n", count)

	// Test 4: Call again to verify idempotence
	result4 := sm.HandlerNoReturn()
	if result4 != "" {
		fmt.Printf("FAIL: Expected empty string again, got '%s'\n", result4)
		os.Exit(1)
	}
	count = sm.GetCount()
	if count != 2 {
		fmt.Printf("FAIL: Expected count=2, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("4. Second call: result='%s', count=%d\n", result4, count)

	fmt.Println("PASS: System return default behavior works correctly")
}
