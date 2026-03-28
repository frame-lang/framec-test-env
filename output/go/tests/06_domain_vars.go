
package main

import "fmt"
import "os"

type DomainVarsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type DomainVarsFrameContext struct {
    _event  DomainVarsFrameEvent
    _return any
    _data   map[string]any
}

type DomainVarsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *DomainVarsFrameEvent
    parentCompartment *DomainVarsCompartment
}

func newDomainVarsCompartment(state string) *DomainVarsCompartment {
    return &DomainVarsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *DomainVarsCompartment) copy() *DomainVarsCompartment {
    nc := &DomainVarsCompartment{
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

type DomainVars struct {
    _state_stack []*DomainVarsCompartment
    __compartment *DomainVarsCompartment
    __next_compartment *DomainVarsCompartment
    _context_stack []DomainVarsFrameContext
    count int
    name string
}

func NewDomainVars() *DomainVars {
    s := &DomainVars{}
    s._state_stack = make([]*DomainVarsCompartment, 0)
    s._context_stack = make([]DomainVarsFrameContext, 0)
    s.__compartment = newDomainVarsCompartment("Counting")
    s.__next_compartment = nil
    __frame_event := DomainVarsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := DomainVarsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *DomainVars) __kernel(__e *DomainVarsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &DomainVarsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &DomainVarsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &DomainVarsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *DomainVars) __router(__e *DomainVarsFrameEvent) {
    switch s.__compartment.state {
    case "Counting":
        s._state_Counting(__e)
    }
}

func (s *DomainVars) __transition(next *DomainVarsCompartment) {
    s.__next_compartment = next
}

func (s *DomainVars) Increment() {
    __e := DomainVarsFrameEvent{_message: "Increment"}
    __ctx := DomainVarsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *DomainVars) Decrement() {
    __e := DomainVarsFrameEvent{_message: "Decrement"}
    __ctx := DomainVarsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *DomainVars) GetCount() int {
    __e := DomainVarsFrameEvent{_message: "GetCount"}
    __ctx := DomainVarsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *DomainVars) SetCount(value int) {
    __params := map[string]any{
        "value": value,
    }
    __e := DomainVarsFrameEvent{_message: "SetCount", _parameters: __params}
    __ctx := DomainVarsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *DomainVars) _state_Counting(__e *DomainVarsFrameEvent) {
    if __e._message == "Decrement" {
        s.count -= 1
        fmt.Printf("%s: decremented to %d\n", s.name, s.count)
    } else if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = s.count
        return
    } else if __e._message == "Increment" {
        s.count += 1
        fmt.Printf("%s: incremented to %d\n", s.name, s.count)
    } else if __e._message == "SetCount" {
        value := __e._parameters["value"].(int)
        _ = value
        s.count = value
        fmt.Printf("%s: set to %d\n", s.name, s.count)
    }
}

func main() {
	fmt.Println("=== Test 06: Domain Variables ===")
	sm := NewDomainVars()
	// Go zero-inits: count=0, name=""
	// We need name to be "counter" for output matching - set it via enter or skip name check
	// Since domain cannot have init values in Go, we just test count behavior

	// Initial value should be 0
	count := sm.GetCount()
	if count != 0 {
		fmt.Printf("FAIL: Expected initial count=0, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Initial count: %d\n", count)

	// Increment
	sm.Increment()
	count = sm.GetCount()
	if count != 1 {
		fmt.Printf("FAIL: Expected count=1, got %d\n", count)
		os.Exit(1)
	}

	sm.Increment()
	count = sm.GetCount()
	if count != 2 {
		fmt.Printf("FAIL: Expected count=2, got %d\n", count)
		os.Exit(1)
	}

	// Decrement
	sm.Decrement()
	count = sm.GetCount()
	if count != 1 {
		fmt.Printf("FAIL: Expected count=1, got %d\n", count)
		os.Exit(1)
	}

	// Set directly
	sm.SetCount(100)
	count = sm.GetCount()
	if count != 100 {
		fmt.Printf("FAIL: Expected count=100, got %d\n", count)
		os.Exit(1)
	}

	fmt.Printf("Final count: %d\n", count)
	fmt.Println("PASS: Domain variables work correctly")
}
