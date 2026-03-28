
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

// Test 51: HSM Persistence
//
// Tests that HSM parent compartment chain is properly saved and restored:
// - Child state vars preserved
// - Parent state vars preserved
// - Parent compartment chain intact after restore
// - Forwarding to parent still works after restore

type HSMPersistFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMPersistFrameContext struct {
    _event  HSMPersistFrameEvent
    _return any
    _data   map[string]any
}

type HSMPersistCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMPersistFrameEvent
    parentCompartment *HSMPersistCompartment
}

func newHSMPersistCompartment(state string) *HSMPersistCompartment {
    return &HSMPersistCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMPersistCompartment) copy() *HSMPersistCompartment {
    nc := &HSMPersistCompartment{
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

type HSMPersist struct {
    _state_stack []*HSMPersistCompartment
    __compartment *HSMPersistCompartment
    __next_compartment *HSMPersistCompartment
    _context_stack []HSMPersistFrameContext
}

func NewHSMPersist() *HSMPersist {
    s := &HSMPersist{}
    s._state_stack = make([]*HSMPersistCompartment, 0)
    s._context_stack = make([]HSMPersistFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newHSMPersistCompartment("Parent")
    __parent_comp_0.parentCompartment = nil
    __parent_comp_0.stateVars["parent_count"] = 100
    s.__compartment = newHSMPersistCompartment("Child")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := HSMPersistFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMPersistFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMPersist) __kernel(__e *HSMPersistFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMPersistFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMPersistFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMPersistFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMPersist) __router(__e *HSMPersistFrameEvent) {
    switch s.__compartment.state {
    case "Child":
        s._state_Child(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMPersist) __transition(next *HSMPersistCompartment) {
    s.__next_compartment = next
}

func (s *HSMPersist) IncrementChild() {
    __e := HSMPersistFrameEvent{_message: "IncrementChild"}
    __ctx := HSMPersistFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMPersist) IncrementParent() {
    __e := HSMPersistFrameEvent{_message: "IncrementParent"}
    __ctx := HSMPersistFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMPersist) GetChildCount() int {
    __e := HSMPersistFrameEvent{_message: "GetChildCount"}
    __ctx := HSMPersistFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMPersist) GetParentCount() int {
    __e := HSMPersistFrameEvent{_message: "GetParentCount"}
    __ctx := HSMPersistFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMPersist) GetState() string {
    __e := HSMPersistFrameEvent{_message: "GetState"}
    __ctx := HSMPersistFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMPersist) _state_Parent(__e *HSMPersistFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Parent" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["parent_count"]; !ok {
            __sv_comp.stateVars["parent_count"] = 100
        }
    } else if __e._message == "GetParentCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["parent_count"].(int)
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    } else if __e._message == "IncrementParent" {
        __sv_comp.stateVars["parent_count"] = __sv_comp.stateVars["parent_count"].(int) + 1
    }
}

func (s *HSMPersist) _state_Child(__e *HSMPersistFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Child" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["child_count"]; !ok {
            __sv_comp.stateVars["child_count"] = 0
        }
    } else if __e._message == "GetChildCount" {
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["child_count"].(int)
        return
    } else if __e._message == "GetParentCount" {
        // Forward to parent
        s._state_Parent(__e)
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Child"
        return
    } else if __e._message == "IncrementChild" {
        __sv_comp.stateVars["child_count"] = __sv_comp.stateVars["child_count"].(int) + 1
    } else if __e._message == "IncrementParent" {
        // Forward to parent
        s._state_Parent(__e)
    }
}

// --- Persist helpers with HSM parent compartment chain ---

type hsmCompSnap struct {
	State     string         `json:"state"`
	StateVars map[string]any `json:"state_vars,omitempty"`
	Parent    *hsmCompSnap   `json:"parent,omitempty"`
}

type hsmPersistSnapshot struct {
	Compartment hsmCompSnap `json:"compartment"`
}

func saveHSMComp(c *HSMPersistCompartment) hsmCompSnap {
	vars := make(map[string]any)
	for k, v := range c.stateVars {
		vars[k] = v
	}
	snap := hsmCompSnap{State: c.state, StateVars: vars}
	if c.parentCompartment != nil {
		parent := saveHSMComp(c.parentCompartment)
		snap.Parent = &parent
	}
	return snap
}

