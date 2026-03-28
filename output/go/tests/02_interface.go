
package main

import "fmt"
import "os"

type WithInterfaceFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type WithInterfaceFrameContext struct {
    _event  WithInterfaceFrameEvent
    _return any
    _data   map[string]any
}

type WithInterfaceCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *WithInterfaceFrameEvent
    parentCompartment *WithInterfaceCompartment
}

func newWithInterfaceCompartment(state string) *WithInterfaceCompartment {
    return &WithInterfaceCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *WithInterfaceCompartment) copy() *WithInterfaceCompartment {
    nc := &WithInterfaceCompartment{
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

type WithInterface struct {
    _state_stack []*WithInterfaceCompartment
    __compartment *WithInterfaceCompartment
    __next_compartment *WithInterfaceCompartment
    _context_stack []WithInterfaceFrameContext
    call_count int
}

func NewWithInterface() *WithInterface {
    s := &WithInterface{}
    s._state_stack = make([]*WithInterfaceCompartment, 0)
    s._context_stack = make([]WithInterfaceFrameContext, 0)
    s.__compartment = newWithInterfaceCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := WithInterfaceFrameEvent{_message: "$>", _parameters: nil}
    __ctx := WithInterfaceFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *WithInterface) __kernel(__e *WithInterfaceFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &WithInterfaceFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &WithInterfaceFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &WithInterfaceFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *WithInterface) __router(__e *WithInterfaceFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *WithInterface) __transition(next *WithInterfaceCompartment) {
    s.__next_compartment = next
}

func (s *WithInterface) Greet(name string) string {
    __params := map[string]any{
        "name": name,
    }
    __e := WithInterfaceFrameEvent{_message: "Greet", _parameters: __params}
    __ctx := WithInterfaceFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *WithInterface) GetCount() int {
    __e := WithInterfaceFrameEvent{_message: "GetCount"}
    __ctx := WithInterfaceFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *WithInterface) _state_Ready(__e *WithInterfaceFrameEvent) {
    if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = s.call_count
        return
    } else if __e._message == "Greet" {
        name := __e._parameters["name"].(string)
        _ = name
        s.call_count += 1
        s._context_stack[len(s._context_stack)-1]._return = "Hello, " + name + "!"
        return
    }
}

func main() {
	fmt.Println("=== Test 02: Interface Methods ===")
	sm := NewWithInterface()

	// Test interface method with parameter and return
	result := sm.Greet("World")
	if result != "Hello, World!" {
		fmt.Printf("FAIL: Expected 'Hello, World!', got '%s'\n", result)
		os.Exit(1)
	}
	fmt.Printf("Greet('World') = %s\n", result)

	// Test domain variable access through interface
	count := sm.GetCount()
	if count != 1 {
		fmt.Printf("FAIL: Expected count=1, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("GetCount() = %d\n", count)

	// Call again to verify state
	sm.Greet("Frame")
	count2 := sm.GetCount()
	if count2 != 2 {
		fmt.Printf("FAIL: Expected count=2, got %d\n", count2)
		os.Exit(1)
	}
	fmt.Printf("After second call: GetCount() = %d\n", count2)

	fmt.Println("PASS: Interface methods work correctly")
}
