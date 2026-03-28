
package main

import (
	"fmt"
	"os"
	"strings"
)

type ActionsTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type ActionsTestFrameContext struct {
    _event  ActionsTestFrameEvent
    _return any
    _data   map[string]any
}

type ActionsTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *ActionsTestFrameEvent
    parentCompartment *ActionsTestCompartment
}

func newActionsTestCompartment(state string) *ActionsTestCompartment {
    return &ActionsTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *ActionsTestCompartment) copy() *ActionsTestCompartment {
    nc := &ActionsTestCompartment{
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

type ActionsTest struct {
    _state_stack []*ActionsTestCompartment
    __compartment *ActionsTestCompartment
    __next_compartment *ActionsTestCompartment
    _context_stack []ActionsTestFrameContext
    log string
}

func NewActionsTest() *ActionsTest {
    s := &ActionsTest{}
    s._state_stack = make([]*ActionsTestCompartment, 0)
    s._context_stack = make([]ActionsTestFrameContext, 0)
    s.__compartment = newActionsTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := ActionsTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := ActionsTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *ActionsTest) __kernel(__e *ActionsTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &ActionsTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &ActionsTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &ActionsTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *ActionsTest) __router(__e *ActionsTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *ActionsTest) __transition(next *ActionsTestCompartment) {
    s.__next_compartment = next
}

func (s *ActionsTest) Process(value int) int {
    __params := map[string]any{
        "value": value,
    }
    __e := ActionsTestFrameEvent{_message: "Process", _parameters: __params}
    __ctx := ActionsTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ActionsTest) GetLog() string {
    __e := ActionsTestFrameEvent{_message: "GetLog"}
    __ctx := ActionsTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ActionsTest) _state_Ready(__e *ActionsTestFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "Process" {
        value := __e._parameters["value"].(int)
        _ = value
        s.__log_event("start")
        s.__validate_positive(value)
        s.__log_event("valid")
        result := value * 2
        s.__log_event("done")
        s._context_stack[len(s._context_stack)-1]._return = result
        return
    }
}

func (s *ActionsTest) __log_event(msg string) {
                s.log = s.log + msg + ";"
}

func (s *ActionsTest) __validate_positive(n int) {
                if n < 0 {
                    panic(fmt.Sprintf("Value must be positive: %d", n))
                }
}

func main() {
	fmt.Println("=== Test 21: Actions Basic (Go) ===")
	sm := NewActionsTest()

	// Test 1: Actions are called correctly
	result := sm.Process(5)
	if result != 10 {
		fmt.Printf("FAIL: Expected 10, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("1. Process(5) = %d\n", result)

	// Test 2: Log shows action calls
	log := sm.GetLog()
	if !strings.Contains(log, "start") {
		fmt.Printf("FAIL: Missing 'start' in log: %s\n", log)
		os.Exit(1)
	}
	if !strings.Contains(log, "valid") {
		fmt.Printf("FAIL: Missing 'valid' in log: %s\n", log)
		os.Exit(1)
	}
	if !strings.Contains(log, "done") {
		fmt.Printf("FAIL: Missing 'done' in log: %s\n", log)
		os.Exit(1)
	}
	fmt.Printf("2. Log: %s\n", log)

	// Test 3: Action with validation
	func() {
		defer func() {
			r := recover()
			if r == nil {
				fmt.Println("FAIL: Should have panicked")
				os.Exit(1)
			}
			msg := fmt.Sprintf("%v", r)
			if strings.Contains(msg, "positive") {
				fmt.Printf("3. Validation caught: %s\n", msg)
			} else {
				panic(r)
			}
		}()
		sm.Process(-1)
	}()

	fmt.Println("PASS: Actions basic works correctly")
}
