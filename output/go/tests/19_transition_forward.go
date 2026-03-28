
package main

import "fmt"
import "os"

type EventForwardTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type EventForwardTestFrameContext struct {
    _event  EventForwardTestFrameEvent
    _return any
    _data   map[string]any
}

type EventForwardTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *EventForwardTestFrameEvent
    parentCompartment *EventForwardTestCompartment
}

func newEventForwardTestCompartment(state string) *EventForwardTestCompartment {
    return &EventForwardTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *EventForwardTestCompartment) copy() *EventForwardTestCompartment {
    nc := &EventForwardTestCompartment{
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

type EventForwardTest struct {
    _state_stack []*EventForwardTestCompartment
    __compartment *EventForwardTestCompartment
    __next_compartment *EventForwardTestCompartment
    _context_stack []EventForwardTestFrameContext
    log []string
}

func NewEventForwardTest() *EventForwardTest {
    s := &EventForwardTest{}
    s._state_stack = make([]*EventForwardTestCompartment, 0)
    s._context_stack = make([]EventForwardTestFrameContext, 0)
    s.__compartment = newEventForwardTestCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := EventForwardTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := EventForwardTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *EventForwardTest) __kernel(__e *EventForwardTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &EventForwardTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &EventForwardTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &EventForwardTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *EventForwardTest) __router(__e *EventForwardTestFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Working":
        s._state_Working(__e)
    }
}

func (s *EventForwardTest) __transition(next *EventForwardTestCompartment) {
    s.__next_compartment = next
}

func (s *EventForwardTest) Process() {
    __e := EventForwardTestFrameEvent{_message: "Process"}
    __ctx := EventForwardTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *EventForwardTest) GetLog() []string {
    __e := EventForwardTestFrameEvent{_message: "GetLog"}
    __ctx := EventForwardTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *EventForwardTest) _state_Idle(__e *EventForwardTestFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Process" {
        s.log = append(s.log, "idle:process:before")
        __compartment := newEventForwardTestCompartment("Working")
        __compartment.parentCompartment = s.__compartment.copy()
        __compartment.forwardEvent = __e
        s.__transition(__compartment)
        return
        // This should NOT execute because -> => returns after dispatch
        s.log = append(s.log, "idle:process:after")
    }
}

func (s *EventForwardTest) _state_Working(__e *EventForwardTestFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Process" {
        s.log = append(s.log, "working:process")
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
	fmt.Println("=== Test 19: Transition Forward (Go) ===")
	sm := NewEventForwardTest()
	sm.Process()
	log := sm.GetLog()
	fmt.Printf("Log: %v\n", log)

	if !contains(log, "idle:process:before") {
		fmt.Printf("FAIL: Expected 'idle:process:before' in log: %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "working:process") {
		fmt.Printf("FAIL: Expected 'working:process' in log: %v\n", log)
		os.Exit(1)
	}
	if contains(log, "idle:process:after") {
		fmt.Printf("FAIL: Should NOT have 'idle:process:after' in log: %v\n", log)
		os.Exit(1)
	}

	fmt.Println("PASS: Transition forward works correctly")
}
