
package main

import "fmt"
import "os"

type HSMSiblingTransitionsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMSiblingTransitionsFrameContext struct {
    _event  HSMSiblingTransitionsFrameEvent
    _return any
    _data   map[string]any
}

type HSMSiblingTransitionsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMSiblingTransitionsFrameEvent
    parentCompartment *HSMSiblingTransitionsCompartment
}

func newHSMSiblingTransitionsCompartment(state string) *HSMSiblingTransitionsCompartment {
    return &HSMSiblingTransitionsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMSiblingTransitionsCompartment) copy() *HSMSiblingTransitionsCompartment {
    nc := &HSMSiblingTransitionsCompartment{
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

type HSMSiblingTransitions struct {
    _state_stack []*HSMSiblingTransitionsCompartment
    __compartment *HSMSiblingTransitionsCompartment
    __next_compartment *HSMSiblingTransitionsCompartment
    _context_stack []HSMSiblingTransitionsFrameContext
    log []string
}

func NewHSMSiblingTransitions() *HSMSiblingTransitions {
    s := &HSMSiblingTransitions{}
    s._state_stack = make([]*HSMSiblingTransitionsCompartment, 0)
    s._context_stack = make([]HSMSiblingTransitionsFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMSiblingTransitionsCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMSiblingTransitionsCompartment("ChildA")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMSiblingTransitionsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMSiblingTransitionsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMSiblingTransitions) __kernel(__e *HSMSiblingTransitionsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMSiblingTransitionsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMSiblingTransitionsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMSiblingTransitionsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMSiblingTransitions) __router(__e *HSMSiblingTransitionsFrameEvent) {
    switch s.__compartment.state {
    case "ChildA":
        s._state_ChildA(__e)
    case "ChildB":
        s._state_ChildB(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMSiblingTransitions) __transition(next *HSMSiblingTransitionsCompartment) {
    s.__next_compartment = next
}

func (s *HSMSiblingTransitions) GoToB() {
    __e := HSMSiblingTransitionsFrameEvent{_message: "GoToB"}
    __ctx := HSMSiblingTransitionsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMSiblingTransitions) GoToA() {
    __e := HSMSiblingTransitionsFrameEvent{_message: "GoToA"}
    __ctx := HSMSiblingTransitionsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMSiblingTransitions) ForwardAction() {
    __e := HSMSiblingTransitionsFrameEvent{_message: "ForwardAction"}
    __ctx := HSMSiblingTransitionsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMSiblingTransitions) GetLog() []string {
    __e := HSMSiblingTransitionsFrameEvent{_message: "GetLog"}
    __ctx := HSMSiblingTransitionsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMSiblingTransitions) GetState() string {
    __e := HSMSiblingTransitionsFrameEvent{_message: "GetState"}
    __ctx := HSMSiblingTransitionsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMSiblingTransitions) _state_Parent(__e *HSMSiblingTransitionsFrameEvent) {
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

func (s *HSMSiblingTransitions) _state_ChildA(__e *HSMSiblingTransitionsFrameEvent) {
    if __e._message == "<$" {
        s.log = append(s.log, "ChildA:exit")
    } else if __e._message == "$>" {
        s.log = append(s.log, "ChildA:enter")
    } else if __e._message == "ForwardAction" {
        s.log = append(s.log, "ChildA:forward")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "ChildA"
        return
    } else if __e._message == "GoToB" {
        s.log = append(s.log, "ChildA:go_to_b")
        __compartment := newHSMSiblingTransitionsCompartment("ChildB")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMSiblingTransitions) _state_ChildB(__e *HSMSiblingTransitionsFrameEvent) {
    if __e._message == "<$" {
        s.log = append(s.log, "ChildB:exit")
    } else if __e._message == "$>" {
        s.log = append(s.log, "ChildB:enter")
    } else if __e._message == "ForwardAction" {
        s.log = append(s.log, "ChildB:forward")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "ChildB"
        return
    } else if __e._message == "GoToA" {
        s.log = append(s.log, "ChildB:go_to_a")
        __compartment := newHSMSiblingTransitionsCompartment("ChildA")
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
	fmt.Println("=== Test 44: HSM Sibling Transitions ===")
	sm := NewHSMSiblingTransitions()

	// Initial state is ChildA with enter handler fired
	log := sm.GetLog()
	if !contains(log, "ChildA:enter") {
		fmt.Printf("FAIL: Expected ChildA:enter on init, got %v\n", log)
		os.Exit(1)
	}
	if sm.GetState() != "ChildA" {
		fmt.Printf("FAIL: Expected ChildA, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC1.4.0: Initial state ChildA with enter - PASS")

	// TC1.4.1: Transition from ChildA to ChildB
	sm.GoToB()
	if sm.GetState() != "ChildB" {
		fmt.Printf("FAIL: Expected ChildB, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC1.4.1: Transition A->B works - PASS")

	// TC1.4.2: Exit handler fired on source
	log = sm.GetLog()
	if !contains(log, "ChildA:exit") {
		fmt.Printf("FAIL: Expected ChildA:exit, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.4.2: Exit handler fires on source - PASS")

	// TC1.4.3: Enter handler fired on target
	if !contains(log, "ChildB:enter") {
		fmt.Printf("FAIL: Expected ChildB:enter, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.4.3: Enter handler fires on target - PASS")

	// TC1.4.4: Parent relationship preserved - ChildB can forward
	sm.ForwardAction()
	log = sm.GetLog()
	if !contains(log, "ChildB:forward") {
		fmt.Printf("FAIL: Expected ChildB:forward, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:forward_action") {
		fmt.Printf("FAIL: Expected Parent handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.4.4: Parent relationship preserved - PASS")

	// TC1.4.5: Transition back to ChildA
	sm.GoToA()
	if sm.GetState() != "ChildA" {
		fmt.Printf("FAIL: Expected ChildA, got %s\n", sm.GetState())
		os.Exit(1)
	}
	log = sm.GetLog()
	exitBCount := countOccurrences(log, "ChildB:exit")
	enterACount := countOccurrences(log, "ChildA:enter")
	if exitBCount != 1 {
		fmt.Printf("FAIL: Expected ChildB:exit once, got %v\n", log)
		os.Exit(1)
	}
	if enterACount != 2 {
		fmt.Printf("FAIL: Expected ChildA:enter twice, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.4.5: Transition B->A works with enter/exit - PASS")

	// TC1.4.6: ChildA can still forward after returning
	sm.ForwardAction()
	log = sm.GetLog()
	if !contains(log, "ChildA:forward") {
		fmt.Printf("FAIL: Expected ChildA:forward, got %v\n", log)
		os.Exit(1)
	}
	parentCount := countOccurrences(log, "Parent:forward_action")
	if parentCount != 2 {
		fmt.Printf("FAIL: Expected 2 Parent handlers, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.4.6: ChildA forwards after returning - PASS")

	fmt.Println("PASS: HSM sibling transitions work correctly")
}
