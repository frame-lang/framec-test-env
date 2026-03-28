
package main

import "fmt"
import "os"

type StateVarBasicFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type StateVarBasicFrameContext struct {
    _event  StateVarBasicFrameEvent
    _return any
    _data   map[string]any
}

type StateVarBasicCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *StateVarBasicFrameEvent
    parentCompartment *StateVarBasicCompartment
}

func newStateVarBasicCompartment(state string) *StateVarBasicCompartment {
    return &StateVarBasicCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *StateVarBasicCompartment) copy() *StateVarBasicCompartment {
    nc := &StateVarBasicCompartment{
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

type StateVarBasic struct {
    _state_stack []*StateVarBasicCompartment
    __compartment *StateVarBasicCompartment
    __next_compartment *StateVarBasicCompartment
    _context_stack []StateVarBasicFrameContext
}

func NewStateVarBasic() *StateVarBasic {
    s := &StateVarBasic{}
    s._state_stack = make([]*StateVarBasicCompartment, 0)
    s._context_stack = make([]StateVarBasicFrameContext, 0)
    s.__compartment = newStateVarBasicCompartment("Counter")
    s.__next_compartment = nil
    __frame_event := StateVarBasicFrameEvent{_message: "$>", _parameters: nil}
    __ctx := StateVarBasicFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *StateVarBasic) __kernel(__e *StateVarBasicFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &StateVarBasicFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &StateVarBasicFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &StateVarBasicFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *StateVarBasic) __router(__e *StateVarBasicFrameEvent) {
    switch s.__compartment.state {
    case "Counter":
        s._state_Counter(__e)
    }
}

func (s *StateVarBasic) __transition(next *StateVarBasicCompartment) {
    s.__next_compartment = next
}

func (s *StateVarBasic) Increment() int {
    __e := StateVarBasicFrameEvent{_message: "Increment"}
    __ctx := StateVarBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StateVarBasic) GetCount() int {
    __e := StateVarBasicFrameEvent{_message: "GetCount"}
    __ctx := StateVarBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StateVarBasic) Reset() {
    __e := StateVarBasicFrameEvent{_message: "Reset"}
    __ctx := StateVarBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StateVarBasic) _state_Counter(__e *StateVarBasicFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Counter" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["count"]; !ok {
            __sv_comp.stateVars["count"] = 0
        }
    } else if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["count"].(int)
        return
    } else if __e._message == "Increment" {
        __sv_comp.stateVars["count"] = __sv_comp.stateVars["count"].(int) + 1
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["count"].(int)
        return
    } else if __e._message == "Reset" {
        __sv_comp.stateVars["count"] = 0
    }
}

func main() {
	fmt.Println("=== Test 10: State Variable Basic ===")
	sm := NewStateVarBasic()

	// Initial value should be 0
	count := sm.GetCount()
	if count != 0 {
		fmt.Printf("FAIL: Expected 0, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Initial count: %d\n", count)

	// Increment should return new value
	result := sm.Increment()
	if result != 1 {
		fmt.Printf("FAIL: Expected 1 after first increment, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("After first increment: %d\n", result)

	// Second increment
	result = sm.Increment()
	if result != 2 {
		fmt.Printf("FAIL: Expected 2 after second increment, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("After second increment: %d\n", result)

	// Reset should set back to 0
	sm.Reset()
	count = sm.GetCount()
	if count != 0 {
		fmt.Printf("FAIL: Expected 0 after reset, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("After reset: %d\n", count)

	fmt.Println("PASS: State variable basic operations work correctly")
}
