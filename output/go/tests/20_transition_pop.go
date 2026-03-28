
package main

import "fmt"
import "os"

type TransitionPopTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type TransitionPopTestFrameContext struct {
    _event  TransitionPopTestFrameEvent
    _return any
    _data   map[string]any
}

type TransitionPopTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *TransitionPopTestFrameEvent
    parentCompartment *TransitionPopTestCompartment
}

func newTransitionPopTestCompartment(state string) *TransitionPopTestCompartment {
    return &TransitionPopTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *TransitionPopTestCompartment) copy() *TransitionPopTestCompartment {
    nc := &TransitionPopTestCompartment{
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

type TransitionPopTest struct {
    _state_stack []*TransitionPopTestCompartment
    __compartment *TransitionPopTestCompartment
    __next_compartment *TransitionPopTestCompartment
    _context_stack []TransitionPopTestFrameContext
    log []string
}

func NewTransitionPopTest() *TransitionPopTest {
    s := &TransitionPopTest{}
    s._state_stack = make([]*TransitionPopTestCompartment, 0)
    s._context_stack = make([]TransitionPopTestFrameContext, 0)
    s.__compartment = newTransitionPopTestCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := TransitionPopTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := TransitionPopTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *TransitionPopTest) __kernel(__e *TransitionPopTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &TransitionPopTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &TransitionPopTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &TransitionPopTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *TransitionPopTest) __router(__e *TransitionPopTestFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Working":
        s._state_Working(__e)
    }
}

func (s *TransitionPopTest) __transition(next *TransitionPopTestCompartment) {
    s.__next_compartment = next
}

func (s *TransitionPopTest) Start() {
    __e := TransitionPopTestFrameEvent{_message: "Start"}
    __ctx := TransitionPopTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TransitionPopTest) Process() {
    __e := TransitionPopTestFrameEvent{_message: "Process"}
    __ctx := TransitionPopTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TransitionPopTest) GetState() string {
    __e := TransitionPopTestFrameEvent{_message: "GetState"}
    __ctx := TransitionPopTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *TransitionPopTest) GetLog() []string {
    __e := TransitionPopTestFrameEvent{_message: "GetLog"}
    __ctx := TransitionPopTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *TransitionPopTest) _state_Working(__e *TransitionPopTestFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Working"
        return
    } else if __e._message == "Process" {
        s.log = append(s.log, "working:process:before_pop")
        __popped := s._state_stack[len(s._state_stack)-1]
        s._state_stack = s._state_stack[:len(s._state_stack)-1]
        s.__transition(__popped)
        return
        // This should NOT execute because pop transitions away
        s.log = append(s.log, "working:process:after_pop")
    }
}

func (s *TransitionPopTest) _state_Idle(__e *TransitionPopTestFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Idle"
        return
    } else if __e._message == "Process" {
        s.log = append(s.log, "idle:process")
    } else if __e._message == "Start" {
        s.log = append(s.log, "idle:start:push")
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newTransitionPopTestCompartment("Working")
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
	fmt.Println("=== Test 20: Transition Pop (Go) ===")
	sm := NewTransitionPopTest()

	// Initial state should be Idle
	if sm.GetState() != "Idle" {
		fmt.Printf("FAIL: Expected 'Idle', got '%s'\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Printf("Initial state: %s\n", sm.GetState())

	// start() pushes Idle, transitions to Working
	sm.Start()
	if sm.GetState() != "Working" {
		fmt.Printf("FAIL: Expected 'Working', got '%s'\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Printf("After Start(): %s\n", sm.GetState())

	// process() in Working does pop transition back to Idle
	sm.Process()
	if sm.GetState() != "Idle" {
		fmt.Printf("FAIL: Expected 'Idle' after pop, got '%s'\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Printf("After Process() with pop: %s\n", sm.GetState())

	log := sm.GetLog()
	fmt.Printf("Log: %v\n", log)

	// Verify log contents
	if !contains(log, "idle:start:push") {
		fmt.Println("FAIL: Expected 'idle:start:push' in log")
		os.Exit(1)
	}
	if !contains(log, "working:process:before_pop") {
		fmt.Println("FAIL: Expected 'working:process:before_pop' in log")
		os.Exit(1)
	}
	if contains(log, "working:process:after_pop") {
		fmt.Println("FAIL: Should NOT have 'working:process:after_pop' in log")
		os.Exit(1)
	}

	fmt.Println("PASS: Transition pop works correctly")
}
