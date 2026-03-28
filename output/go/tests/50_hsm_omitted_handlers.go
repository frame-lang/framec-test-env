
package main

import "fmt"
import "os"

type HSMOmittedHandlersFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMOmittedHandlersFrameContext struct {
    _event  HSMOmittedHandlersFrameEvent
    _return any
    _data   map[string]any
}

type HSMOmittedHandlersCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMOmittedHandlersFrameEvent
    parentCompartment *HSMOmittedHandlersCompartment
}

func newHSMOmittedHandlersCompartment(state string) *HSMOmittedHandlersCompartment {
    return &HSMOmittedHandlersCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMOmittedHandlersCompartment) copy() *HSMOmittedHandlersCompartment {
    nc := &HSMOmittedHandlersCompartment{
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

type HSMOmittedHandlers struct {
    _state_stack []*HSMOmittedHandlersCompartment
    __compartment *HSMOmittedHandlersCompartment
    __next_compartment *HSMOmittedHandlersCompartment
    _context_stack []HSMOmittedHandlersFrameContext
    log []string
}

func NewHSMOmittedHandlers() *HSMOmittedHandlers {
    s := &HSMOmittedHandlers{}
    s._state_stack = make([]*HSMOmittedHandlersCompartment, 0)
    s._context_stack = make([]HSMOmittedHandlersFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMOmittedHandlersCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMOmittedHandlersCompartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMOmittedHandlersFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMOmittedHandlersFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMOmittedHandlers) __kernel(__e *HSMOmittedHandlersFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMOmittedHandlersFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMOmittedHandlersFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMOmittedHandlersFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMOmittedHandlers) __router(__e *HSMOmittedHandlersFrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMOmittedHandlers) __transition(next *HSMOmittedHandlersCompartment) {
    s.__next_compartment = next
}

func (s *HSMOmittedHandlers) HandledByChild() {
    __e := HSMOmittedHandlersFrameEvent{_message: "HandledByChild"}
    __ctx := HSMOmittedHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMOmittedHandlers) ForwardedExplicitly() {
    __e := HSMOmittedHandlersFrameEvent{_message: "ForwardedExplicitly"}
    __ctx := HSMOmittedHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMOmittedHandlers) UnhandledNoForward() {
    __e := HSMOmittedHandlersFrameEvent{_message: "UnhandledNoForward"}
    __ctx := HSMOmittedHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMOmittedHandlers) GetLog() []string {
    __e := HSMOmittedHandlersFrameEvent{_message: "GetLog"}
    __ctx := HSMOmittedHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMOmittedHandlers) GetState() string {
    __e := HSMOmittedHandlersFrameEvent{_message: "GetState"}
    __ctx := HSMOmittedHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMOmittedHandlers) _state_Parent(__e *HSMOmittedHandlersFrameEvent) {
    if __e._message == "ForwardedExplicitly" {
        s.log = append(s.log, "Parent:forwarded_explicitly")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    } else if __e._message == "HandledByChild" {
        s.log = append(s.log, "Parent:handled_by_child")
    } else if __e._message == "UnhandledNoForward" {
        s.log = append(s.log, "Parent:unhandled_no_forward")
    }
}

func (s *HSMOmittedHandlers) _state_Child(__e *HSMOmittedHandlersFrameEvent) {
    if __e._message == "ForwardedExplicitly" {
        s.log = append(s.log, "Child:before_forward")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Child"
        return
    } else if __e._message == "HandledByChild" {
        s.log = append(s.log, "Child:handled_by_child")
    }
}

type HSMDefaultForward2FrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMDefaultForward2FrameContext struct {
    _event  HSMDefaultForward2FrameEvent
    _return any
    _data   map[string]any
}

type HSMDefaultForward2Compartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMDefaultForward2FrameEvent
    parentCompartment *HSMDefaultForward2Compartment
}

func newHSMDefaultForward2Compartment(state string) *HSMDefaultForward2Compartment {
    return &HSMDefaultForward2Compartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMDefaultForward2Compartment) copy() *HSMDefaultForward2Compartment {
    nc := &HSMDefaultForward2Compartment{
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

type HSMDefaultForward2 struct {
    _state_stack []*HSMDefaultForward2Compartment
    __compartment *HSMDefaultForward2Compartment
    __next_compartment *HSMDefaultForward2Compartment
    _context_stack []HSMDefaultForward2FrameContext
    log []string
}

func NewHSMDefaultForward2() *HSMDefaultForward2 {
    s := &HSMDefaultForward2{}
    s._state_stack = make([]*HSMDefaultForward2Compartment, 0)
    s._context_stack = make([]HSMDefaultForward2FrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMDefaultForward2Compartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMDefaultForward2Compartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMDefaultForward2FrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMDefaultForward2FrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMDefaultForward2) __kernel(__e *HSMDefaultForward2FrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMDefaultForward2FrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMDefaultForward2FrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMDefaultForward2FrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMDefaultForward2) __router(__e *HSMDefaultForward2FrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMDefaultForward2) __transition(next *HSMDefaultForward2Compartment) {
    s.__next_compartment = next
}

func (s *HSMDefaultForward2) ChildHandled() {
    __e := HSMDefaultForward2FrameEvent{_message: "ChildHandled"}
    __ctx := HSMDefaultForward2FrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMDefaultForward2) ParentHandled() {
    __e := HSMDefaultForward2FrameEvent{_message: "ParentHandled"}
    __ctx := HSMDefaultForward2FrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMDefaultForward2) BothRespond() {
    __e := HSMDefaultForward2FrameEvent{_message: "BothRespond"}
    __ctx := HSMDefaultForward2FrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMDefaultForward2) GetLog() []string {
    __e := HSMDefaultForward2FrameEvent{_message: "GetLog"}
    __ctx := HSMDefaultForward2FrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMDefaultForward2) _state_Child(__e *HSMDefaultForward2FrameEvent) {
    if __e._message == "ChildHandled" {
        s.log = append(s.log, "Child:child_handled")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else {
        s._state_Parent(__e)
    }
}

func (s *HSMDefaultForward2) _state_Parent(__e *HSMDefaultForward2FrameEvent) {
    if __e._message == "BothRespond" {
        s.log = append(s.log, "Parent:both_respond")
    } else if __e._message == "ChildHandled" {
        s.log = append(s.log, "Parent:child_handled")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "ParentHandled" {
        s.log = append(s.log, "Parent:parent_handled")
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
	fmt.Println("=== Test 50: HSM Omitted Handlers ===")

	// Part 1: Explicit forwarding vs no forwarding
	s1 := NewHSMOmittedHandlers()

	// TC2.6.1: Event handled by child only
	s1.HandledByChild()
	log := s1.GetLog()
	if !contains(log, "Child:handled_by_child") {
		fmt.Printf("FAIL: Expected Child handler, got %v\n", log)
		os.Exit(1)
	}
	if contains(log, "Parent:handled_by_child") {
		fmt.Printf("FAIL: Parent should NOT be called, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.6.1: Handled by child, not forwarded - PASS")

	// TC2.6.2: Event explicitly forwarded to parent
	s1.ForwardedExplicitly()
	log = s1.GetLog()
	if !contains(log, "Child:before_forward") {
		fmt.Printf("FAIL: Expected Child forward, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:forwarded_explicitly") {
		fmt.Printf("FAIL: Expected Parent handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.6.2: Explicitly forwarded to parent - PASS")

	// TC2.6.3: Unhandled event with no forward - silently ignored
	s1.UnhandledNoForward()
	log = s1.GetLog()
	if contains(log, "Parent:unhandled_no_forward") {
		fmt.Printf("FAIL: Unhandled should be ignored, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.6.3: Unhandled (no forward) is silently ignored - PASS")

	// Part 2: State-level default forward
	s2 := NewHSMDefaultForward2()

	// TC2.6.4: Event handled by child (no forward despite => $^)
	s2.ChildHandled()
	log = s2.GetLog()
	if !contains(log, "Child:child_handled") {
		fmt.Printf("FAIL: Expected Child handler, got %v\n", log)
		os.Exit(1)
	}
	if contains(log, "Parent:child_handled") {
		fmt.Printf("FAIL: Handled by child, not forwarded, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.6.4: Child handles, not forwarded - PASS")

	// TC2.6.5: Unhandled event forwarded via => $^
	s2.ParentHandled()
	log = s2.GetLog()
	if !contains(log, "Parent:parent_handled") {
		fmt.Printf("FAIL: Expected Parent handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.6.5: Unhandled forwarded via state-level => $^ - PASS")

	// TC2.6.6: Another unhandled event forwarded
	s2.BothRespond()
	log = s2.GetLog()
	if !contains(log, "Parent:both_respond") {
		fmt.Printf("FAIL: Expected Parent handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.6.6: Default forward works for multiple events - PASS")

	fmt.Println("PASS: HSM omitted handlers work correctly")
}
