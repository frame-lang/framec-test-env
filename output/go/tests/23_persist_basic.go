
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type PersistTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type PersistTestFrameContext struct {
    _event  PersistTestFrameEvent
    _return any
    _data   map[string]any
}

type PersistTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *PersistTestFrameEvent
    parentCompartment *PersistTestCompartment
}

func newPersistTestCompartment(state string) *PersistTestCompartment {
    return &PersistTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *PersistTestCompartment) copy() *PersistTestCompartment {
    nc := &PersistTestCompartment{
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

type PersistTest struct {
    _state_stack []*PersistTestCompartment
    __compartment *PersistTestCompartment
    __next_compartment *PersistTestCompartment
    _context_stack []PersistTestFrameContext
    value int
    name string
}

func NewPersistTest() *PersistTest {
    s := &PersistTest{}
    s._state_stack = make([]*PersistTestCompartment, 0)
    s._context_stack = make([]PersistTestFrameContext, 0)
    s.__compartment = newPersistTestCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := PersistTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := PersistTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *PersistTest) __kernel(__e *PersistTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &PersistTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &PersistTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &PersistTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *PersistTest) __router(__e *PersistTestFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Active":
        s._state_Active(__e)
    }
}

func (s *PersistTest) __transition(next *PersistTestCompartment) {
    s.__next_compartment = next
}

func (s *PersistTest) SetValue(v int) {
    __params := map[string]any{
        "v": v,
    }
    __e := PersistTestFrameEvent{_message: "SetValue", _parameters: __params}
    __ctx := PersistTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistTest) GetValue() int {
    __e := PersistTestFrameEvent{_message: "GetValue"}
    __ctx := PersistTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *PersistTest) GoActive() {
    __e := PersistTestFrameEvent{_message: "GoActive"}
    __ctx := PersistTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistTest) GoIdle() {
    __e := PersistTestFrameEvent{_message: "GoIdle"}
    __ctx := PersistTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistTest) _state_Active(__e *PersistTestFrameEvent) {
    if __e._message == "GetValue" {
        s._context_stack[len(s._context_stack)-1]._return = s.value
        return
    } else if __e._message == "GoActive" {
        // Already active
    } else if __e._message == "GoIdle" {
        __compartment := newPersistTestCompartment("Idle")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "SetValue" {
        v := __e._parameters["v"].(int)
        _ = v
        s.value = v * 2
    }
}

func (s *PersistTest) _state_Idle(__e *PersistTestFrameEvent) {
    if __e._message == "GetValue" {
        s._context_stack[len(s._context_stack)-1]._return = s.value
        return
    } else if __e._message == "GoActive" {
        __compartment := newPersistTestCompartment("Active")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GoIdle" {
        // Already idle
    } else if __e._message == "SetValue" {
        v := __e._parameters["v"].(int)
        _ = v
        s.value = v
    }
}

// --- Persist helpers (same package, can access unexported fields) ---

type persistTestSnapshot struct {
	State      string `json:"state"`
	Value      int    `json:"value"`
	Name       string `json:"name"`
}

func savePersistTest(s *PersistTest) string {
	snap := persistTestSnapshot{
		State: s.__compartment.state,
		Value: s.value,
		Name:  s.name,
	}
	b, err := json.Marshal(snap)
	if err != nil {
		panic(err)
	}
	return string(b)
}

func restorePersistTest(jsonStr string) *PersistTest {
	var snap persistTestSnapshot
	if err := json.Unmarshal([]byte(jsonStr), &snap); err != nil {
		panic(err)
	}
	s := &PersistTest{}
	s._state_stack = make([]*PersistTestCompartment, 0)
	s._context_stack = make([]PersistTestFrameContext, 0)
	s.__compartment = newPersistTestCompartment(snap.State)
	s.__next_compartment = nil
	s.value = snap.Value
	s.name = snap.Name
	return s
}

func main() {
	fmt.Println("=== Test 23: Persist Basic (Go) ===")

	// Test 1: Create and modify system
	s1 := NewPersistTest()
	s1.SetValue(10)
	s1.GoActive()
	s1.SetValue(5) // Should be doubled to 10 in Active state
	if s1.GetValue() != 10 {
		fmt.Printf("FAIL: Expected 10 after doubling, got %d\n", s1.GetValue())
		os.Exit(1)
	}

	// Test 2: Save state
	data := savePersistTest(s1)
	fmt.Printf("1. Saved state: %s\n", data)

	// Test 3: Verify JSON contains expected values
	var raw map[string]any
	if err := json.Unmarshal([]byte(data), &raw); err != nil {
		fmt.Printf("FAIL: Invalid JSON: %v\n", err)
		os.Exit(1)
	}
	if raw["state"] != "Active" {
		fmt.Printf("FAIL: Expected state 'Active', got '%v'\n", raw["state"])
		os.Exit(1)
	}

	// Test 4: Restore state
	s2 := restorePersistTest(data)
	if s2.GetValue() != 10 {
		fmt.Printf("FAIL: Expected 10, got %d\n", s2.GetValue())
		os.Exit(1)
	}
	fmt.Printf("2. Restored value: %d\n", s2.GetValue())

	// Test 5: Verify state is preserved (Active state doubles)
	s2.SetValue(3) // Should be doubled to 6 in Active state
	if s2.GetValue() != 6 {
		fmt.Printf("FAIL: Expected 6, got %d\n", s2.GetValue())
		os.Exit(1)
	}
	fmt.Printf("3. After SetValue(3) in Active: %d\n", s2.GetValue())

	// Test 6: Verify transitions work after restore
	s2.GoIdle()
	s2.SetValue(4) // Should NOT be doubled in Idle state
	if s2.GetValue() != 4 {
		fmt.Printf("FAIL: Expected 4, got %d\n", s2.GetValue())
		os.Exit(1)
	}
	fmt.Printf("4. After GoIdle, SetValue(4): %d\n", s2.GetValue())

	fmt.Println("PASS: Persist basic works correctly")
}
