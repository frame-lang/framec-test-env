
package main

import "fmt"
import "os"

type HSMForwardFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMForwardFrameContext struct {
    _event  HSMForwardFrameEvent
    _return any
    _data   map[string]any
}

type HSMForwardCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMForwardFrameEvent
    parentCompartment *HSMForwardCompartment
}

func newHSMForwardCompartment(state string) *HSMForwardCompartment {
    return &HSMForwardCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMForwardCompartment) copy() *HSMForwardCompartment {
    nc := &HSMForwardCompartment{
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

type HSMForward struct {
    _state_stack []*HSMForwardCompartment
    __compartment *HSMForwardCompartment
    __next_compartment *HSMForwardCompartment
    _context_stack []HSMForwardFrameContext
    log []string
}

func NewHSMForward() *HSMForward {
    s := &HSMForward{}
    s._state_stack = make([]*HSMForwardCompartment, 0)
    s._context_stack = make([]HSMForwardFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMForwardCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMForwardCompartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMForwardFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMForwardFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMForward) __kernel(__e *HSMForwardFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMForwardFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMForwardFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMForwardFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMForward) __router(__e *HSMForwardFrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMForward) __transition(next *HSMForwardCompartment) {
    s.__next_compartment = next
}

func (s *HSMForward) EventA() {
    __e := HSMForwardFrameEvent{_message: "EventA"}
    __ctx := HSMForwardFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMForward) EventB() {
    __e := HSMForwardFrameEvent{_message: "EventB"}
    __ctx := HSMForwardFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMForward) GetLog() []string {
    __e := HSMForwardFrameEvent{_message: "GetLog"}
    __ctx := HSMForwardFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMForward) _state_Parent(__e *HSMForwardFrameEvent) {
    if __e._message == "EventA" {
        s.log = append(s.log, "Parent:event_a")
    } else if __e._message == "EventB" {
        s.log = append(s.log, "Parent:event_b")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    }
}

func (s *HSMForward) _state_Child(__e *HSMForwardFrameEvent) {
    if __e._message == "EventA" {
        s.log = append(s.log, "Child:event_a")
    } else if __e._message == "EventB" {
        s.log = append(s.log, "Child:event_b_forward")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
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
	fmt.Println("=== Test 08: HSM Forward ===")
	sm := NewHSMForward()

	// event_a should be handled by Child (no forward)
	sm.EventA()
	log := sm.GetLog()
	if !contains(log, "Child:event_a") {
		fmt.Printf("FAIL: Expected 'Child:event_a' in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("After EventA: %v\n", log)

	// event_b should forward to Parent
	sm.EventB()
	log = sm.GetLog()
	if !contains(log, "Child:event_b_forward") {
		fmt.Printf("FAIL: Expected 'Child:event_b_forward' in log, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:event_b") {
		fmt.Printf("FAIL: Expected 'Parent:event_b' in log (forwarded), got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("After EventB (forwarded): %v\n", log)

	fmt.Println("PASS: HSM forward works correctly")
}
