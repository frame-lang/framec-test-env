
package main

import "fmt"
import "os"

// Tests that @@:return follows "last writer wins" across transition lifecycle

type SystemReturnChainTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SystemReturnChainTestFrameContext struct {
    _event  SystemReturnChainTestFrameEvent
    _return any
    _data   map[string]any
}

type SystemReturnChainTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SystemReturnChainTestFrameEvent
    parentCompartment *SystemReturnChainTestCompartment
}

func newSystemReturnChainTestCompartment(state string) *SystemReturnChainTestCompartment {
    return &SystemReturnChainTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SystemReturnChainTestCompartment) copy() *SystemReturnChainTestCompartment {
    nc := &SystemReturnChainTestCompartment{
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

type SystemReturnChainTest struct {
    _state_stack []*SystemReturnChainTestCompartment
    __compartment *SystemReturnChainTestCompartment
    __next_compartment *SystemReturnChainTestCompartment
    _context_stack []SystemReturnChainTestFrameContext
}

func NewSystemReturnChainTest() *SystemReturnChainTest {
    s := &SystemReturnChainTest{}
    s._state_stack = make([]*SystemReturnChainTestCompartment, 0)
    s._context_stack = make([]SystemReturnChainTestFrameContext, 0)
    s.__compartment = newSystemReturnChainTestCompartment("Start")
    s.__next_compartment = nil
    __frame_event := SystemReturnChainTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SystemReturnChainTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *SystemReturnChainTest) __kernel(__e *SystemReturnChainTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SystemReturnChainTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SystemReturnChainTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SystemReturnChainTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *SystemReturnChainTest) __router(__e *SystemReturnChainTestFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "EnterSetter":
        s._state_EnterSetter(__e)
    case "BothSet":
        s._state_BothSet(__e)
    }
}

func (s *SystemReturnChainTest) __transition(next *SystemReturnChainTestCompartment) {
    s.__next_compartment = next
}

func (s *SystemReturnChainTest) TestEnterSets() string {
    __e := SystemReturnChainTestFrameEvent{_message: "TestEnterSets"}
    __ctx := SystemReturnChainTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnChainTest) TestExitThenEnter() string {
    __e := SystemReturnChainTestFrameEvent{_message: "TestExitThenEnter"}
    __ctx := SystemReturnChainTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnChainTest) GetState() string {
    __e := SystemReturnChainTestFrameEvent{_message: "GetState"}
    __ctx := SystemReturnChainTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnChainTest) _state_BothSet(__e *SystemReturnChainTestFrameEvent) {
    if __e._message == "$>" {
        s._context_stack[len(s._context_stack)-1]._return = "enter_wins"
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "BothSet"
        return
    }
}

func (s *SystemReturnChainTest) _state_Start(__e *SystemReturnChainTestFrameEvent) {
    if __e._message == "<$" {
        // Exit handler sets initial value
        s._context_stack[len(s._context_stack)-1]._return = "from_exit"
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Start"
        return
    } else if __e._message == "TestEnterSets" {
        __compartment := newSystemReturnChainTestCompartment("EnterSetter")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "TestExitThenEnter" {
        __compartment := newSystemReturnChainTestCompartment("BothSet")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *SystemReturnChainTest) _state_EnterSetter(__e *SystemReturnChainTestFrameEvent) {
    if __e._message == "$>" {
        // Enter handler sets return value
        s._context_stack[len(s._context_stack)-1]._return = "from_enter"
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "EnterSetter"
        return
    }
}

func main() {
	fmt.Println("=== Test 15: System Return Chain (Last Writer Wins) ===")

	// Test 1: Start exit + EnterSetter enter
	s1 := NewSystemReturnChainTest()
	result1 := s1.TestEnterSets()
	if result1 != "from_enter" {
		fmt.Printf("FAIL: Expected 'from_enter', got '%s'\n", result1)
		os.Exit(1)
	}
	state1 := s1.GetState()
	if state1 != "EnterSetter" {
		fmt.Printf("FAIL: Expected state 'EnterSetter'\n")
		os.Exit(1)
	}
	fmt.Printf("1. Exit set then enter set - enter wins: '%s'\n", result1)

	// Test 2: Both handlers set, enter wins
	s2 := NewSystemReturnChainTest()
	result2 := s2.TestExitThenEnter()
	if result2 != "enter_wins" {
		fmt.Printf("FAIL: Expected 'enter_wins', got '%s'\n", result2)
		os.Exit(1)
	}
	state2 := s2.GetState()
	if state2 != "BothSet" {
		fmt.Printf("FAIL: Expected state 'BothSet'\n")
		os.Exit(1)
	}
	fmt.Printf("2. Both set - enter wins: '%s'\n", result2)

	fmt.Println("PASS: System return chain (last writer wins) works correctly")
}
