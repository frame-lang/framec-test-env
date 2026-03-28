
package main

import "fmt"
import "os"

type HSMEnterParentOnlyFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMEnterParentOnlyFrameContext struct {
    _event  HSMEnterParentOnlyFrameEvent
    _return any
    _data   map[string]any
}

type HSMEnterParentOnlyCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMEnterParentOnlyFrameEvent
    parentCompartment *HSMEnterParentOnlyCompartment
}

func newHSMEnterParentOnlyCompartment(state string) *HSMEnterParentOnlyCompartment {
    return &HSMEnterParentOnlyCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMEnterParentOnlyCompartment) copy() *HSMEnterParentOnlyCompartment {
    nc := &HSMEnterParentOnlyCompartment{
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

type HSMEnterParentOnly struct {
    _state_stack []*HSMEnterParentOnlyCompartment
    __compartment *HSMEnterParentOnlyCompartment
    __next_compartment *HSMEnterParentOnlyCompartment
    _context_stack []HSMEnterParentOnlyFrameContext
    log []string
}

func NewHSMEnterParentOnly() *HSMEnterParentOnly {
    s := &HSMEnterParentOnly{}
    s._state_stack = make([]*HSMEnterParentOnlyCompartment, 0)
    s._context_stack = make([]HSMEnterParentOnlyFrameContext, 0)
    s.__compartment = newHSMEnterParentOnlyCompartment("Start")
    s.__next_compartment = nil
    __frame_event := HSMEnterParentOnlyFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMEnterParentOnlyFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMEnterParentOnly) __kernel(__e *HSMEnterParentOnlyFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMEnterParentOnlyFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMEnterParentOnlyFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMEnterParentOnlyFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMEnterParentOnly) __router(__e *HSMEnterParentOnlyFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMEnterParentOnly) __transition(next *HSMEnterParentOnlyCompartment) {
    s.__next_compartment = next
}

func (s *HSMEnterParentOnly) GoToChild() {
    __e := HSMEnterParentOnlyFrameEvent{_message: "GoToChild"}
    __ctx := HSMEnterParentOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterParentOnly) GoToParent() {
    __e := HSMEnterParentOnlyFrameEvent{_message: "GoToParent"}
    __ctx := HSMEnterParentOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterParentOnly) GetLog() []string {
    __e := HSMEnterParentOnlyFrameEvent{_message: "GetLog"}
    __ctx := HSMEnterParentOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterParentOnly) GetState() string {
    __e := HSMEnterParentOnlyFrameEvent{_message: "GetState"}
    __ctx := HSMEnterParentOnlyFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterParentOnly) _state_Parent(__e *HSMEnterParentOnlyFrameEvent) {
    if __e._message == "$>" {
        s.log = append(s.log, "Parent:enter")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    } else if __e._message == "GoToChild" {
        __compartment := newHSMEnterParentOnlyCompartment("Child")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMEnterParentOnly) _state_Start(__e *HSMEnterParentOnlyFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Start"
        return
    } else if __e._message == "GoToChild" {
        __compartment := newHSMEnterParentOnlyCompartment("Child")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GoToParent" {
        __compartment := newHSMEnterParentOnlyCompartment("Parent")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMEnterParentOnly) _state_Child(__e *HSMEnterParentOnlyFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Child"
        return
    } else if __e._message == "GoToParent" {
        __compartment := newHSMEnterParentOnlyCompartment("Parent")
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
	fmt.Println("=== Test 46: HSM Enter in Parent Only ===")
	sm := NewHSMEnterParentOnly()

	// TC2.2.1: Child enters without error (no enter handler)
	sm.GoToChild()
	if sm.GetState() != "Child" {
		fmt.Printf("FAIL: Expected Child, got %s\n", sm.GetState())
		os.Exit(1)
	}
	log := sm.GetLog()
	fmt.Printf("TC2.2.1: Child enters without error (log: %v) - PASS\n", log)

	// TC2.2.2: Parent's enter does NOT auto-fire when child is entered
	if contains(log, "Parent:enter") {
		fmt.Printf("FAIL: Parent:enter should NOT fire for child entry, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.2.2: Parent enter NOT auto-fired for child - PASS")

	// TC2.2.3: Parent enter only fires when transitioning directly TO parent
	sm.GoToParent()
	if sm.GetState() != "Parent" {
		fmt.Printf("FAIL: Expected Parent, got %s\n", sm.GetState())
		os.Exit(1)
	}
	log = sm.GetLog()
	if !contains(log, "Parent:enter") {
		fmt.Printf("FAIL: Expected Parent:enter when transitioning to Parent, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.2.3: Parent enter fires when transitioning to Parent - PASS")

	// TC2.2.4: Going back to child from parent
	sm.GoToChild()
	if sm.GetState() != "Child" {
		fmt.Printf("FAIL: Expected Child, got %s\n", sm.GetState())
		os.Exit(1)
	}
	log = sm.GetLog()
	count := countOccurrences(log, "Parent:enter")
	if count != 1 {
		fmt.Printf("FAIL: Expected exactly 1 Parent:enter, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.2.4: Return to child, parent enter count unchanged - PASS")

	fmt.Println("PASS: HSM enter in parent only works correctly")
}
