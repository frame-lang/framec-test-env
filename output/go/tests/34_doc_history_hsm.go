
package main

import "fmt"
import "os"

type HistoryHSMFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HistoryHSMFrameContext struct {
    _event  HistoryHSMFrameEvent
    _return any
    _data   map[string]any
}

type HistoryHSMCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HistoryHSMFrameEvent
    parentCompartment *HistoryHSMCompartment
}

func newHistoryHSMCompartment(state string) *HistoryHSMCompartment {
    return &HistoryHSMCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HistoryHSMCompartment) copy() *HistoryHSMCompartment {
    nc := &HistoryHSMCompartment{
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

type HistoryHSM struct {
    _state_stack []*HistoryHSMCompartment
    __compartment *HistoryHSMCompartment
    __next_compartment *HistoryHSMCompartment
    _context_stack []HistoryHSMFrameContext
    log []string
}

func NewHistoryHSM() *HistoryHSM {
    s := &HistoryHSM{}
    s._state_stack = make([]*HistoryHSMCompartment, 0)
    s._context_stack = make([]HistoryHSMFrameContext, 0)
    s.__compartment = newHistoryHSMCompartment("Waiting")
    s.__next_compartment = nil
    __frame_event := HistoryHSMFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HistoryHSMFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HistoryHSM) __kernel(__e *HistoryHSMFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HistoryHSMFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HistoryHSMFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HistoryHSMFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HistoryHSM) __router(__e *HistoryHSMFrameEvent) {
    switch s.__compartment.state {
    case "Waiting":
        s._state_Waiting(__e)
    case "A":
        s._state_A(__e)
    case "B":
        s._state_B(__e)
    case "AB":
        s._state_AB(__e)
    case "C":
        s._state_C(__e)
    }
}

func (s *HistoryHSM) __transition(next *HistoryHSMCompartment) {
    s.__next_compartment = next
}

func (s *HistoryHSM) GotoA() {
    __e := HistoryHSMFrameEvent{_message: "GotoA"}
    __ctx := HistoryHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryHSM) GotoB() {
    __e := HistoryHSMFrameEvent{_message: "GotoB"}
    __ctx := HistoryHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryHSM) GotoC() {
    __e := HistoryHSMFrameEvent{_message: "GotoC"}
    __ctx := HistoryHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryHSM) GoBack() {
    __e := HistoryHSMFrameEvent{_message: "GoBack"}
    __ctx := HistoryHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HistoryHSM) GetState() string {
    __e := HistoryHSMFrameEvent{_message: "GetState"}
    __ctx := HistoryHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HistoryHSM) GetLog() []string {
    __e := HistoryHSMFrameEvent{_message: "GetLog"}
    __ctx := HistoryHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HistoryHSM) _state_B(__e *HistoryHSMFrameEvent) {
    if __e._message == "$>" {
        s.__log_msg("In $B")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "B"
        return
    } else if __e._message == "GotoA" {
        s.__log_msg("gotoA")
        __compartment := newHistoryHSMCompartment("A")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else {
        s._state_AB(__e)
    }
}

func (s *HistoryHSM) _state_AB(__e *HistoryHSMFrameEvent) {
    if __e._message == "GotoC" {
        s.__log_msg("gotoC in $AB")
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newHistoryHSMCompartment("C")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HistoryHSM) _state_C(__e *HistoryHSMFrameEvent) {
    if __e._message == "$>" {
        s.__log_msg("In $C")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "C"
        return
    } else if __e._message == "GoBack" {
        s.__log_msg("goBack")
        __popped := s._state_stack[len(s._state_stack)-1]
        s._state_stack = s._state_stack[:len(s._state_stack)-1]
        s.__transition(__popped)
        return
    }
}

func (s *HistoryHSM) _state_Waiting(__e *HistoryHSMFrameEvent) {
    if __e._message == "$>" {
        s.__log_msg("In $Waiting")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Waiting"
        return
    } else if __e._message == "GotoA" {
        s.__log_msg("gotoA")
        __compartment := newHistoryHSMCompartment("A")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GotoB" {
        s.__log_msg("gotoB")
        __compartment := newHistoryHSMCompartment("B")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *HistoryHSM) _state_A(__e *HistoryHSMFrameEvent) {
    if __e._message == "$>" {
        s.__log_msg("In $A")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "A"
        return
    } else if __e._message == "GotoB" {
        s.__log_msg("gotoB")
        __compartment := newHistoryHSMCompartment("B")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else {
        s._state_AB(__e)
    }
}

func (s *HistoryHSM) __log_msg(msg string) {
                s.log = append(s.log, msg)
}

func main() {
	fmt.Println("=== Test 34: Doc History HSM ===")
	h := NewHistoryHSM()

	// Start in Waiting
	if h.GetState() != "Waiting" {
		fmt.Printf("FAIL: Expected 'Waiting', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go to A
	h.GotoA()
	if h.GetState() != "A" {
		fmt.Printf("FAIL: Expected 'A', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go to C (using inherited GotoC from $AB)
	h.GotoC()
	if h.GetState() != "C" {
		fmt.Printf("FAIL: Expected 'C', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go back (should pop to A)
	h.GoBack()
	if h.GetState() != "A" {
		fmt.Printf("FAIL: Expected 'A' after GoBack, got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go to B
	h.GotoB()
	if h.GetState() != "B" {
		fmt.Printf("FAIL: Expected 'B', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go to C (again using inherited GotoC)
	h.GotoC()
	if h.GetState() != "C" {
		fmt.Printf("FAIL: Expected 'C', got '%s'\n", h.GetState())
		os.Exit(1)
	}

	// Go back (should pop to B)
	h.GoBack()
	if h.GetState() != "B" {
		fmt.Printf("FAIL: Expected 'B' after GoBack, got '%s'\n", h.GetState())
		os.Exit(1)
	}

	fmt.Printf("Log: %v\n", h.GetLog())
	fmt.Println("PASS: HSM with history works correctly")
}
