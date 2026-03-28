
package main

import "fmt"
import "os"

type HSMEnterChildOnlyFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMEnterChildOnlyFrameContext struct {
    _event  HSMEnterChildOnlyFrameEvent
    _return any
    _data   map[string]any
}

type HSMEnterChildOnlyCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMEnterChildOnlyFrameEvent
    parentCompartment *HSMEnterChildOnlyCompartment
}

func newHSMEnterChildOnlyCompartment(state string) *HSMEnterChildOnlyCompartment {
    return &HSMEnterChildOnlyCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMEnterChildOnlyCompartment) copy() *HSMEnterChildOnlyCompartment {
    nc := &HSMEnterChildOnlyCompartment{
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

type HSMEnterChildOnly struct {
    _state_stack []*HSMEnterChildOnlyCompartment
    __compartment *HSMEnterChildOnlyCompartment
    __next_compartment *HSMEnterChildOnlyCompartment
    _context_stack []HSMEnterChildOnlyFrameContext
    log []string
}

func NewHSMEnterChildOnly() *HSMEnterChildOnly {
    s := &HSMEnterChildOnly{}
    s._state_stack = make([]*HSMEnterChildOnlyCompartment, 0)
    s._context_stack = make([]HSMEnterChildOnlyFrameContext, 0)
    s.__compartment = newHSMEnterChildOnlyCompartment("Start")
    s.__next_compartment = nil
    __frame_event := HSMEnterChildOnlyFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMEnterChildOnlyFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMEnterChildOnly) __kernel(__e *HSMEnterChildOnlyFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMEnterChildOnlyFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMEnterChildOnlyFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMEnterChildOnlyFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMEnterChildOnly) __router(__e *HSMEnterChildOnlyFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMEnterChildOnly) __transition(next *HSMEnterChildOnlyCompartment) {
    s.__next_compartment = next
}

func (s *HSMEnterChildOnly) GoToChild() {
    __e := HSMEnterChildOnlyFrameEvent{_message: "GoToChild"}
    __ctx := HSMEnterChildOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterChildOnly) ForwardAction() {
    __e := HSMEnterChildOnlyFrameEvent{_message: "ForwardAction"}
    __ctx := HSMEnterChildOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterChildOnly) GetLog() []string {
    __e := HSMEnterChildOnlyFrameEvent{_message: "GetLog"}
    __ctx := HSMEnterChildOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterChildOnly) GetState() string {
    __e := HSMEnterChildOnlyFrameEvent{_message: "GetState"}
    __ctx := HSMEnterChildOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterChildOnly) _state_Parent(__e *HSMEnterChildOnlyFrameEvent) {
    if __e._message == "ForwardAction" {
        s.log = append(s.log, "Parent:forward_action")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    }
}

func (s *HSMEnterChildOnly) _state_Start(__e *HSMEnterChildOnlyFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Start"
        return
    } else if __e._message == "GoToChild" {
        __compartment := newHSMEnterChildOnlyCompartment("Child")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMEnterChildOnly) _state_Child(__e *HSMEnterChildOnlyFrameEvent) {
    if __e._message == "$>" {
        s.log = append(s.log, "Child:enter")
    } else if __e._message == "ForwardAction" {
        s.log = append(s.log, "Child:forward")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Child"
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
	fmt.Println("=== Test 45: HSM Enter in Child Only ===")
	sm := NewHSMEnterChildOnly()

	// Start state has no enter
	if sm.GetState() != "Start" {
		fmt.Printf("FAIL: Expected Start, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC2.1.0: Initial state is Start - PASS")

	// TC2.1.1: Child enter handler fires on entry
	sm.GoToChild()
	log := sm.GetLog()
	if !contains(log, "Child:enter") {
		fmt.Printf("FAIL: Expected Child:enter, got %v\n", log)
		os.Exit(1)
	}
	if sm.GetState() != "Child" {
		fmt.Printf("FAIL: Expected Child, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC2.1.1: Child enter handler fires - PASS")

	// TC2.1.2: No error when parent lacks enter (verified by compilation/execution)
	fmt.Println("TC2.1.2: No error when parent lacks enter - PASS")

	// TC2.1.3: Forward to parent works without parent having enter
	sm.ForwardAction()
	log = sm.GetLog()
	if !contains(log, "Child:forward") {
		fmt.Printf("FAIL: Expected Child:forward, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:forward_action") {
		fmt.Printf("FAIL: Expected Parent handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.1.3: Forward works without parent enter - PASS")

	fmt.Println("PASS: HSM enter in child only works correctly")
}
