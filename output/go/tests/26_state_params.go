
package main

import "fmt"
import "os"

type StateParamsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type StateParamsFrameContext struct {
    _event  StateParamsFrameEvent
    _return any
    _data   map[string]any
}

type StateParamsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *StateParamsFrameEvent
    parentCompartment *StateParamsCompartment
}

func newStateParamsCompartment(state string) *StateParamsCompartment {
    return &StateParamsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *StateParamsCompartment) copy() *StateParamsCompartment {
    nc := &StateParamsCompartment{
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

type StateParams struct {
    _state_stack []*StateParamsCompartment
    __compartment *StateParamsCompartment
    __next_compartment *StateParamsCompartment
    _context_stack []StateParamsFrameContext
}

func NewStateParams() *StateParams {
    s := &StateParams{}
    s._state_stack = make([]*StateParamsCompartment, 0)
    s._context_stack = make([]StateParamsFrameContext, 0)
    s.__compartment = newStateParamsCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := StateParamsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := StateParamsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *StateParams) __kernel(__e *StateParamsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &StateParamsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &StateParamsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &StateParamsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *StateParams) __router(__e *StateParamsFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Counter":
        s._state_Counter(__e)
    }
}

func (s *StateParams) __transition(next *StateParamsCompartment) {
    s.__next_compartment = next
}

func (s *StateParams) Start(val int) {
    __params := map[string]any{
        "val": val,
    }
    __e := StateParamsFrameEvent{_message: "Start", _parameters: __params}
    __ctx := StateParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StateParams) GetValue() int {
    __e := StateParamsFrameEvent{_message: "GetValue"}
    __ctx := StateParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StateParams) _state_Counter(__e *StateParamsFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Counter" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["count"]; !ok {
            __sv_comp.stateVars["count"] = 0
        }
        // Access state param via compartment stateArgs
        __sv_comp.stateVars["count"] = s.__compartment.stateArgs["0"].(int)
        count_val := __sv_comp.stateVars["count"].(int)
        fmt.Printf("Counter entered with initial=%d\n", count_val)
    } else if __e._message == "GetValue" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["count"].(int)
        return
    }
}

func (s *StateParams) _state_Idle(__e *StateParamsFrameEvent) {
    if __e._message == "GetValue" {
        s._context_stack[len(s._context_stack)-1]._return = 0
        return
    } else if __e._message == "Start" {
        val := __e._parameters["val"].(int)
        _ = val
        __compartment := newStateParamsCompartment("Counter")
        __compartment.parentCompartment = s.__compartment.copy()
        __compartment.stateArgs["0"] = val
        s.__transition(__compartment)
        return
    }
}

func main() {
	fmt.Println("=== Test 26: State Parameters ===")
	sm := NewStateParams()

	val := sm.GetValue()
	if val != 0 {
		fmt.Printf("FAIL: Expected 0 in Idle, got %d\n", val)
		os.Exit(1)
	}
	fmt.Printf("Initial value: %d\n", val)

	sm.Start(42)
	val = sm.GetValue()
	if val != 42 {
		fmt.Printf("FAIL: Expected 42 in Counter from state param, got %d\n", val)
		os.Exit(1)
	}
	fmt.Printf("Value after transition: %d\n", val)

	fmt.Println("PASS: State parameters work correctly")
}
