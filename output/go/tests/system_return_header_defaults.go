
package main

import (
	"fmt"
	"os"
)

// capability: @@:return header defaults and handler returns (Go).

type SystemReturnHeaderDefaultsGoFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SystemReturnHeaderDefaultsGoFrameContext struct {
    _event  SystemReturnHeaderDefaultsGoFrameEvent
    _return any
    _data   map[string]any
}

type SystemReturnHeaderDefaultsGoCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SystemReturnHeaderDefaultsGoFrameEvent
    parentCompartment *SystemReturnHeaderDefaultsGoCompartment
}

func newSystemReturnHeaderDefaultsGoCompartment(state string) *SystemReturnHeaderDefaultsGoCompartment {
    return &SystemReturnHeaderDefaultsGoCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SystemReturnHeaderDefaultsGoCompartment) copy() *SystemReturnHeaderDefaultsGoCompartment {
    nc := &SystemReturnHeaderDefaultsGoCompartment{
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

type SystemReturnHeaderDefaultsGo struct {
    _state_stack []*SystemReturnHeaderDefaultsGoCompartment
    __compartment *SystemReturnHeaderDefaultsGoCompartment
    __next_compartment *SystemReturnHeaderDefaultsGoCompartment
    _context_stack []SystemReturnHeaderDefaultsGoFrameContext
    x int
}

func NewSystemReturnHeaderDefaultsGo() *SystemReturnHeaderDefaultsGo {
    s := &SystemReturnHeaderDefaultsGo{}
    s._state_stack = make([]*SystemReturnHeaderDefaultsGoCompartment, 0)
    s._context_stack = make([]SystemReturnHeaderDefaultsGoFrameContext, 0)
    s.__compartment = newSystemReturnHeaderDefaultsGoCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := SystemReturnHeaderDefaultsGoFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SystemReturnHeaderDefaultsGoFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *SystemReturnHeaderDefaultsGo) __kernel(__e *SystemReturnHeaderDefaultsGoFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SystemReturnHeaderDefaultsGoFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SystemReturnHeaderDefaultsGoFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SystemReturnHeaderDefaultsGoFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *SystemReturnHeaderDefaultsGo) __router(__e *SystemReturnHeaderDefaultsGoFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    }
}

func (s *SystemReturnHeaderDefaultsGo) __transition(next *SystemReturnHeaderDefaultsGoCompartment) {
    s.__next_compartment = next
}

func (s *SystemReturnHeaderDefaultsGo) A1() int {
    __e := SystemReturnHeaderDefaultsGoFrameEvent{_message: "A1"}
    __ctx := SystemReturnHeaderDefaultsGoFrameContext{_event: __e, _return: 10, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnHeaderDefaultsGo) A2(a int) int {
    __params := map[string]any{
        "a": a,
    }
    __e := SystemReturnHeaderDefaultsGoFrameEvent{_message: "A2", _parameters: __params}
    __ctx := SystemReturnHeaderDefaultsGoFrameContext{_event: __e, _return: a, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnHeaderDefaultsGo) A3(a int) int {
    __params := map[string]any{
        "a": a,
    }
    __e := SystemReturnHeaderDefaultsGoFrameEvent{_message: "A3", _parameters: __params}
    __ctx := SystemReturnHeaderDefaultsGoFrameContext{_event: __e, _return: s.x + a, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnHeaderDefaultsGo) _state_Idle(__e *SystemReturnHeaderDefaultsGoFrameEvent) {
    if __e._message == "$>" {
        s.x = 3
    } else if __e._message == "A1" {
        if s.x < 5 {
            return
        } else {
            s._context_stack[len(s._context_stack)-1]._return = 0
            return
        }
    } else if __e._message == "A2" {
        a := __e._parameters["a"].(int)
        _ = a
        return
    } else if __e._message == "A3" {
        a := __e._parameters["a"].(int)
        _ = a
        s._context_stack[len(s._context_stack)-1]._return = a
        return
    }
}

func (s *SystemReturnHeaderDefaultsGo) bumpX(delta int) {
                s.x = s.x + delta
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..1")
	s := NewSystemReturnHeaderDefaultsGo()
	if s.A1() != 10 {
		fmt.Println("not ok 1 # a1 failed")
		os.Exit(1)
	}
	if s.A2(42) != 42 {
		fmt.Println("not ok 1 # a2 failed")
		os.Exit(1)
	}
	if s.A3(7) != 7 {
		fmt.Println("not ok 1 # a3 failed")
		os.Exit(1)
	}
	fmt.Println("ok 1 - system_return_header_defaults")
}
