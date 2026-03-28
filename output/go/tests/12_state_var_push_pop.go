
package main

import "fmt"
import "os"

type StateVarPushPopFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type StateVarPushPopFrameContext struct {
    _event  StateVarPushPopFrameEvent
    _return any
    _data   map[string]any
}

type StateVarPushPopCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *StateVarPushPopFrameEvent
    parentCompartment *StateVarPushPopCompartment
}

func newStateVarPushPopCompartment(state string) *StateVarPushPopCompartment {
    return &StateVarPushPopCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *StateVarPushPopCompartment) copy() *StateVarPushPopCompartment {
    nc := &StateVarPushPopCompartment{
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

type StateVarPushPop struct {
    _state_stack []*StateVarPushPopCompartment
    __compartment *StateVarPushPopCompartment
    __next_compartment *StateVarPushPopCompartment
    _context_stack []StateVarPushPopFrameContext
}

func NewStateVarPushPop() *StateVarPushPop {
    s := &StateVarPushPop{}
    s._state_stack = make([]*StateVarPushPopCompartment, 0)
    s._context_stack = make([]StateVarPushPopFrameContext, 0)
    s.__compartment = newStateVarPushPopCompartment("Counter")
    s.__next_compartment = nil
    __frame_event := StateVarPushPopFrameEvent{_message: "$>", _parameters: nil}
    __ctx := StateVarPushPopFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *StateVarPushPop) __kernel(__e *StateVarPushPopFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &StateVarPushPopFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &StateVarPushPopFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &StateVarPushPopFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *StateVarPushPop) __router(__e *StateVarPushPopFrameEvent) {
    switch s.__compartment.state {
    case "Counter":
        s._state_Counter(__e)
    case "Other":
        s._state_Other(__e)
    }
}

func (s *StateVarPushPop) __transition(next *StateVarPushPopCompartment) {
    s.__next_compartment = next
}

func (s *StateVarPushPop) Increment() int {
    __e := StateVarPushPopFrameEvent{_message: "Increment"}
    __ctx := StateVarPushPopFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StateVarPushPop) GetCount() int {
    __e := StateVarPushPopFrameEvent{_message: "GetCount"}
    __ctx := StateVarPushPopFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StateVarPushPop) SaveAndGo() {
    __e := StateVarPushPopFrameEvent{_message: "SaveAndGo"}
    __ctx := StateVarPushPopFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StateVarPushPop) Restore() {
    __e := StateVarPushPopFrameEvent{_message: "Restore"}
    __ctx := StateVarPushPopFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StateVarPushPop) _state_Other(__e *StateVarPushPopFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Other" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["other_count"]; !ok {
            __sv_comp.stateVars["other_count"] = 100
        }
    } else if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["other_count"].(int)
        return
    } else if __e._message == "Increment" {
        __sv_comp.stateVars["other_count"] = __sv_comp.stateVars["other_count"].(int) + 1
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["other_count"].(int)
        return
    } else if __e._message == "Restore" {
        __popped := s._state_stack[len(s._state_stack)-1]
        s._state_stack = s._state_stack[:len(s._state_stack)-1]
        s.__transition(__popped)
        return
    }
}

func (s *StateVarPushPop) _state_Counter(__e *StateVarPushPopFrameEvent) {
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
    } else if __e._message == "SaveAndGo" {
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newStateVarPushPopCompartment("Other")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func main() {
	fmt.Println("=== Test 12: State Variable Push/Pop ===")
	sm := NewStateVarPushPop()

	// Increment counter to 3
	sm.Increment()
	sm.Increment()
	sm.Increment()
	count := sm.GetCount()
	if count != 3 {
		fmt.Printf("FAIL: Expected 3, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Counter before push: %d\n", count)

	// Push and go to Other state
	sm.SaveAndGo()
	fmt.Println("Pushed and transitioned to Other")

	// In Other state, count should be 100 (Other's state var)
	count = sm.GetCount()
	if count != 100 {
		fmt.Printf("FAIL: Expected 100 in Other state, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Other state count: %d\n", count)

	// Increment in Other
	sm.Increment()
	count = sm.GetCount()
	if count != 101 {
		fmt.Printf("FAIL: Expected 101 after increment, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Other state after increment: %d\n", count)

	// Pop back - should restore Counter with count=3
	sm.Restore()
	fmt.Println("Popped back to Counter")

	count = sm.GetCount()
	if count != 3 {
		fmt.Printf("FAIL: Expected 3 after pop (preserved), got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Counter after pop: %d\n", count)

	// Increment to verify it works
	sm.Increment()
	count = sm.GetCount()
	if count != 4 {
		fmt.Printf("FAIL: Expected 4, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Counter after increment: %d\n", count)

	fmt.Println("PASS: State variables preserved across push/pop")
}
