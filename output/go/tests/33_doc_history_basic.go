
package main

import "fmt"
import "os"

type HistoryBasicFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HistoryBasicFrameContext struct {
    _event  HistoryBasicFrameEvent
    _return any
    _data   map[string]any
}

type HistoryBasicCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HistoryBasicFrameEvent
    parentCompartment *HistoryBasicCompartment
}

func newHistoryBasicCompartment(state string) *HistoryBasicCompartment {
    return &HistoryBasicCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HistoryBasicCompartment) copy() *HistoryBasicCompartment {
    nc := &HistoryBasicCompartment{
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

type HistoryBasic struct {
    _state_stack []*HistoryBasicCompartment
    __compartment *HistoryBasicCompartment
    __next_compartment *HistoryBasicCompartment
    _context_stack []HistoryBasicFrameContext
}

func NewHistoryBasic() *HistoryBasic {
    s := &HistoryBasic{}
    s._state_stack = make([]*HistoryBasicCompartment, 0)
    s._context_stack = make([]HistoryBasicFrameContext, 0)
    s.__compartment = newHistoryBasicCompartment("A")
    s.__next_compartment = nil
    __frame_event := HistoryBasicFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HistoryBasicFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HistoryBasic) __kernel(__e *HistoryBasicFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HistoryBasicFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HistoryBasicFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HistoryBasicFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HistoryBasic) __router(__e *HistoryBasicFrameEvent) {
    switch s.__compartment.state {
    case "A":
        s._state_A(__e)
    case "B":
        s._state_B(__e)
    case "C":
        s._state_C(__e)
    }
}

func (s *HistoryBasic) __transition(next *HistoryBasicCompartment) {
    s.__next_compartment = next
}

func (s *HistoryBasic) GotoCFromA() {
    __e := HistoryBasicFrameEvent{_message: "GotoCFromA"}
    __ctx := HistoryBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryBasic) GotoCFromB() {
    __e := HistoryBasicFrameEvent{_message: "GotoCFromB"}
    __ctx := HistoryBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryBasic) GotoB() {
    __e := HistoryBasicFrameEvent{_message: "GotoB"}
    __ctx := HistoryBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryBasic) ReturnBack() {
    __e := HistoryBasicFrameEvent{_message: "ReturnBack"}
    __ctx := HistoryBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryBasic) GetState() string {
    __e := HistoryBasicFrameEvent{_message: "GetState"}
    __ctx := HistoryBasicFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HistoryBasic) _state_A(__e *HistoryBasicFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "A"
        return
    } else if __e._message == "GotoB" {
        __compartment := newHistoryBasicCompartment("B")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GotoCFromA" {
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newHistoryBasicCompartment("C")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HistoryBasic) _state_B(__e *HistoryBasicFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "B"
        return
    } else if __e._message == "GotoCFromB" {
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newHistoryBasicCompartment("C")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HistoryBasic) _state_C(__e *HistoryBasicFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "C"
        return
    } else if __e._message == "ReturnBack" {
        __popped := s._state_stack[len(s._state_stack)-1]
        s._state_stack = s._state_stack[:len(s._state_stack)-1]
        s.__transition(__popped)
        return
    }
}

func main() {
	fmt.Println("=== Test 33: Doc History Basic ===")
	h := NewHistoryBasic()

	// Start in A
	if h.GetState() != "A" {
		fmt.Printf("FAIL: Expected 'A', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go to C from A (push A)
	h.GotoCFromA()
	if h.GetState() != "C" {
		fmt.Printf("FAIL: Expected 'C', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Return back (pop to A)
	h.ReturnBack()
	if h.GetState() != "A" {
		fmt.Printf("FAIL: Expected 'A' after pop, got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Now go to B
	h.GotoB()
	if h.GetState() != "B" {
		fmt.Printf("FAIL: Expected 'B', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go to C from B (push B)
	h.GotoCFromB()
	if h.GetState() != "C" {
		fmt.Printf("FAIL: Expected 'C', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Return back (pop to B)
	h.ReturnBack()
	if h.GetState() != "B" {
		fmt.Printf("FAIL: Expected 'B' after pop, got '%s'\n", h.GetState())
		os.Exit(1)
	}

	fmt.Println("PASS: History push/pop works correctly")
}
