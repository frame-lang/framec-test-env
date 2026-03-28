
package main

import "fmt"
import "os"

type HSMMultiChildrenFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMMultiChildrenFrameContext struct {
    _event  HSMMultiChildrenFrameEvent
    _return any
    _data   map[string]any
}

type HSMMultiChildrenCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMMultiChildrenFrameEvent
    parentCompartment *HSMMultiChildrenCompartment
}

func newHSMMultiChildrenCompartment(state string) *HSMMultiChildrenCompartment {
    return &HSMMultiChildrenCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMMultiChildrenCompartment) copy() *HSMMultiChildrenCompartment {
    nc := &HSMMultiChildrenCompartment{
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

type HSMMultiChildren struct {
    _state_stack []*HSMMultiChildrenCompartment
    __compartment *HSMMultiChildrenCompartment
    __next_compartment *HSMMultiChildrenCompartment
    _context_stack []HSMMultiChildrenFrameContext
    log []string
}

func NewHSMMultiChildren() *HSMMultiChildren {
    s := &HSMMultiChildren{}
    s._state_stack = make([]*HSMMultiChildrenCompartment, 0)
    s._context_stack = make([]HSMMultiChildrenFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMMultiChildrenCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMMultiChildrenCompartment("ChildA")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMMultiChildrenFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMMultiChildrenFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMMultiChildren) __kernel(__e *HSMMultiChildrenFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMMultiChildrenFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMMultiChildrenFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMMultiChildrenFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMMultiChildren) __router(__e *HSMMultiChildrenFrameEvent) {
    switch s.__compartment.state {
    case "ChildA":
        s._state_ChildA(__e)
    case "ChildB":
        s._state_ChildB(__e)
    case "ChildC":
        s._state_ChildC(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMMultiChildren) __transition(next *HSMMultiChildrenCompartment) {
    s.__next_compartment = next
}

func (s *HSMMultiChildren) StartA() {
    __e := HSMMultiChildrenFrameEvent{_message: "StartA"}
    __ctx := HSMMultiChildrenFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMMultiChildren) StartB() {
    __e := HSMMultiChildrenFrameEvent{_message: "StartB"}
    __ctx := HSMMultiChildrenFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMMultiChildren) StartC() {
    __e := HSMMultiChildrenFrameEvent{_message: "StartC"}
    __ctx := HSMMultiChildrenFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMMultiChildren) DoAction() {
    __e := HSMMultiChildrenFrameEvent{_message: "DoAction"}
    __ctx := HSMMultiChildrenFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMMultiChildren) ForwardAction() {
    __e := HSMMultiChildrenFrameEvent{_message: "ForwardAction"}
    __ctx := HSMMultiChildrenFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMMultiChildren) GetLog() []string {
    __e := HSMMultiChildrenFrameEvent{_message: "GetLog"}
    __ctx := HSMMultiChildrenFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMMultiChildren) GetState() string {
    __e := HSMMultiChildrenFrameEvent{_message: "GetState"}
    __ctx := HSMMultiChildrenFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMMultiChildren) _state_Parent(__e *HSMMultiChildrenFrameEvent) {
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

func (s *HSMMultiChildren) _state_ChildC(__e *HSMMultiChildrenFrameEvent) {
    if __e._message == "DoAction" {
        s.log = append(s.log, "ChildC:do_action")
    } else if __e._message == "ForwardAction" {
        s.log = append(s.log, "ChildC:forward_action")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "ChildC"
        return
    } else if __e._message == "StartA" {
        __compartment := newHSMMultiChildrenCompartment("ChildA")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "StartB" {
        __compartment := newHSMMultiChildrenCompartment("ChildB")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "StartC" {
        // stay
    }
}

func (s *HSMMultiChildren) _state_ChildA(__e *HSMMultiChildrenFrameEvent) {
    if __e._message == "DoAction" {
        s.log = append(s.log, "ChildA:do_action")
    } else if __e._message == "ForwardAction" {
        s.log = append(s.log, "ChildA:forward_action")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "ChildA"
        return
    } else if __e._message == "StartA" {
        // stay
    } else if __e._message == "StartB" {
        __compartment := newHSMMultiChildrenCompartment("ChildB")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "StartC" {
        __compartment := newHSMMultiChildrenCompartment("ChildC")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMMultiChildren) _state_ChildB(__e *HSMMultiChildrenFrameEvent) {
    if __e._message == "DoAction" {
        s.log = append(s.log, "ChildB:do_action")
    } else if __e._message == "ForwardAction" {
        s.log = append(s.log, "ChildB:forward_action")
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "ChildB"
        return
    } else if __e._message == "StartA" {
        __compartment := newHSMMultiChildrenCompartment("ChildA")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "StartB" {
        // stay
    } else if __e._message == "StartC" {
        __compartment := newHSMMultiChildrenCompartment("ChildC")
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
	fmt.Println("=== Test 43: HSM Multiple Children ===")
	sm := NewHSMMultiChildren()

	// TC1.3.1: Multiple children declare same parent (verified by compilation)
	fmt.Println("TC1.3.1: Multiple children with same parent compiles - PASS")

	// Start in ChildA
	if sm.GetState() != "ChildA" {
		fmt.Printf("FAIL: Expected ChildA, got %s\n", sm.GetState())
		os.Exit(1)
	}

	// TC1.3.2: ChildA can forward to shared parent
	sm.ForwardAction()
	log := sm.GetLog()
	if !contains(log, "ChildA:forward_action") {
		fmt.Printf("FAIL: Expected ChildA forward, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:forward_action") {
		fmt.Printf("FAIL: Expected Parent handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.3.2: ChildA forwards to parent - PASS")

	// TC1.3.3: Transition to sibling
	sm.StartB()
	if sm.GetState() != "ChildB" {
		fmt.Printf("FAIL: Expected ChildB after transition, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC1.3.3: Transition A->B works - PASS")

	// TC1.3.4: ChildB can also forward to same parent
	sm.ForwardAction()
	log = sm.GetLog()
	if !contains(log, "ChildB:forward_action") {
		fmt.Printf("FAIL: Expected ChildB forward, got %v\n", log)
		os.Exit(1)
	}
	parentCount := countOccurrences(log, "Parent:forward_action")
	if parentCount != 2 {
		fmt.Printf("FAIL: Expected 2 Parent forwards, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.3.4: ChildB forwards to same parent - PASS")

	// TC1.3.5: Transition to ChildC
	sm.StartC()
	if sm.GetState() != "ChildC" {
		fmt.Printf("FAIL: Expected ChildC, got %s\n", sm.GetState())
		os.Exit(1)
	}
	sm.ForwardAction()
	log = sm.GetLog()
	if !contains(log, "ChildC:forward_action") {
		fmt.Printf("FAIL: Expected ChildC forward, got %v\n", log)
		os.Exit(1)
	}
	parentCount2 := countOccurrences(log, "Parent:forward_action")
	if parentCount2 != 3 {
		fmt.Printf("FAIL: Expected 3 Parent forwards, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.3.5: ChildC forwards to same parent - PASS")

	// TC1.3.6: Each sibling maintains independent actions
	sm.StartA()
	sm.DoAction()
	sm.StartB()
	sm.DoAction()
	sm.StartC()
	sm.DoAction()
	log = sm.GetLog()
	if !contains(log, "ChildA:do_action") {
		fmt.Println("FAIL: Expected ChildA action")
		os.Exit(1)
	}
	if !contains(log, "ChildB:do_action") {
		fmt.Println("FAIL: Expected ChildB action")
		os.Exit(1)
	}
	if !contains(log, "ChildC:do_action") {
		fmt.Println("FAIL: Expected ChildC action")
		os.Exit(1)
	}
	fmt.Println("TC1.3.6: Each sibling has independent handlers - PASS")

	fmt.Println("PASS: HSM multiple children work correctly")
}
