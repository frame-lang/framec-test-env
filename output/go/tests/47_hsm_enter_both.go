
package main

import "fmt"
import "os"

type HSMEnterBothFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMEnterBothFrameContext struct {
    _event  HSMEnterBothFrameEvent
    _return any
    _data   map[string]any
}

type HSMEnterBothCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMEnterBothFrameEvent
    parentCompartment *HSMEnterBothCompartment
}

func newHSMEnterBothCompartment(state string) *HSMEnterBothCompartment {
    return &HSMEnterBothCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMEnterBothCompartment) copy() *HSMEnterBothCompartment {
    nc := &HSMEnterBothCompartment{
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

type HSMEnterBoth struct {
    _state_stack []*HSMEnterBothCompartment
    __compartment *HSMEnterBothCompartment
    __next_compartment *HSMEnterBothCompartment
    _context_stack []HSMEnterBothFrameContext
    log []string
}

func NewHSMEnterBoth() *HSMEnterBoth {
    s := &HSMEnterBoth{}
    s._state_stack = make([]*HSMEnterBothCompartment, 0)
    s._context_stack = make([]HSMEnterBothFrameContext, 0)
    s.__compartment = newHSMEnterBothCompartment("Start")
    s.__next_compartment = nil
    __frame_event := HSMEnterBothFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMEnterBothFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMEnterBoth) __kernel(__e *HSMEnterBothFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMEnterBothFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMEnterBothFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMEnterBothFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMEnterBoth) __router(__e *HSMEnterBothFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMEnterBoth) __transition(next *HSMEnterBothCompartment) {
    s.__next_compartment = next
}

func (s *HSMEnterBoth) GoToChild() {
    __e := HSMEnterBothFrameEvent{_message: "GoToChild"}
    __ctx := HSMEnterBothFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterBoth) GoToParent() {
    __e := HSMEnterBothFrameEvent{_message: "GoToParent"}
    __ctx := HSMEnterBothFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterBoth) GetLog() []string {
    __e := HSMEnterBothFrameEvent{_message: "GetLog"}
    __ctx := HSMEnterBothFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterBoth) GetState() string {
    __e := HSMEnterBothFrameEvent{_message: "GetState"}
    __ctx := HSMEnterBothFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterBoth) _state_Start(__e *HSMEnterBothFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Start"
        return
    } else if __e._message == "GoToChild" {
        __compartment := newHSMEnterBothCompartment("Child")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GoToParent" {
        __compartment := newHSMEnterBothCompartment("Parent")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMEnterBoth) _state_Child(__e *HSMEnterBothFrameEvent) {
    if __e._message == "$>" {
        s.log = append(s.log, "Child:enter")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Child"
        return
    } else if __e._message == "GoToParent" {
        __compartment := newHSMEnterBothCompartment("Parent")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMEnterBoth) _state_Parent(__e *HSMEnterBothFrameEvent) {
    if __e._message == "$>" {
        s.log = append(s.log, "Parent:enter")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    } else if __e._message == "GoToChild" {
        __compartment := newHSMEnterBothCompartment("Child")
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
	fmt.Println("=== Test 47: HSM Enter in Both ===")
	sm := NewHSMEnterBoth()

	// TC2.3.1: Only child's enter fires when entering child
	sm.GoToChild()
	log := sm.GetLog()
	if !contains(log, "Child:enter") {
		fmt.Printf("FAIL: Expected Child:enter, got %v\n", log)
		os.Exit(1)
	}
	if contains(log, "Parent:enter") {
		fmt.Printf("FAIL: Parent:enter should NOT fire when entering child, got %v\n", log)
		os.Exit(1)
	}
	if sm.GetState() != "Child" {
		fmt.Printf("FAIL: Expected Child, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC2.3.1: Only child's enter fires when entering child - PASS")

	// TC2.3.2: Parent's enter fires only when transitioning to parent
	sm.GoToParent()
	log = sm.GetLog()
	if !contains(log, "Parent:enter") {
		fmt.Printf("FAIL: Expected Parent:enter, got %v\n", log)
		os.Exit(1)
	}
	if sm.GetState() != "Parent" {
		fmt.Printf("FAIL: Expected Parent, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC2.3.2: Parent's enter fires when transitioning to parent - PASS")

	// TC2.3.3: No implicit cascading - counts should be exactly 1 each
	childCount := countOccurrences(log, "Child:enter")
	parentCount := countOccurrences(log, "Parent:enter")
	if childCount != 1 {
		fmt.Printf("FAIL: Expected exactly 1 Child:enter, got %v\n", log)
		os.Exit(1)
	}
	if parentCount != 1 {
		fmt.Printf("FAIL: Expected exactly 1 Parent:enter, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.3.3: No implicit cascading of enter handlers - PASS")

	// TC2.3.4: Going back to child fires child enter again
	sm.GoToChild()
	log = sm.GetLog()
	childCount2 := countOccurrences(log, "Child:enter")
	parentCount2 := countOccurrences(log, "Parent:enter")
	if childCount2 != 2 {
		fmt.Printf("FAIL: Expected 2 Child:enter, got %v\n", log)
		os.Exit(1)
	}
	if parentCount2 != 1 {
		fmt.Printf("FAIL: Expected still 1 Parent:enter, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.3.4: Re-entering child fires child enter again - PASS")

	fmt.Println("PASS: HSM enter in both works correctly")
}
