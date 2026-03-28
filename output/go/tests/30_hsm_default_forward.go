
package main

import "fmt"
import "os"

type HSMDefaultForwardFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMDefaultForwardFrameContext struct {
    _event  HSMDefaultForwardFrameEvent
    _return any
    _data   map[string]any
}

type HSMDefaultForwardCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMDefaultForwardFrameEvent
    parentCompartment *HSMDefaultForwardCompartment
}

func newHSMDefaultForwardCompartment(state string) *HSMDefaultForwardCompartment {
    return &HSMDefaultForwardCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMDefaultForwardCompartment) copy() *HSMDefaultForwardCompartment {
    nc := &HSMDefaultForwardCompartment{
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

type HSMDefaultForward struct {
    _state_stack []*HSMDefaultForwardCompartment
    __compartment *HSMDefaultForwardCompartment
    __next_compartment *HSMDefaultForwardCompartment
    _context_stack []HSMDefaultForwardFrameContext
    log []string
}

func NewHSMDefaultForward() *HSMDefaultForward {
    s := &HSMDefaultForward{}
    s._state_stack = make([]*HSMDefaultForwardCompartment, 0)
    s._context_stack = make([]HSMDefaultForwardFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMDefaultForwardCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMDefaultForwardCompartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMDefaultForwardFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMDefaultForwardFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMDefaultForward) __kernel(__e *HSMDefaultForwardFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMDefaultForwardFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMDefaultForwardFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMDefaultForwardFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMDefaultForward) __router(__e *HSMDefaultForwardFrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMDefaultForward) __transition(next *HSMDefaultForwardCompartment) {
    s.__next_compartment = next
}

func (s *HSMDefaultForward) HandledEvent() {
    __e := HSMDefaultForwardFrameEvent{_message: "HandledEvent"}
    __ctx := HSMDefaultForwardFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMDefaultForward) UnhandledEvent() {
    __e := HSMDefaultForwardFrameEvent{_message: "UnhandledEvent"}
    __ctx := HSMDefaultForwardFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMDefaultForward) GetLog() []string {
    __e := HSMDefaultForwardFrameEvent{_message: "GetLog"}
    __ctx := HSMDefaultForwardFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMDefaultForward) _state_Parent(__e *HSMDefaultForwardFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "HandledEvent" {
        s.log = append(s.log, "Parent:handled_event")
    } else if __e._message == "UnhandledEvent" {
        s.log = append(s.log, "Parent:unhandled_event")
    }
}

func (s *HSMDefaultForward) _state_Child(__e *HSMDefaultForwardFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "HandledEvent" {
        s.log = append(s.log, "Child:handled_event")
    } else {
        s._state_Parent(__e)
    }
}

func contains(slice []string, item string) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}

func main() {
	fmt.Println("=== Test 30: HSM State-Level Default Forward ===")
	sm := NewHSMDefaultForward()

	sm.HandledEvent()
	log := sm.GetLog()
	if !contains(log, "Child:handled_event") {
		fmt.Printf("FAIL: Expected 'Child:handled_event' in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("After HandledEvent: %v\n", log)

	sm.UnhandledEvent()
	log = sm.GetLog()
	if !contains(log, "Parent:unhandled_event") {
		fmt.Printf("FAIL: Expected 'Parent:unhandled_event' in log (forwarded), got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("After UnhandledEvent (forwarded): %v\n", log)

	fmt.Println("PASS: HSM state-level default forward works correctly")
}