func saveHSMPersist(s *HSMPersist) string {
	snap := hsmPersistSnapshot{
		Compartment: saveHSMComp(s.__compartment),
	}
	b, err := json.Marshal(snap)
	if err != nil {
		panic(err)
	}
	return string(b)
}

func restoreHSMComp(cs hsmCompSnap) *HSMPersistCompartment {
	c := newHSMPersistCompartment(cs.State)
	for k, v := range cs.StateVars {
		if f, ok := v.(float64); ok {
			c.stateVars[k] = int(f)
		} else {
			c.stateVars[k] = v
		}
	}
	if cs.Parent != nil {
		c.parentCompartment = restoreHSMComp(*cs.Parent)
	}
	return c
}

func restoreHSMPersist(jsonStr string) *HSMPersist {
	var snap hsmPersistSnapshot
	if err := json.Unmarshal([]byte(jsonStr), &snap); err != nil {
		panic(err)
	}
	s := &HSMPersist{}
	s._state_stack = make([]*HSMPersistCompartment, 0)
	s._context_stack = make([]HSMPersistFrameContext, 0)
	s.__compartment = restoreHSMComp(snap.Compartment)
	s.__next_compartment = nil
	return s
}

func main() {
	fmt.Println("=== Test 51: HSM Persistence (Go) ===")

	// Create system and modify state vars at both levels
	s1 := NewHSMPersist()

	// Verify initial state
	if s1.GetState() != "Child" {
		fmt.Printf("FAIL: Expected Child, got %s\n", s1.GetState())
		os.Exit(1)
	}
	if s1.GetChildCount() != 0 {
		fmt.Printf("FAIL: Expected 0, got %d\n", s1.GetChildCount())
		os.Exit(1)
	}
	if s1.GetParentCount() != 100 {
		fmt.Printf("FAIL: Expected 100, got %d\n", s1.GetParentCount())
		os.Exit(1)
	}
	fmt.Println("1. Initial state verified: Child with child_count=0, parent_count=100")

	// Modify state vars at both levels
	s1.IncrementChild()
	s1.IncrementChild()
	s1.IncrementChild() // child_count = 3
	s1.IncrementParent()
	s1.IncrementParent() // parent_count = 102

	if s1.GetChildCount() != 3 {
		fmt.Printf("FAIL: Expected 3, got %d\n", s1.GetChildCount())
		os.Exit(1)
	}
	if s1.GetParentCount() != 102 {
		fmt.Printf("FAIL: Expected 102, got %d\n", s1.GetParentCount())
		os.Exit(1)
	}
	fmt.Printf("2. After increments: child_count=%d, parent_count=%d\n", s1.GetChildCount(), s1.GetParentCount())

	// Save state
	data := saveHSMPersist(s1)
	fmt.Printf("3. Saved state: %s\n", data)

	// Restore to new instance
	s2 := restoreHSMPersist(data)

	// Verify restored state
	if s2.GetState() != "Child" {
		fmt.Printf("FAIL: Expected Child after restore, got %s\n", s2.GetState())
		os.Exit(1)
	}
	fmt.Printf("4. Restored state: %s\n", s2.GetState())

	// Verify child state var preserved
	if s2.GetChildCount() != 3 {
		fmt.Printf("FAIL: Expected child_count=3, got %d\n", s2.GetChildCount())
		os.Exit(1)
	}
	fmt.Printf("5. Child state var preserved: child_count=%d\n", s2.GetChildCount())

	// Verify parent state var preserved (requires parent compartment chain)
	if s2.GetParentCount() != 102 {
		fmt.Printf("FAIL: Expected parent_count=102, got %d\n", s2.GetParentCount())
		os.Exit(1)
	}
	fmt.Printf("6. Parent state var preserved: parent_count=%d\n", s2.GetParentCount())

	// Verify state machine still works after restore
	s2.IncrementChild()
	s2.IncrementParent()
	if s2.GetChildCount() != 4 {
		fmt.Printf("FAIL: Expected 4, got %d\n", s2.GetChildCount())
		os.Exit(1)
	}
	if s2.GetParentCount() != 103 {
		fmt.Printf("FAIL: Expected 103, got %d\n", s2.GetParentCount())
		os.Exit(1)
	}
	fmt.Printf("7. After post-restore increments: child_count=%d, parent_count=%d\n", s2.GetChildCount(), s2.GetParentCount())

	fmt.Println("PASS: HSM persistence works correctly")
}
