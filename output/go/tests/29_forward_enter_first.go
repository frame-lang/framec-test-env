
package main

import "fmt"
import "os"

type ForwardEnterFirstFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type ForwardEnterFirstFrameContext struct {
    _event  ForwardEnterFirstFrameEvent
    _return any
    _data   map[string]any
}

type ForwardEnterFirstCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *ForwardEnterFirstFrameEvent
    parentCompartment *ForwardEnterFirstCompartment
}

func newForwardEnterFirstCompartment(state string) *ForwardEnterFirstCompartment {
    return &ForwardEnterFirstCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *ForwardEnterFirstCompartment) copy() *ForwardEnterFirstCompartment {
    nc := &ForwardEnterFirstCompartment{
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

type ForwardEnterFirst struct {
    _state_stack []*ForwardEnterFirstCompartment
    __compartment *ForwardEnterFirstCompartment
    __next_compartment *ForwardEnterFirstCompartment
    _context_stack []ForwardEnterFirstFrameContext
    log []string
}

func NewForwardEnterFirst() *ForwardEnterFirst {
    s := &ForwardEnterFirst{}
    s._state_stack = make([]*ForwardEnterFirstCompartment, 0)
    s._context_stack = make([]ForwardEnterFirstFrameContext, 0)
    s.__compartment = newForwardEnterFirstCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := ForwardEnterFirstFrameEvent{_message: "$>", _parameters: nil}
    __ctx := ForwardEnterFirstFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *ForwardEnterFirst) __kernel(__e *ForwardEnterFirstFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &ForwardEnterFirstFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &ForwardEnterFirstFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &ForwardEnterFirstFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *ForwardEnterFirst) __router(__e *ForwardEnterFirstFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Working":
        s._state_Working(__e)
    }
}

func (s *ForwardEnterFirst) __transition(next *ForwardEnterFirstCompartment) {
    s.__next_compartment = next
}

func (s *ForwardEnterFirst) Process() {
    __e := ForwardEnterFirstFrameEvent{_message: "Process"}
    __ctx := ForwardEnterFirstFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *ForwardEnterFirst) GetCounter() int {
    __e := ForwardEnterFirstFrameEvent{_message: "GetCounter"}
    __ctx := ForwardEnterFirstFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ForwardEnterFirst) GetLog() []string {
    __e := ForwardEnterFirstFrameEvent{_message: "GetLog"}
    __ctx := ForwardEnterFirstFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ForwardEnterFirst) _state_Working(__e *ForwardEnterFirstFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Working" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["counter"]; !ok {
            __sv_comp.stateVars["counter"] = 100
        }
        s.log = append(s.log, "Working:enter")
    } else if __e._message == "GetCounter" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["counter"].(int)
        return
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Process" {
        s.log = append(s.log, fmt.Sprintf("Working:process:counter=%d", __sv_comp.stateVars["counter"].(int)))
        __sv_comp.stateVars["counter"] = __sv_comp.stateVars["counter"].(int) + 1
    }
}

func (s *ForwardEnterFirst) _state_Idle(__e *ForwardEnterFirstFrameEvent) {
    if __e._message == "GetCounter" {
        s._context_stack[len(s._context_stack)-1]._return = -1
        return
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Process" {
        __compartment := newForwardEnterFirstCompartment("Working")
        __compartment.parentCompartment = s.__compartment.copy()
        __compartment.forwardEvent = __e
        s.__transition(__compartment)
        return
    }
}

func indexOf(slice []string, item string) int {
	for i, v := range slice {
		if v == item {
			return i
		}
	}
	return -1
}

func contains(slice []string, item string) bool {
	return indexOf(slice, item) >= 0
}

func main() {
	fmt.Println("=== Test 29: Forward Enter First ===")
	sm := NewForwardEnterFirst()

	if sm.GetCounter() != -1 {
		fmt.Println("FAIL: Expected -1 in Idle")
		os.Exit(1)
	}

	sm.Process()

	counter := sm.GetCounter()
	log := sm.GetLog()
	fmt.Printf("Counter after forward: %d\n", counter)
	fmt.Printf("Log: %v\n", log)

	if !contains(log, "Working:enter") {
		fmt.Printf("FAIL: Expected 'Working:enter' in log: %v\n", log)
		os.Exit(1)
	}

	if !contains(log, "Working:process:counter=100") {
		fmt.Printf("FAIL: Expected 'Working:process:counter=100' in log: %v\n", log)
		os.Exit(1)
	}

	if counter != 101 {
		fmt.Printf("FAIL: Expected counter=101, got %d\n", counter)
		os.Exit(1)
	}

	enterIdx := indexOf(log, "Working:enter")
	processIdx := indexOf(log, "Working:process:counter=100")
	if enterIdx >= processIdx {
		fmt.Printf("FAIL: $> should run before process: %v\n", log)
		os.Exit(1)
	}

	fmt.Println("PASS: Forward sends $> first for non-$> events")
}
