
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type PersistRoundtripFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type PersistRoundtripFrameContext struct {
    _event  PersistRoundtripFrameEvent
    _return any
    _data   map[string]any
}

type PersistRoundtripCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *PersistRoundtripFrameEvent
    parentCompartment *PersistRoundtripCompartment
}

func newPersistRoundtripCompartment(state string) *PersistRoundtripCompartment {
    return &PersistRoundtripCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *PersistRoundtripCompartment) copy() *PersistRoundtripCompartment {
    nc := &PersistRoundtripCompartment{
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

type PersistRoundtrip struct {
    _state_stack []*PersistRoundtripCompartment
    __compartment *PersistRoundtripCompartment
    __next_compartment *PersistRoundtripCompartment
    _context_stack []PersistRoundtripFrameContext
    counter int
    mode string
}

func NewPersistRoundtrip() *PersistRoundtrip {
    s := &PersistRoundtrip{}
    s._state_stack = make([]*PersistRoundtripCompartment, 0)
    s._context_stack = make([]PersistRoundtripFrameContext, 0)
    s.__compartment = newPersistRoundtripCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := PersistRoundtripFrameEvent{_message: "$>", _parameters: nil}
    __ctx := PersistRoundtripFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *PersistRoundtrip) __kernel(__e *PersistRoundtripFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &PersistRoundtripFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &PersistRoundtripFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &PersistRoundtripFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *PersistRoundtrip) __router(__e *PersistRoundtripFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Active":
        s._state_Active(__e)
    }
}

func (s *PersistRoundtrip) __transition(next *PersistRoundtripCompartment) {
    s.__next_compartment = next
}

func (s *PersistRoundtrip) GoActive() {
    __e := PersistRoundtripFrameEvent{_message: "GoActive"}
    __ctx := PersistRoundtripFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistRoundtrip) GoIdle() {
    __e := PersistRoundtripFrameEvent{_message: "GoIdle"}
    __ctx := PersistRoundtripFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistRoundtrip) GetState() string {
    __e := PersistRoundtripFrameEvent{_message: "GetState"}
    __ctx := PersistRoundtripFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *PersistRoundtrip) SetCounter(n int) {
    __params := map[string]any{
        "n": n,
    }
    __e := PersistRoundtripFrameEvent{_message: "SetCounter", _parameters: __params}
    __ctx := PersistRoundtripFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *PersistRoundtrip) GetCounter() int {
    __e := PersistRoundtripFrameEvent{_message: "GetCounter"}
    __ctx := PersistRoundtripFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *PersistRoundtrip) _state_Idle(__e *PersistRoundtripFrameEvent) {
    if __e._message == "GetCounter" {
        s._context_stack[len(s._context_stack)-1]._return = s.counter
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "idle"
        return
    } else if __e._message == "GoActive" {
        __compartment := newPersistRoundtripCompartment("Active")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GoIdle" {
        // already idle
    } else if __e._message == "SetCounter" {
        n := __e._parameters["n"].(int)
        _ = n
        s.counter = n
    }
}

func (s *PersistRoundtrip) _state_Active(__e *PersistRoundtripFrameEvent) {
    if __e._message == "GetCounter" {
        s._context_stack[len(s._context_stack)-1]._return = s.counter
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "active"
        return
    } else if __e._message == "GoActive" {
        // already active
    } else if __e._message == "GoIdle" {
        __compartment := newPersistRoundtripCompartment("Idle")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "SetCounter" {
        n := __e._parameters["n"].(int)
        _ = n
        s.counter = n * 2
    }
}

// --- Persist helpers ---

type persistRoundtripSnapshot struct {
	State   string `json:"state"`
	Counter int    `json:"counter"`
	Mode    string `json:"mode"`
}

func savePersistRoundtrip(s *PersistRoundtrip) string {
	snap := persistRoundtripSnapshot{
		State:   s.__compartment.state,
		Counter: s.counter,
		Mode:    s.mode,
	}
	b, err := json.Marshal(snap)
	if err != nil {
		panic(err)
	}
	return string(b)
}

func restorePersistRoundtrip(jsonStr string) *PersistRoundtrip {
	var snap persistRoundtripSnapshot
	if err := json.Unmarshal([]byte(jsonStr), &snap); err != nil {
		panic(err)
	}
	s := &PersistRoundtrip{}
	s._state_stack = make([]*PersistRoundtripCompartment, 0)
	s._context_stack = make([]PersistRoundtripFrameContext, 0)
	s.__compartment = newPersistRoundtripCompartment(snap.State)
	s.__next_compartment = nil
	s.counter = snap.Counter
	s.mode = snap.Mode
	return s
}

func main() {
	fmt.Println("=== Test 24: Persist Roundtrip (Go) ===")

	// Test 1: Create system and build up state
	s1 := NewPersistRoundtrip()
	s1.SetCounter(5)
	s1.GoActive()
	s1.SetCounter(3) // Should be 6 in Active (doubled)

	if s1.GetState() != "active" {
		fmt.Printf("FAIL: Expected active, got %s\n", s1.GetState())
		os.Exit(1)
	}
	if s1.GetCounter() != 6 {
		fmt.Printf("FAIL: Expected 6, got %d\n", s1.GetCounter())
		os.Exit(1)
	}
	fmt.Printf("1. State before save: state=%s, counter=%d\n", s1.GetState(), s1.GetCounter())

	// Test 2: Save state
	data := savePersistRoundtrip(s1)
	fmt.Printf("2. Saved: %s\n", data)

	// Test 3: Restore to new instance
	s2 := restorePersistRoundtrip(data)

	// Verify restored state matches
	if s2.GetState() != "active" {
		fmt.Printf("FAIL: Expected active, got %s\n", s2.GetState())
		os.Exit(1)
	}
	if s2.GetCounter() != 6 {
		fmt.Printf("FAIL: Expected 6, got %d\n", s2.GetCounter())
		os.Exit(1)
	}
	fmt.Printf("3. Restored state: state=%s, counter=%d\n", s2.GetState(), s2.GetCounter())

	// Test 4: State machine continues to work after restore
	s2.SetCounter(2) // Should be 4 in Active (doubled)
	if s2.GetCounter() != 4 {
		fmt.Printf("FAIL: Expected 4, got %d\n", s2.GetCounter())
		os.Exit(1)
	}
	fmt.Printf("4. Counter after SetCounter(2): %d\n", s2.GetCounter())

	// Test 5: Transitions work after restore
	s2.GoIdle()
	if s2.GetState() != "idle" {
		fmt.Printf("FAIL: Expected idle after GoIdle\n")
		os.Exit(1)
	}
	s2.SetCounter(10) // Not doubled in Idle
	if s2.GetCounter() != 10 {
		fmt.Printf("FAIL: Expected 10, got %d\n", s2.GetCounter())
		os.Exit(1)
	}
	fmt.Printf("5. After GoIdle: state=%s, counter=%d\n", s2.GetState(), s2.GetCounter())

	fmt.Println("PASS: Persist roundtrip works correctly")
}
