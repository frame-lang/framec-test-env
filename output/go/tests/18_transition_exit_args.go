
package main

import "fmt"
import "os"

type TransitionExitArgsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type TransitionExitArgsFrameContext struct {
    _event  TransitionExitArgsFrameEvent
    _return any
    _data   map[string]any
}

type TransitionExitArgsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *TransitionExitArgsFrameEvent
    parentCompartment *TransitionExitArgsCompartment
}

func newTransitionExitArgsCompartment(state string) *TransitionExitArgsCompartment {
    return &TransitionExitArgsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *TransitionExitArgsCompartment) copy() *TransitionExitArgsCompartment {
    nc := &TransitionExitArgsCompartment{
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

type TransitionExitArgs struct {
    _state_stack []*TransitionExitArgsCompartment
    __compartment *TransitionExitArgsCompartment
    __next_compartment *TransitionExitArgsCompartment
    _context_stack []TransitionExitArgsFrameContext
    log []string
}

func NewTransitionExitArgs() *TransitionExitArgs {
    s := &TransitionExitArgs{}
    s._state_stack = make([]*TransitionExitArgsCompartment, 0)
    s._context_stack = make([]TransitionExitArgsFrameContext, 0)
    s.__compartment = newTransitionExitArgsCompartment("Active")
    s.__next_compartment = nil
    __frame_event := TransitionExitArgsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := TransitionExitArgsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *TransitionExitArgs) __kernel(__e *TransitionExitArgsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &TransitionExitArgsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &TransitionExitArgsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &TransitionExitArgsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *TransitionExitArgs) __router(__e *TransitionExitArgsFrameEvent) {
    switch s.__compartment.state {
    case "Active":
        s._state_Active(__e)
    case "Done":
        s._state_Done(__e)
    }
}

func (s *TransitionExitArgs) __transition(next *TransitionExitArgsCompartment) {
    s.__next_compartment = next
}

func (s *TransitionExitArgs) Leave() {
    __e := TransitionExitArgsFrameEvent{_message: "Leave"}
    __ctx := TransitionExitArgsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TransitionExitArgs) GetLog() []string {
    __e := TransitionExitArgsFrameEvent{_message: "GetLog"}
    __ctx := TransitionExitArgsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *TransitionExitArgs) _state_Done(__e *TransitionExitArgsFrameEvent) {
    if __e._message == "$>" {
        s.log = append(s.log, "enter:done")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    }
}

func (s *TransitionExitArgs) _state_Active(__e *TransitionExitArgsFrameEvent) {
    if __e._message == "<$" {
        reason := s.__compartment.exitArgs["0"].(string)
        _ = reason
        code := s.__compartment.exitArgs["1"].(int)
        _ = code
        s.log = append(s.log, fmt.Sprintf("exit:%s:%d", reason, code))
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Leave" {
        s.log = append(s.log, "leaving")
        s.__compartment.exitArgs["0"] = "cleanup"
        s.__compartment.exitArgs["1"] = 42
        __compartment := newTransitionExitArgsCompartment("Done")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
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
	fmt.Println("=== Test 18: Transition Exit Args ===")
	sm := NewTransitionExitArgs()

	// Initial state is Active
	log := sm.GetLog()
	if len(log) != 0 {
		fmt.Printf("FAIL: Expected empty log, got %v\n", log)
		os.Exit(1)
	}

	// Leave - should call exit handler with args
	sm.Leave()
	log = sm.GetLog()
	if !contains(log, "leaving") {
		fmt.Printf("FAIL: Expected 'leaving' in log, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "exit:cleanup:42") {
		fmt.Printf("FAIL: Expected 'exit:cleanup:42' in log, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "enter:done") {
		fmt.Printf("FAIL: Expected 'enter:done' in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("Log after transition: %v\n", log)

	fmt.Println("PASS: Transition exit args work correctly")
}
