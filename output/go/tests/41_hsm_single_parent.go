
package main

import "fmt"
import "os"

type HSMSingleParentFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMSingleParentFrameContext struct {
    _event  HSMSingleParentFrameEvent
    _return any
    _data   map[string]any
}

type HSMSingleParentCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMSingleParentFrameEvent
    parentCompartment *HSMSingleParentCompartment
}

func newHSMSingleParentCompartment(state string) *HSMSingleParentCompartment {
    return &HSMSingleParentCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMSingleParentCompartment) copy() *HSMSingleParentCompartment {
    nc := &HSMSingleParentCompartment{
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

type HSMSingleParent struct {
    _state_stack []*HSMSingleParentCompartment
    __compartment *HSMSingleParentCompartment
    __next_compartment *HSMSingleParentCompartment
    _context_stack []HSMSingleParentFrameContext
    log []string
}

func NewHSMSingleParent() *HSMSingleParent {
    s := &HSMSingleParent{}
    s._state_stack = make([]*HSMSingleParentCompartment, 0)
    s._context_stack = make([]HSMSingleParentFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMSingleParentCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMSingleParentCompartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMSingleParentFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMSingleParentFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMSingleParent) __kernel(__e *HSMSingleParentFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMSingleParentFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMSingleParentFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMSingleParentFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMSingleParent) __router(__e *HSMSingleParentFrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMSingleParent) __transition(next *HSMSingleParentCompartment) {
    s.__next_compartment = next
}

func (s *HSMSingleParent) ChildOnly() {
    __e := HSMSingleParentFrameEvent{_message: "ChildOnly"}
    __ctx := HSMSingleParentFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMSingleParent) ForwardToParent() {
    __e := HSMSingleParentFrameEvent{_message: "ForwardToParent"}
    __ctx := HSMSingleParentFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMSingleParent) GetLog() []string {
    __e := HSMSingleParentFrameEvent{_message: "GetLog"}
    __ctx := HSMSingleParentFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMSingleParent) GetState() string {
    __e := HSMSingleParentFrameEvent{_message: "GetState"}
    __ctx := HSMSingleParentFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMSingleParent) _state_Parent(__e *HSMSingleParentFrameEvent) {
    if __e._message == "ForwardToParent" {
        s.log = append(s.log, "Parent:forward_to_parent")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    }
}

func (s *HSMSingleParent) _state_Child(__e *HSMSingleParentFrameEvent) {
    if __e._message == "ChildOnly" {
        s.log = append(s.log, "Child:child_only")
    } else if __e._message == "ForwardToParent" {
        s.log = append(s.log, "Child:before_forward")
        s._state_Parent(__e)
        s.log = append(s.log, "Child:after_forward")
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

func countOccurrences(slice []string, item string) int {
	count := 0
	for _, v := range slice {
		if v == item {
			count++
		}
	}
	return count
}

func indexOf(slice []string, item string) int {
	for i, v := range slice {
		if v == item {
			return i
		}
	}
	return -1
}

func main() {
	fmt.Println("=== Test 41: HSM Single Parent ===")
	sm := NewHSMSingleParent()

	// TC1.1.1: Child declares parent with `=> $Parent` syntax (verified by compilation)
	fmt.Println("TC1.1.1: Child-Parent relationship compiles - PASS")

	// TC1.1.2: Child can forward events to parent
	sm.ForwardToParent()
	log := sm.GetLog()
	if !contains(log, "Child:before_forward") {
		fmt.Printf("FAIL: Expected Child:before_forward in log, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:forward_to_parent") {
		fmt.Printf("FAIL: Expected Parent:forward_to_parent in log, got %v\n", log)
		os.Exit(1)
	}
	fmt.Printf("TC1.1.2: Child forwards to parent - PASS (log: %v)\n", log)

	// TC1.1.3: Child remains the current state (no transition occurs on forward)
	state := sm.GetState()
	if state != "Child" {
		fmt.Printf("FAIL: Expected state 'Child', got '%s'\n", state)
		os.Exit(1)
	}
	fmt.Println("TC1.1.3: Child remains current state after forward - PASS")

	// TC1.1.4: Parent handler executes and returns control
	if !contains(log, "Child:after_forward") {
		fmt.Printf("FAIL: Expected Child:after_forward in log (after parent), got %v\n", log)
		os.Exit(1)
	}
	idxParent := indexOf(log, "Parent:forward_to_parent")
	idxAfter := indexOf(log, "Child:after_forward")
	if idxAfter <= idxParent {
		fmt.Println("FAIL: Expected Child:after_forward after Parent handler")
		os.Exit(1)
	}
	fmt.Println("TC1.1.4: Parent executes and returns control - PASS")

	// TC1.1.5: Child-only event not forwarded
	sm.ChildOnly()
	log = sm.GetLog()
	count := countOccurrences(log, "Child:child_only")
	if count != 1 {
		fmt.Printf("FAIL: Expected exactly 1 Child:child_only, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.1.5: Child-only event handled locally - PASS")

	fmt.Println("PASS: HSM single parent relationship works correctly")
}
