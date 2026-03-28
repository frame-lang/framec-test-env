
package main

import "fmt"
import "os"

type ReturnInitTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type ReturnInitTestFrameContext struct {
    _event  ReturnInitTestFrameEvent
    _return any
    _data   map[string]any
}

type ReturnInitTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *ReturnInitTestFrameEvent
    parentCompartment *ReturnInitTestCompartment
}

func newReturnInitTestCompartment(state string) *ReturnInitTestCompartment {
    return &ReturnInitTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *ReturnInitTestCompartment) copy() *ReturnInitTestCompartment {
    nc := &ReturnInitTestCompartment{
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

type ReturnInitTest struct {
    _state_stack []*ReturnInitTestCompartment
    __compartment *ReturnInitTestCompartment
    __next_compartment *ReturnInitTestCompartment
    _context_stack []ReturnInitTestFrameContext
}

func NewReturnInitTest() *ReturnInitTest {
    s := &ReturnInitTest{}
    s._state_stack = make([]*ReturnInitTestCompartment, 0)
    s._context_stack = make([]ReturnInitTestFrameContext, 0)
    s.__compartment = newReturnInitTestCompartment("Start")
    s.__next_compartment = nil
    __frame_event := ReturnInitTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := ReturnInitTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *ReturnInitTest) __kernel(__e *ReturnInitTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &ReturnInitTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &ReturnInitTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &ReturnInitTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *ReturnInitTest) __router(__e *ReturnInitTestFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "Active":
        s._state_Active(__e)
    }
}

func (s *ReturnInitTest) __transition(next *ReturnInitTestCompartment) {
    s.__next_compartment = next
}

func (s *ReturnInitTest) GetStatus() string {
    __e := ReturnInitTestFrameEvent{_message: "GetStatus"}
    __ctx := ReturnInitTestFrameContext{_event: __e, _return: "unknown", _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ReturnInitTest) GetCount() int {
    __e := ReturnInitTestFrameEvent{_message: "GetCount"}
    __ctx := ReturnInitTestFrameContext{_event: __e, _return: 0, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ReturnInitTest) GetFlag() bool {
    __e := ReturnInitTestFrameEvent{_message: "GetFlag"}
    __ctx := ReturnInitTestFrameContext{_event: __e, _return: false, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ReturnInitTest) Trigger() {
    __e := ReturnInitTestFrameEvent{_message: "Trigger"}
    __ctx := ReturnInitTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *ReturnInitTest) _state_Active(__e *ReturnInitTestFrameEvent) {
    if __e._message == "$>" {
        // Active state enter (no-op)
    } else if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = 42
    } else if __e._message == "GetFlag" {
        s._context_stack[len(s._context_stack)-1]._return = true
    } else if __e._message == "GetStatus" {
        s._context_stack[len(s._context_stack)-1]._return = "active"
    } else if __e._message == "Trigger" {
        __compartment := newReturnInitTestCompartment("Start")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *ReturnInitTest) _state_Start(__e *ReturnInitTestFrameEvent) {
    if __e._message == "$>" {
        // Start state enter (no-op)
    } else if __e._message == "GetCount" {
        // Do not set return - should use default 0
    } else if __e._message == "GetFlag" {
        // Do not set return - should use default false
    } else if __e._message == "GetStatus" {
        // Do not set return - should use default "unknown"
    } else if __e._message == "Trigger" {
        __compartment := newReturnInitTestCompartment("Active")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..6")

	sm := NewReturnInitTest()

	// Test 1: Default string return
	if sm.GetStatus() == "unknown" {
		fmt.Println("ok 1 - default string return is 'unknown'")
	} else {
		fmt.Printf("not ok 1 - default string return is 'unknown' # got %s\n", sm.GetStatus())
		os.Exit(1)
	}

	// Test 2: Default int return
	if sm.GetCount() == 0 {
		fmt.Println("ok 2 - default int return is 0")
	} else {
		fmt.Printf("not ok 2 - default int return is 0 # got %d\n", sm.GetCount())
		os.Exit(1)
	}

	// Test 3: Default bool return
	if sm.GetFlag() == false {
		fmt.Println("ok 3 - default bool return is false")
	} else {
		fmt.Printf("not ok 3 - default bool return is false # got %v\n", sm.GetFlag())
		os.Exit(1)
	}

	// Transition to Active state
	sm.Trigger()

	// Test 4: Explicit string return overrides default
	if sm.GetStatus() == "active" {
		fmt.Println("ok 4 - explicit return overrides default string")
	} else {
		fmt.Printf("not ok 4 - explicit return overrides default string # got %s\n", sm.GetStatus())
		os.Exit(1)
	}

	// Test 5: Explicit int return overrides default
	if sm.GetCount() == 42 {
		fmt.Println("ok 5 - explicit return overrides default int")
	} else {
		fmt.Printf("not ok 5 - explicit return overrides default int # got %d\n", sm.GetCount())
		os.Exit(1)
	}

	// Test 6: Explicit bool return overrides default
	if sm.GetFlag() == true {
		fmt.Println("ok 6 - explicit return overrides default bool")
	} else {
		fmt.Printf("not ok 6 - explicit return overrides default bool # got %v\n", sm.GetFlag())
		os.Exit(1)
	}

	fmt.Println("# PASS - return_init provides default return values")
}
