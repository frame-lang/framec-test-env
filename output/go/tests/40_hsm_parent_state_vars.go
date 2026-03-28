
package main

import "fmt"
import "os"

type HSMParentStateVarsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMParentStateVarsFrameContext struct {
    _event  HSMParentStateVarsFrameEvent
    _return any
    _data   map[string]any
}

type HSMParentStateVarsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMParentStateVarsFrameEvent
    parentCompartment *HSMParentStateVarsCompartment
}

func newHSMParentStateVarsCompartment(state string) *HSMParentStateVarsCompartment {
    return &HSMParentStateVarsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMParentStateVarsCompartment) copy() *HSMParentStateVarsCompartment {
    nc := &HSMParentStateVarsCompartment{
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

type HSMParentStateVars struct {
    _state_stack []*HSMParentStateVarsCompartment
    __compartment *HSMParentStateVarsCompartment
    __next_compartment *HSMParentStateVarsCompartment
    _context_stack []HSMParentStateVarsFrameContext
}

func NewHSMParentStateVars() *HSMParentStateVars {
    s := &HSMParentStateVars{}
    s._state_stack = make([]*HSMParentStateVarsCompartment, 0)
    s._context_stack = make([]HSMParentStateVarsFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMParentStateVarsCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    __parent_comp_0.stateVars["parent_count"] = 100
    s.__compartment = newHSMParentStateVarsCompartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMParentStateVarsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMParentStateVarsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMParentStateVars) __kernel(__e *HSMParentStateVarsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMParentStateVarsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMParentStateVarsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMParentStateVarsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMParentStateVars) __router(__e *HSMParentStateVarsFrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMParentStateVars) __transition(next *HSMParentStateVarsCompartment) {
    s.__next_compartment = next
}

func (s *HSMParentStateVars) GetChildCount() int {
    __e := HSMParentStateVarsFrameEvent{_message: "GetChildCount"}
    __ctx := HSMParentStateVarsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMParentStateVars) GetParentCount() int {
    __e := HSMParentStateVarsFrameEvent{_message: "GetParentCount"}
    __ctx := HSMParentStateVarsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMParentStateVars) _state_Child(__e *HSMParentStateVarsFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Child" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["child_count"]; !ok {
            __sv_comp.stateVars["child_count"] = 0
        }
    } else if __e._message == "GetChildCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["child_count"].(int)
        return
    } else if __e._message == "GetParentCount" {
        s._state_Parent(__e)
    }
}

func (s *HSMParentStateVars) _state_Parent(__e *HSMParentStateVarsFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Parent" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["parent_count"]; !ok {
            __sv_comp.stateVars["parent_count"] = 100
        }
    } else if __e._message == "GetParentCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["parent_count"].(int)
        return
    }
}

func main() {
	fmt.Println("=== Test 40: HSM Parent State Variables ===")
	sm := NewHSMParentStateVars()

	childCount := sm.GetChildCount()
	if childCount != 0 {
		fmt.Printf("FAIL: Expected child_count=0, got %d\n", childCount)
		os.Exit(1)
	}
	fmt.Printf("Child count: %d\n", childCount)

	parentCount := sm.GetParentCount()
	if parentCount != 100 {
		fmt.Printf("FAIL: Expected parent_count=100, got %d\n", parentCount)
		os.Exit(1)
	}
	fmt.Printf("Parent count: %d\n", parentCount)

	fmt.Println("PASS: HSM parent state variables work correctly")
}
