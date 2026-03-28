
package main

import "fmt"
import "os"

type HSMEnterExitParamsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type HSMEnterExitParamsFrameContext struct {
    _event  HSMEnterExitParamsFrameEvent
    _return any
    _data   map[string]any
}

type HSMEnterExitParamsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *HSMEnterExitParamsFrameEvent
    parentCompartment *HSMEnterExitParamsCompartment
}

func newHSMEnterExitParamsCompartment(state string) *HSMEnterExitParamsCompartment {
    return &HSMEnterExitParamsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *HSMEnterExitParamsCompartment) copy() *HSMEnterExitParamsCompartment {
    nc := &HSMEnterExitParamsCompartment{
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

type HSMEnterExitParams struct {
    _state_stack []*HSMEnterExitParamsCompartment
    __compartment *HSMEnterExitParamsCompartment
    __next_compartment *HSMEnterExitParamsCompartment
    _context_stack []HSMEnterExitParamsFrameContext
    log []string
}

func NewHSMEnterExitParams() *HSMEnterExitParams {
    s := &HSMEnterExitParams{}
    s._state_stack = make([]*HSMEnterExitParamsCompartment, 0)
    s._context_stack = make([]HSMEnterExitParamsFrameContext, 0)
    s.__compartment = newHSMEnterExitParamsCompartment("Start")
    s.__next_compartment = nil
    __frame_event := HSMEnterExitParamsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := HSMEnterExitParamsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *HSMEnterExitParams) __kernel(__e *HSMEnterExitParamsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &HSMEnterExitParamsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &HSMEnterExitParamsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &HSMEnterExitParamsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *HSMEnterExitParams) __router(__e *HSMEnterExitParamsFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "ChildA":
        s._state_ChildA(__e)
    case "ChildB":
        s._state_ChildB(__e)
    case "Parent":
        s._state_Parent(__e)
    }
}

func (s *HSMEnterExitParams) __transition(next *HSMEnterExitParamsCompartment) {
    s.__next_compartment = next
}

func (s *HSMEnterExitParams) GoToA() {
    __e := HSMEnterExitParamsFrameEvent{_message: "GoToA"}
    __ctx := HSMEnterExitParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterExitParams) GoToSibling() {
    __e := HSMEnterExitParamsFrameEvent{_message: "GoToSibling"}
    __ctx := HSMEnterExitParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterExitParams) GoBack() {
    __e := HSMEnterExitParamsFrameEvent{_message: "GoBack"}
    __ctx := HSMEnterExitParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *HSMEnterExitParams) GetLog() []string {
    __e := HSMEnterExitParamsFrameEvent{_message: "GetLog"}
    __ctx := HSMEnterExitParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result []string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.([]string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterExitParams) GetState() string {
    __e := HSMEnterExitParamsFrameEvent{_message: "GetState"}
    __ctx := HSMEnterExitParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *HSMEnterExitParams) _state_ChildB(__e *HSMEnterExitParamsFrameEvent) {
    if __e._message == "<$" {
        reason := s.__compartment.exitArgs["0"].(string)
        _ = reason
        s.log = append(s.log, "ChildB:exit(" + reason + ")")
    } else if __e._message == "$>" {
        msg := s.__compartment.enterArgs["0"].(string)
        _ = msg
        s.log = append(s.log, "ChildB:enter(" + msg + ")")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "ChildB"
        return
    } else if __e._message == "GoBack" {
        s.__compartment.exitArgs["0"] = "leaving_B"
        __compartment := newHSMEnterExitParamsCompartment("ChildA")
        __compartment.parentCompartment = s.__compartment.copy()
        __compartment.enterArgs["0"] = "returning_A"
        s.__transition(__compartment)
        return
    }
}

func (s *HSMEnterExitParams) _state_Start(__e *HSMEnterExitParamsFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Start"
        return
    } else if __e._message == "GoToA" {
        __compartment := newHSMEnterExitParamsCompartment("ChildA")
        __compartment.parentCompartment = s.__compartment.copy()
        __compartment.enterArgs["0"] = "starting"
        s.__transition(__compartment)
        return
    }
}

func (s *HSMEnterExitParams) _state_Parent(__e *HSMEnterExitParamsFrameEvent) {
    if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Parent"
        return
    }
}

func (s *HSMEnterExitParams) _state_ChildA(__e *HSMEnterExitParamsFrameEvent) {
    if __e._message == "<$" {
        reason := s.__compartment.exitArgs["0"].(string)
        _ = reason
        s.log = append(s.log, "ChildA:exit(" + reason + ")")
    } else if __e._message == "$>" {
        msg := s.__compartment.enterArgs["0"].(string)
        _ = msg
        s.log = append(s.log, "ChildA:enter(" + msg + ")")
    } else if __e._message == "GetLog" {
        s._context_stack[len(s._context_stack)-1]._return = s.log
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "ChildA"
        return
    } else if __e._message == "GoToSibling" {
        s.__compartment.exitArgs["0"] = "leaving_A"
        __compartment := newHSMEnterExitParamsCompartment("ChildB")
        __compartment.parentCompartment = s.__compartment.copy()
        __compartment.enterArgs["0"] = "arriving_B"
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
	fmt.Println("=== Test 49: HSM Enter/Exit with Params ===")
	sm := NewHSMEnterExitParams()

	// First go to ChildA with enter params
	sm.GoToA()
	log := sm.GetLog()
	if !contains(log, "ChildA:enter(starting)") {
		fmt.Printf("FAIL: Expected ChildA:enter(starting), got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.5.0: Initial transition with enter params - PASS")

	// TC2.5.1: Exit params passed correctly
	sm.GoToSibling()
	log = sm.GetLog()
	if !contains(log, "ChildA:exit(leaving_A)") {
		fmt.Printf("FAIL: Expected exit with param, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.5.1: Exit params passed correctly - PASS")

	// TC2.5.2: Enter params passed to target state
	if !contains(log, "ChildB:enter(arriving_B)") {
		fmt.Printf("FAIL: Expected enter with param, got %v\n", log)
		os.Exit(1)
	}
	if sm.GetState() != "ChildB" {
		fmt.Printf("FAIL: Expected ChildB, got %s\n", sm.GetState())
		os.Exit(1)
	}
	fmt.Println("TC2.5.2: Enter params passed to target - PASS")

	// TC2.5.3: Return transition with different params
	sm.GoBack()
	log = sm.GetLog()
	if !contains(log, "ChildB:exit(leaving_B)") {
		fmt.Printf("FAIL: Expected ChildB exit, got %v\n", log)
		os.Exit(1)
	}
	if !contains(log, "ChildA:enter(returning_A)") {
		fmt.Printf("FAIL: Expected ChildA enter, got %v\n", log)
		os.Exit(1)
	}
	fmt.Println("TC2.5.3: Return transition with params - PASS")

	fmt.Println("PASS: HSM enter/exit with params works correctly")
}
