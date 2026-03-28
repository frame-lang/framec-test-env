
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type PersistStackFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type PersistStackFrameContext struct {
    _event  PersistStackFrameEvent
    _return any
    _data   map[string]any
}

type PersistStackCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *PersistStackFrameEvent
    parentCompartment *PersistStackCompartment
}

func newPersistStackCompartment(state string) *PersistStackCompartment {
    return &PersistStackCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *PersistStackCompartment) copy() *PersistStackCompartment {
    nc := &PersistStackCompartment{
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

type PersistStack struct {
    _state_stack []*PersistStackCompartment
    __compartment *PersistStackCompartment
    __next_compartment *PersistStackCompartment
    _context_stack []PersistStackFrameContext
    depth int
}

func NewPersistStack() *PersistStack {
    s := &PersistStack{}
    s._state_stack = make([]*PersistStackCompartment, 0)
    s._context_stack = make([]PersistStackFrameContext, 0)
    s.__compartment = newPersistStackCompartment("Start")
    s.__next_compartment = nil
    __frame_event := PersistStackFrameEvent{_message: "$>", _parameters: nil}
    __ctx := PersistStackFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *PersistStack) __kernel(__e *PersistStackFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &PersistStackFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &PersistStackFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &PersistStackFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *PersistStack) __router(__e *PersistStackFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "Middle":
        s._state_Middle(__e)
    case "End":
        s._state_End(__e)
    }
}

func (s *PersistStack) __transition(next *PersistStackCompartment) {
    s.__next_compartment = next
}

func (s *PersistStack) PushAndGo() {
    __e := PersistStackFrameEvent{_message: "PushAndGo"}
    __ctx := PersistStackFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistStack) PopBack() {
    __e := PersistStackFrameEvent{_message: "PopBack"}
    __ctx := PersistStackFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistStack) GetState() string {
    __e := PersistStackFrameEvent{_message: "GetState"}
    __ctx := PersistStackFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *PersistStack) GetDepth() int {
    __e := PersistStackFrameEvent{_message: "GetDepth"}
    __ctx := PersistStackFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *PersistStack) _state_Start(__e *PersistStackFrameEvent) {
    if __e._message == "GetDepth" {
        s._context_stack[len(s._context_stack)-1]._return = s.depth
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "start"
        return
    } else if __e._message == "PopBack" {
        // nothing to pop
    } else if __e._message == "PushAndGo" {
        s.depth = s.depth + 1
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newPersistStackCompartment("Middle")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *PersistStack) _state_End(__e *PersistStackFrameEvent) {
    if __e._message == "GetDepth" {
        s._context_stack[len(s._context_stack)-1]._return = s.depth
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "end"
        return
    } else if __e._message == "PopBack" {
        s.depth = s.depth - 1
        __popped := s._state_stack[len(s._state_stack)-1]
        s._state_stack = s._state_stack[:len(s._state_stack)-1]
        s.__transition(__popped)
        return
    } else if __e._message == "PushAndGo" {
        // cannot go further
    }
}

func (s *PersistStack) _state_Middle(__e *PersistStackFrameEvent) {
    if __e._message == "GetDepth" {
        s._context_stack[len(s._context_stack)-1]._return = s.depth
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "middle"
        return
    } else if __e._message == "PopBack" {
        s.depth = s.depth - 1
        __popped := s._state_stack[len(s._state_stack)-1]
        s._state_stack = s._state_stack[:len(s._state_stack)-1]
        s.__transition(__popped)
        return
    } else if __e._message == "PushAndGo" {
        s.depth = s.depth + 1
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newPersistStackCompartment("End")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

// --- Persist helpers with stack support ---

type persistStackCompSnap struct {
	State     string            `json:"state"`
	StateVars map[string]any    `json:"state_vars,omitempty"`
}

type persistStackSnapshot struct {
	Compartment persistStackCompSnap   `json:"compartment"`
	Stack       []persistStackCompSnap `json:"stack"`
	Depth       int                    `json:"depth"`
}

func saveCompSnap(c *PersistStackCompartment) persistStackCompSnap {
	vars := make(map[string]any)
	for k, v := range c.stateVars {
		vars[k] = v
	}
	return persistStackCompSnap{State: c.state, StateVars: vars}
}

func savePersistStack(s *PersistStack) string {
	snap := persistStackSnapshot{
		Compartment: saveCompSnap(s.__compartment),
		Depth:       s.depth,
	}
	for _, c := range s._state_stack {
		snap.Stack = append(snap.Stack, saveCompSnap(c))
	}
	b, err := json.Marshal(snap)
	if err != nil {
		panic(err)
	}
	return string(b)
}

func restoreCompSnap(cs persistStackCompSnap) *PersistStackCompartment {
	c := newPersistStackCompartment(cs.State)
	for k, v := range cs.StateVars {
		c.stateVars[k] = v
	}
	return c
}

func restorePersistStack(jsonStr string) *PersistStack {
	var snap persistStackSnapshot
	if err := json.Unmarshal([]byte(jsonStr), &snap); err != nil {
		panic(err)
	}
	s := &PersistStack{}
	s._state_stack = make([]*PersistStackCompartment, 0)
	s._context_stack = make([]PersistStackFrameContext, 0)
	s.__compartment = restoreCompSnap(snap.Compartment)
	s.__next_compartment = nil
	s.depth = snap.Depth
	for _, cs := range snap.Stack {
		s._state_stack = append(s._state_stack, restoreCompSnap(cs))
	}
	return s
}

func main() {
	fmt.Println("=== Test 25: Persist Stack (Go) ===")

	// Test 1: Build up a stack
	s1 := NewPersistStack()
	if s1.GetState() != "start" {
		fmt.Printf("FAIL: Expected start, got %s\n", s1.GetState())
		os.Exit(1)
	}

	s1.PushAndGo() // Start -> Middle (push Start)
	if s1.GetState() != "middle" {
		fmt.Printf("FAIL: Expected middle, got %s\n", s1.GetState())
		os.Exit(1)
	}
	if s1.GetDepth() != 1 {
		fmt.Printf("FAIL: Expected depth 1, got %d\n", s1.GetDepth())
		os.Exit(1)
	}

	s1.PushAndGo() // Middle -> End (push Middle)
	if s1.GetState() != "end" {
		fmt.Printf("FAIL: Expected end, got %s\n", s1.GetState())
		os.Exit(1)
	}
	if s1.GetDepth() != 2 {
		fmt.Printf("FAIL: Expected depth 2, got %d\n", s1.GetDepth())
		os.Exit(1)
	}

	fmt.Printf("1. Built stack: state=%s, depth=%d\n", s1.GetState(), s1.GetDepth())

	// Test 2: Save state (should include stack)
	data := savePersistStack(s1)
	fmt.Printf("2. Saved: %s\n", data)

	// Test 3: Restore and verify stack works
	s2 := restorePersistStack(data)
	if s2.GetState() != "end" {
		fmt.Printf("FAIL: Restored: expected end, got %s\n", s2.GetState())
		os.Exit(1)
	}
	if s2.GetDepth() != 2 {
		fmt.Printf("FAIL: Restored: expected depth 2, got %d\n", s2.GetDepth())
		os.Exit(1)
	}
	fmt.Printf("3. Restored: state=%s, depth=%d\n", s2.GetState(), s2.GetDepth())

	// Test 4: Pop should work after restore
	s2.PopBack() // End -> Middle (pop)
	if s2.GetState() != "middle" {
		fmt.Printf("FAIL: After pop: expected middle, got %s\n", s2.GetState())
		os.Exit(1)
	}
	if s2.GetDepth() != 1 {
		fmt.Printf("FAIL: After pop: expected depth 1, got %d\n", s2.GetDepth())
		os.Exit(1)
	}
	fmt.Printf("4. After pop: state=%s, depth=%d\n", s2.GetState(), s2.GetDepth())

	// Test 5: Pop again
	s2.PopBack() // Middle -> Start (pop)
	if s2.GetState() != "start" {
		fmt.Printf("FAIL: After 2nd pop: expected start, got %s\n", s2.GetState())
		os.Exit(1)
	}
	if s2.GetDepth() != 0 {
		fmt.Printf("FAIL: After 2nd pop: expected depth 0, got %d\n", s2.GetDepth())
		os.Exit(1)
	}
	fmt.Printf("5. After 2nd pop: state=%s, depth=%d\n", s2.GetState(), s2.GetDepth())

	fmt.Println("PASS: Persist stack works correctly")
}
