
package main

import "fmt"
import "os"

type TransitionEnterArgsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type TransitionEnterArgsFrameContext struct {
    _event  TransitionEnterArgsFrameEvent
    _return any
    _data   map[string]any
}

type TransitionEnterArgsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *TransitionEnterArgsFrameEvent
    parentCompartment *TransitionEnterArgsCompartment
}

func newTransitionEnterArgsCompartment(state string) *TransitionEnterArgsCompartment {
    return &TransitionEnterArgsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *TransitionEnterArgsCompartment) copy() *TransitionEnterArgsCompartment {
    nc := &TransitionEnterArgsCompartment{
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

type TransitionEnterArgs struct {
    _state_stack []*TransitionEnterArgsCompartment
    __compartment *TransitionEnterArgsCompartment
    __next_compartment *TransitionEnterArgsCompartment
    _context_stack []TransitionEnterArgsFrameContext
    log []string
}

func NewTransitionEnterArgs() *TransitionEnterArgs {
    s := &TransitionEnterArgs{}
    s._state_stack = make([]*TransitionEnterArgsCompartment, 0)
    s._context_stack = make([]TransitionEnterArgsFrameContext, 0)
    s.__compartment = newTransitionEnterArgsCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := TransitionEnterArgsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := TransitionEnterArgsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *TransitionEnterArgs) __kernel(__e *TransitionEnterArgsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &TransitionEnterArgsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &TransitionEnterArgsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &TransitionEnterArgsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *TransitionEnterArgs) __router(__e *TransitionEnterArgsFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Active":
        s._state_Active(__e)
    }
}

func (s *TransitionEnterArgs) __transition(next *TransitionEnterArgsCompartment) {
    s.__next_compartment = next
}

func (s *TransitionEnterArgs) Start() {
    __e := TransitionEnterArgsFrameEvent{_message: "Start"}
    __ctx := TransitionEnterArgsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TransitionEnterArgs) GetLog() []string {
    __e := TransitionEnterArgsFrameEvent{_message: "GetLog"}
    __ctx := TransitionEnterArgsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *TransitionEnterArgs) _state_Idle(__e *TransitionEnterArgsFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Start" {
        s.log = append(s.log, "idle:start")
        __compartment := newTransitionEnterArgsCompartment("Active")
        __compartment.parentCompartment = s.__compartment.copy()
        __compartment.enterArgs["0"] = "from_idle"
        __compartment.enterArgs["1"] = 42
        s.__transition(__compartment)
        return
    }
}

func (s *TransitionEnterArgs) _state_Active(__e *TransitionEnterArgsFrameEvent) {
    if __e._message == "$>" {
        source := s.__compartment.enterArgs["0"].(string)
        _ = source
        value := s.__compartment.enterArgs["1"].(int)
        _ = value
        s.log = append(s.log, fmt.Sprintf("active:enter:%s:%d", source, value))
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Start" {
        s.log = append(s.log, "active:start")
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
	fmt.Println("=== Test 17: Transition Enter Args ===")
	sm := NewTransitionEnterArgs()

	// Initial state is Idle
	log := sm.GetLog()
	if len(log) != 0 {
		fmt.Printf("FAIL: Expected empty log, got %v\n", log)
		os.Exit(1)
	}

	// Transition to Active with args
	sm.Start()
	log = sm.GetLog()
	if !contains(log, "idle:start") {
		fmt.Printf("FAIL: Expected 'idle:start' in log, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "active:enter:from_idle:42") {
		fmt.Printf("FAIL: Expected 'active:enter:from_idle:42' in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("Log after transition: %v\n", log)

	fmt.Println("PASS: Transition enter args work correctly")
}
