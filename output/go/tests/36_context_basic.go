
package main

import "fmt"
import "os"

type ContextBasicTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type ContextBasicTestFrameContext struct {
    _event  ContextBasicTestFrameEvent
    _return any
    _data   map[string]any
}

type ContextBasicTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *ContextBasicTestFrameEvent
    parentCompartment *ContextBasicTestCompartment
}

func newContextBasicTestCompartment(state string) *ContextBasicTestCompartment {
    return &ContextBasicTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *ContextBasicTestCompartment) copy() *ContextBasicTestCompartment {
    nc := &ContextBasicTestCompartment{
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

type ContextBasicTest struct {
    _state_stack []*ContextBasicTestCompartment
    __compartment *ContextBasicTestCompartment
    __next_compartment *ContextBasicTestCompartment
    _context_stack []ContextBasicTestFrameContext
}

func NewContextBasicTest() *ContextBasicTest {
    s := &ContextBasicTest{}
    s._state_stack = make([]*ContextBasicTestCompartment, 0)
    s._context_stack = make([]ContextBasicTestFrameContext, 0)
    s.__compartment = newContextBasicTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := ContextBasicTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := ContextBasicTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *ContextBasicTest) __kernel(__e *ContextBasicTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &ContextBasicTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &ContextBasicTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &ContextBasicTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *ContextBasicTest) __router(__e *ContextBasicTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *ContextBasicTest) __transition(next *ContextBasicTestCompartment) {
    s.__next_compartment = next
}

func (s *ContextBasicTest) Add(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := ContextBasicTestFrameEvent{_message: "Add", _parameters: __params}
    __ctx := ContextBasicTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextBasicTest) GetEventName() string {
    __e := ContextBasicTestFrameEvent{_message: "GetEventName"}
    __ctx := ContextBasicTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextBasicTest) Greet(name string) string {
    __params := map[string]any{
        "name": name,
    }
    __e := ContextBasicTestFrameEvent{_message: "Greet", _parameters: __params}
    __ctx := ContextBasicTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextBasicTest) _state_Ready(__e *ContextBasicTestFrameEvent) {
    if __e._message == "Add" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        // Access params directly (Go backend extracts them)
        s._context_stack[len(s._context_stack)-1]._return = a + b
    } else if __e._message == "GetEventName" {
        // Access event name via __e
        s._context_stack[len(s._context_stack)-1]._return = __e._message
    } else if __e._message == "Greet" {
        name := __e._parameters["name"].(string)
        _ = name
        // Mix param access and return
        result := "Hello, " + name + "!"
        s._context_stack[len(s._context_stack)-1]._return = result
    }
}

func main() {
	fmt.Println("=== Test 36: Context Basic ===")
	sm := NewContextBasicTest()

	// Test 1: param access, @@:return
	result1 := sm.Add(3, 5)
	if result1 != 8 {
		fmt.Printf("FAIL: Expected 8, got %d\n", result1)
		os.Exit(1)
	}
	fmt.Printf("1. Add(3, 5) = %d\n", result1)

	// Test 2: event name access
	eventName := sm.GetEventName()
	if eventName != "GetEventName" {
		fmt.Printf("FAIL: Expected 'GetEventName', got '%s'\n", eventName)
		os.Exit(1)
	}
	fmt.Printf("2. event = '%s'\n", eventName)

	// Test 3: param access with string
	greeting := sm.Greet("World")
	if greeting != "Hello, World!" {
		fmt.Printf("FAIL: Expected 'Hello, World!', got '%s'\n", greeting)
		os.Exit(1)
	}
	fmt.Printf("3. Greet('World') = '%s'\n", greeting)

	fmt.Println("PASS: Context basic access works correctly")
}
