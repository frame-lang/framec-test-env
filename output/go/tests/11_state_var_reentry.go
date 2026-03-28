
package main

import "fmt"
import "os"

type StateVarReentryFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type StateVarReentryFrameContext struct {
    _event  StateVarReentryFrameEvent
    _return any
    _data   map[string]any
}

type StateVarReentryCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *StateVarReentryFrameEvent
    parentCompartment *StateVarReentryCompartment
}

func newStateVarReentryCompartment(state string) *StateVarReentryCompartment {
    return &StateVarReentryCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *StateVarReentryCompartment) copy() *StateVarReentryCompartment {
    nc := &StateVarReentryCompartment{
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

type StateVarReentry struct {
    _state_stack []*StateVarReentryCompartment
    __compartment *StateVarReentryCompartment
    __next_compartment *StateVarReentryCompartment
    _context_stack []StateVarReentryFrameContext
}

func NewStateVarReentry() *StateVarReentry {
    s := &StateVarReentry{}
    s._state_stack = make([]*StateVarReentryCompartment, 0)
    s._context_stack = make([]StateVarReentryFrameContext, 0)
    s.__compartment = newStateVarReentryCompartment("Counter")
    s.__next_compartment = nil
    __frame_event := StateVarReentryFrameEvent{_message: "$>", _parameters: nil}
    __ctx := StateVarReentryFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *StateVarReentry) __kernel(__e *StateVarReentryFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &StateVarReentryFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &StateVarReentryFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &StateVarReentryFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *StateVarReentry) __router(__e *StateVarReentryFrameEvent) {
    switch s.__compartment.state {
    case "Counter":
        s._state_Counter(__e)
    case "Other":
        s._state_Other(__e)
    }
}

func (s *StateVarReentry) __transition(next *StateVarReentryCompartment) {
    s.__next_compartment = next
}

func (s *StateVarReentry) Increment() int {
    __e := StateVarReentryFrameEvent{_message: "Increment"}
    __ctx := StateVarReentryFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StateVarReentry) GetCount() int {
    __e := StateVarReentryFrameEvent{_message: "GetCount"}
    __ctx := StateVarReentryFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StateVarReentry) GoOther() {
    __e := StateVarReentryFrameEvent{_message: "GoOther"}
    __ctx := StateVarReentryFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StateVarReentry) ComeBack() {
    __e := StateVarReentryFrameEvent{_message: "ComeBack"}
    __ctx := StateVarReentryFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StateVarReentry) _state_Other(__e *StateVarReentryFrameEvent) {
    if __e._message == "ComeBack" {
        __compartment := newStateVarReentryCompartment("Counter")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = -1
        return
    } else if __e._message == "Increment" {
        s._context_stack[len(s._context_stack)-1]._return = -1
        return
    }
}

func (s *StateVarReentry) _state_Counter(__e *StateVarReentryFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Counter" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["count"]; !ok {
            __sv_comp.stateVars["count"] = 0
        }
    } else if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["count"].(int)
        return
    } else if __e._message == "GoOther" {
        __compartment := newStateVarReentryCompartment("Other")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "Increment" {
        __sv_comp.stateVars["count"] = __sv_comp.stateVars["count"].(int) + 1
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["count"].(int)
        return
    }
}

func main() {
	fmt.Println("=== Test 11: State Variable Reentry ===")
	sm := NewStateVarReentry()

	// Increment a few times
	sm.Increment()
	sm.Increment()
	count := sm.GetCount()
	if count != 2 {
		fmt.Printf("FAIL: Expected 2 after two increments, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Count before leaving: %d\n", count)

	// Leave the state
	sm.GoOther()
	fmt.Println("Transitioned to Other state")

	// Come back - state var should be reinitialized to 0
	sm.ComeBack()
	count = sm.GetCount()
	if count != 0 {
		fmt.Printf("FAIL: Expected 0 after re-entering Counter (state var reinit), got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Count after re-entering Counter: %d\n", count)

	// Increment again to verify it works
	result := sm.Increment()
	if result != 1 {
		fmt.Printf("FAIL: Expected 1 after increment, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("After increment: %d\n", result)

	fmt.Println("PASS: State variables reinitialize on state reentry")
}
