
package main

import "fmt"
import "os"

type HSMThreeLevelsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMThreeLevelsFrameContext struct {
    _event  HSMThreeLevelsFrameEvent
    _return any
    _data   map[string]any
}

type HSMThreeLevelsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMThreeLevelsFrameEvent
    parentCompartment *HSMThreeLevelsCompartment
}

func newHSMThreeLevelsCompartment(state string) *HSMThreeLevelsCompartment {
    return &HSMThreeLevelsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMThreeLevelsCompartment) copy() *HSMThreeLevelsCompartment {
    nc := &HSMThreeLevelsCompartment{
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

type HSMThreeLevels struct {
    _state_stack []*HSMThreeLevelsCompartment
    __compartment *HSMThreeLevelsCompartment
    __next_compartment *HSMThreeLevelsCompartment
    _context_stack []HSMThreeLevelsFrameContext
    log []string
}

func NewHSMThreeLevels() *HSMThreeLevels {
    s := &HSMThreeLevels{}
    s._state_stack = make([]*HSMThreeLevelsCompartment, 0)
    s._context_stack = make([]HSMThreeLevelsFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMThreeLevelsCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    __parent_comp_0.stateVars["parent_var"] = 100
    __parent_comp_1 := newHSMThreeLevelsCompartment("Child")
    __parent_comp_1.parentCompartment = __parent_comp_0
    __parent_comp_1.stateVars["child_var"] = 10
    s.__compartment = newHSMThreeLevelsCompartment("Grandchild")
    s.__compartment.parentCompartment = __parent_comp_1
    s.__next_compartment = nil
    __frame_event := HSMThreeLevelsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMThreeLevelsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMThreeLevels) __kernel(__e *HSMThreeLevelsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMThreeLevelsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMThreeLevelsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMThreeLevelsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMThreeLevels) __router(__e *HSMThreeLevelsFrameEvent) {
    switch s.__compartment.state {
    case "Grandchild":
        s._state_Grandchild(__e)
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMThreeLevels) __transition(next *HSMThreeLevelsCompartment) {
    s.__next_compartment = next
}

func (s *HSMThreeLevels) HandleAtGrandchild() {
    __e := HSMThreeLevelsFrameEvent{_message: "HandleAtGrandchild"}
    __ctx := HSMThreeLevelsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMThreeLevels) ForwardToChild() {
    __e := HSMThreeLevelsFrameEvent{_message: "ForwardToChild"}
    __ctx := HSMThreeLevelsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMThreeLevels) ForwardToParent() {
    __e := HSMThreeLevelsFrameEvent{_message: "ForwardToParent"}
    __ctx := HSMThreeLevelsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMThreeLevels) ForwardThroughAll() {
    __e := HSMThreeLevelsFrameEvent{_message: "ForwardThroughAll"}
    __ctx := HSMThreeLevelsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMThreeLevels) GetLog() []string {
    __e := HSMThreeLevelsFrameEvent{_message: "GetLog"}
    __ctx := HSMThreeLevelsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMThreeLevels) _state_Child(__e *HSMThreeLevelsFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Child" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["child_var"]; !ok {
            __sv_comp.stateVars["child_var"] = 10
        }
    } else if __e._message == "ForwardThroughAll" {
        val := __sv_comp.stateVars["child_var"].(int)
        s.log = append(s.log, fmt.Sprintf("Child:forward_through_all(var=%d)", val))
        s._state_Parent(__e)
    } else if __e._message == "ForwardToChild" {
        val := __sv_comp.stateVars["child_var"].(int)
        s.log = append(s.log, fmt.Sprintf("Child:handled(var=%d)", val))
    } else if __e._message == "ForwardToParent" {
        val := __sv_comp.stateVars["child_var"].(int)
        s.log = append(s.log, fmt.Sprintf("Child:forward_to_parent(var=%d)", val))
        s._state_Parent(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    }
}

func (s *HSMThreeLevels) _state_Grandchild(__e *HSMThreeLevelsFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Grandchild" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["grandchild_var"]; !ok {
            __sv_comp.stateVars["grandchild_var"] = 1
        }
    } else if __e._message == "ForwardThroughAll" {
        s.log = append(s.log, "Grandchild:forward_through_all")
        s._state_Child(__e)
    } else if __e._message == "ForwardToChild" {
        s.log = append(s.log, "Grandchild:forward_to_child")
        s._state_Child(__e)
    } else if __e._message == "ForwardToParent" {
        s.log = append(s.log, "Grandchild:forward_to_parent")
        s._state_Child(__e)
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "HandleAtGrandchild" {
        val := __sv_comp.stateVars["grandchild_var"].(int)
        s.log = append(s.log, fmt.Sprintf("Grandchild:handled(var=%d)", val))
    }
}

func (s *HSMThreeLevels) _state_Parent(__e *HSMThreeLevelsFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Parent" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["parent_var"]; !ok {
            __sv_comp.stateVars["parent_var"] = 100
        }
    } else if __e._message == "ForwardThroughAll" {
        val := __sv_comp.stateVars["parent_var"].(int)
        s.log = append(s.log, fmt.Sprintf("Parent:forward_through_all(var=%d)", val))
    } else if __e._message == "ForwardToParent" {
        val := __sv_comp.stateVars["parent_var"].(int)
        s.log = append(s.log, fmt.Sprintf("Parent:handled(var=%d)", val))
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
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
	fmt.Println("=== Test 42: HSM Three-Level Hierarchy ===")
	sm := NewHSMThreeLevels()

	// TC1.2.1: Three-level hierarchy compiles
	fmt.Println("TC1.2.1: Three-level hierarchy compiles - PASS")

	// TC1.2.2: Handle at grandchild (no forward)
	sm.HandleAtGrandchild()
	log := sm.GetLog()
	if !contains(log, "Grandchild:handled(var=1)") {
		fmt.Printf("FAIL: Expected Grandchild handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.2.2: Grandchild handles locally - PASS")

	// TC1.2.3: Forward from grandchild to child
	sm.ForwardToChild()
	log = sm.GetLog()
	if !contains(log, "Grandchild:forward_to_child") {
		fmt.Printf("FAIL: Expected Grandchild forward, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Child:handled(var=10)") {
		fmt.Printf("FAIL: Expected Child handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.2.3: Forward grandchild->child - PASS")

	// TC1.2.4: Forward from grandchild through child to parent
	sm.ForwardToParent()
	log = sm.GetLog()
	if !contains(log, "Grandchild:forward_to_parent") {
		fmt.Printf("FAIL: Expected Grandchild forward, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Child:forward_to_parent(var=10)") {
		fmt.Printf("FAIL: Expected Child forward, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:handled(var=100)") {
		fmt.Printf("FAIL: Expected Parent handler, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.2.4: Forward grandchild->child->parent - PASS")

	// TC1.2.5: Forward through entire chain
	sm.ForwardThroughAll()
	log = sm.GetLog()
	if !contains(log, "Grandchild:forward_through_all") {
		fmt.Printf("FAIL: Expected Grandchild, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Child:forward_through_all(var=10)") {
		fmt.Printf("FAIL: Expected Child, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Parent:forward_through_all(var=100)") {
		fmt.Printf("FAIL: Expected Parent, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC1.2.5: Full chain forward - PASS")

	// Verify state variable isolation
	fmt.Println("TC1.2.6: State vars isolated (grandchild=1, child=10, parent=100) - PASS")

	fmt.Println("PASS: HSM three-level hierarchy works correctly")
}
