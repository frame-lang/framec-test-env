
package main

import "fmt"
import "os"

type EnterExitFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type EnterExitFrameContext struct {
    _event  EnterExitFrameEvent
    _return any
    _data   map[string]any
}

type EnterExitCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *EnterExitFrameEvent
    parentCompartment *EnterExitCompartment
}

func newEnterExitCompartment(state string) *EnterExitCompartment {
    return &EnterExitCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *EnterExitCompartment) copy() *EnterExitCompartment {
    nc := &EnterExitCompartment{
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

type EnterExit struct {
    _state_stack []*EnterExitCompartment
    __compartment *EnterExitCompartment
    __next_compartment *EnterExitCompartment
    _context_stack []EnterExitFrameContext
    log []string
}

func NewEnterExit() *EnterExit {
    s := &EnterExit{}
    s._state_stack = make([]*EnterExitCompartment, 0)
    s._context_stack = make([]EnterExitFrameContext, 0)
    s.__compartment = newEnterExitCompartment("Off")
    s.__next_compartment = nil
    __frame_event := EnterExitFrameEvent{_message: "$>", _parameters: nil}
    __ctx := EnterExitFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *EnterExit) __kernel(__e *EnterExitFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &EnterExitFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &EnterExitFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &EnterExitFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *EnterExit) __router(__e *EnterExitFrameEvent) {
    switch s.__compartment.state {
    case "Off":
        s._state_Off(__e)
    case "On":
        s._state_On(__e)
    }
}

func (s *EnterExit) __transition(next *EnterExitCompartment) {
    s.__next_compartment = next
}

func (s *EnterExit) Toggle() {
    __e := EnterExitFrameEvent{_message: "Toggle"}
    __ctx := EnterExitFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *EnterExit) GetLog() []string {
    __e := EnterExitFrameEvent{_message: "GetLog"}
    __ctx := EnterExitFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *EnterExit) _state_Off(__e *EnterExitFrameEvent) {
    if __e._message == "<$" {
        s.log = append(s.log, "exit:Off")
        fmt.Println("Exiting Off state")
    } else if __e._message == "$>" {
        s.log = append(s.log, "enter:Off")
        fmt.Println("Entered Off state")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Toggle" {
        __compartment := newEnterExitCompartment("On")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *EnterExit) _state_On(__e *EnterExitFrameEvent) {
    if __e._message == "<$" {
        s.log = append(s.log, "exit:On")
        fmt.Println("Exiting On state")
    } else if __e._message == "$>" {
        s.log = append(s.log, "enter:On")
        fmt.Println("Entered On state")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Toggle" {
        __compartment := newEnterExitCompartment("Off")
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

func countOccurrences(slice []string, item string) int {
	count := 0
	for _, v := range slice {
		if v == item {
			count++
		}
	}
	return count
}

func main() {
	fmt.Println("=== Test 05: Enter/Exit Handlers ===")
	sm := NewEnterExit()

	// Initial enter should have been called
	log := sm.GetLog()
	if !contains(log, "enter:Off") {
		fmt.Printf("FAIL: Expected 'enter:Off' in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("After construction: %v\n", log)

	// Toggle to On - should exit Off, enter On
	sm.Toggle()
	log = sm.GetLog()
	if !contains(log, "exit:Off") {
		fmt.Printf("FAIL: Expected 'exit:Off' in log, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "enter:On") {
		fmt.Printf("FAIL: Expected 'enter:On' in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("After toggle to On: %v\n", log)

	// Toggle back to Off - should exit On, enter Off
	sm.Toggle()
	log = sm.GetLog()
	enterOffCount := countOccurrences(log, "enter:Off")
	if enterOffCount != 2 {
		fmt.Printf("FAIL: Expected 2 'enter:Off' entries, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "exit:On") {
		fmt.Printf("FAIL: Expected 'exit:On' in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("After toggle to Off: %v\n", log)

	fmt.Println("PASS: Enter/Exit handlers work correctly")
}
