
package main

import "fmt"
import "os"

type HSMExitHandlersFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMExitHandlersFrameContext struct {
    _event  HSMExitHandlersFrameEvent
    _return any
    _data   map[string]any
}

type HSMExitHandlersCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMExitHandlersFrameEvent
    parentCompartment *HSMExitHandlersCompartment
}

func newHSMExitHandlersCompartment(state string) *HSMExitHandlersCompartment {
    return &HSMExitHandlersCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMExitHandlersCompartment) copy() *HSMExitHandlersCompartment {
    nc := &HSMExitHandlersCompartment{
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

type HSMExitHandlers struct {
    _state_stack []*HSMExitHandlersCompartment
    __compartment *HSMExitHandlersCompartment
    __next_compartment *HSMExitHandlersCompartment
    _context_stack []HSMExitHandlersFrameContext
    log []string
}

func NewHSMExitHandlers() *HSMExitHandlers {
    s := &HSMExitHandlers{}
    s._state_stack = make([]*HSMExitHandlersCompartment, 0)
    s._context_stack = make([]HSMExitHandlersFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMExitHandlersCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newHSMExitHandlersCompartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMExitHandlersFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMExitHandlersFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMExitHandlers) __kernel(__e *HSMExitHandlersFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMExitHandlersFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMExitHandlersFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMExitHandlersFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMExitHandlers) __router(__e *HSMExitHandlersFrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    case "Other":
        s._state_Other(__e)
    }
}

func (s *HSMExitHandlers) __transition(next *HSMExitHandlersCompartment) {
    s.__next_compartment = next
}

func (s *HSMExitHandlers) GoToOther() {
    __e := HSMExitHandlersFrameEvent{_message: "GoToOther"}
    __ctx := HSMExitHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMExitHandlers) GoToParent() {
    __e := HSMExitHandlersFrameEvent{_message: "GoToParent"}
    __ctx := HSMExitHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMExitHandlers) GoToChild() {
    __e := HSMExitHandlersFrameEvent{_message: "GoToChild"}
    __ctx := HSMExitHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMExitHandlers) GetLog() []string {
    __e := HSMExitHandlersFrameEvent{_message: "GetLog"}
    __ctx := HSMExitHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMExitHandlers) GetState() string {
    __e := HSMExitHandlersFrameEvent{_message: "GetState"}
    __ctx := HSMExitHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMExitHandlers) GetChildVar() int {
    __e := HSMExitHandlersFrameEvent{_message: "GetChildVar"}
    __ctx := HSMExitHandlersFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMExitHandlers) _state_Child(__e *HSMExitHandlersFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Child" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "<$" {
        val := __sv_comp.stateVars["child_var"].(int)
        s.log = append(s.log, fmt.Sprintf("Child:exit(var=%d)", val))
    } else if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["child_var"]; !ok {
            __sv_comp.stateVars["child_var"] = 42
        }
        s.log = append(s.log, "Child:enter")
    } else if __e._message == "GetChildVar" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["child_var"].(int)
        return
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Child"
        return
    } else if __e._message == "GoToOther" {
        __compartment := newHSMExitHandlersCompartment("Other")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GoToParent" {
        __compartment := newHSMExitHandlersCompartment("Parent")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMExitHandlers) _state_Parent(__e *HSMExitHandlersFrameEvent) {
    if __e._message == "<$" {
        s.log = append(s.log, "Parent:exit")
    } else if __e._message == "$>" {
        s.log = append(s.log, "Parent:enter")
    } else if __e._message == "GetChildVar" {
        s._context_stack[len(s._context_stack)-1]._return = -1
        return
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    } else if __e._message == "GoToChild" {
        __compartment := newHSMExitHandlersCompartment("Child")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GoToOther" {
        __compartment := newHSMExitHandlersCompartment("Other")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HSMExitHandlers) _state_Other(__e *HSMExitHandlersFrameEvent) {
    if __e._message == "$>" {
        s.log = append(s.log, "Other:enter")
    } else if __e._message == "GetChildVar" {
        s._context_stack[len(s._context_stack)-1]._return = -1
        return
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Other"
        return
    } else if __e._message == "GoToChild" {
        __compartment := newHSMExitHandlersCompartment("Child")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GoToParent" {
        __compartment := newHSMExitHandlersCompartment("Parent")
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
	fmt.Println("=== Test 48: HSM Exit Handlers ===")
	sm := NewHSMExitHandlers()

	// Initial state is Child
	log := sm.GetLog()
	if !contains(log, "Child:enter") {
		fmt.Printf("FAIL: Expected Child:enter on init, got %v\n", log)
		os.Exit(1)
	}
	if sm.GetState() != "Child" {
		fmt.Printf("FAIL: Expected Child, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC2.4.0: Initial state is Child with enter - PASS")

	// TC2.4.1: Child exit fires when transitioning out of child
	sm.GoToOther()
	log = sm.GetLog()
	if !contains(log, "Child:exit(var=42)") {
		fmt.Printf("FAIL: Expected Child:exit, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "Other:enter") {
		fmt.Printf("FAIL: Expected Other:enter, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.4.1: Child exit fires when transitioning out - PASS")

	// TC2.4.2: Parent exit does NOT fire when transitioning out of child
	if contains(log, "Parent:exit") {
		fmt.Printf("FAIL: Parent:exit should NOT fire for child exit, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.4.2: Parent exit NOT fired for child exit - PASS")

	// TC2.4.3: Exit handler can access child's state variables (verified by var=42 in log)
	fmt.Println("TC2.4.3: Exit handler accesses state var (var=42) - PASS")

	// TC2.4.4: Parent exit fires when transitioning out of Parent
	sm.GoToParent()
	log = sm.GetLog()
	if !contains(log, "Parent:enter") {
		fmt.Printf("FAIL: Expected Parent:enter, got %v\n", log)
		os.Exit(1)
	}

	sm.GoToOther()
	log = sm.GetLog()
	if !contains(log, "Parent:exit") {
		fmt.Printf("FAIL: Expected Parent:exit, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.4.4: Parent exit fires when leaving parent - PASS")

	fmt.Println("PASS: HSM exit handlers work correctly")
}
