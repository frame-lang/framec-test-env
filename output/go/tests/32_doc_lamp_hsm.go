
package main

import "fmt"
import "os"

type LampHSMFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type LampHSMFrameContext struct {
    _event  LampHSMFrameEvent
    _return any
    _data   map[string]any
}

type LampHSMCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *LampHSMFrameEvent
    parentCompartment *LampHSMCompartment
}

func newLampHSMCompartment(state string) *LampHSMCompartment {
    return &LampHSMCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *LampHSMCompartment) copy() *LampHSMCompartment {
    nc := &LampHSMCompartment{
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

type LampHSM struct {
    _state_stack []*LampHSMCompartment
    __compartment *LampHSMCompartment
    __next_compartment *LampHSMCompartment
    _context_stack []LampHSMFrameContext
    color string
    lamp_on bool
}

func NewLampHSM() *LampHSM {
    s := &LampHSM{}
    s._state_stack = make([]*LampHSMCompartment, 0)
    s._context_stack = make([]LampHSMFrameContext, 0)
    // HSM: Create parent compartment chain
    __parent_comp_0 := newLampHSMCompartment("ColorBehavior")
    __parent_comp_0.parentCompartment = nil
    s.__compartment = newLampHSMCompartment("Off")
    s.__compartment.parentCompartment = __parent_comp_0
    s.__next_compartment = nil
    __frame_event := LampHSMFrameEvent{_message: "$>", _parameters: nil}
    __ctx := LampHSMFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *LampHSM) __kernel(__e *LampHSMFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &LampHSMFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &LampHSMFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &LampHSMFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *LampHSM) __router(__e *LampHSMFrameEvent) {
    switch s.__compartment.state {
    case "Off":
        s._state_Off(__e)
    case "On":
        s._state_On(__e)
    case "ColorBehavior":
        s._state_ColorBehavior(__e)
    }
}

func (s *LampHSM) __transition(next *LampHSMCompartment) {
    s.__next_compartment = next
}

func (s *LampHSM) TurnOn() {
    __e := LampHSMFrameEvent{_message: "TurnOn"}
    __ctx := LampHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *LampHSM) TurnOff() {
    __e := LampHSMFrameEvent{_message: "TurnOff"}
    __ctx := LampHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *LampHSM) GetColor() string {
    __e := LampHSMFrameEvent{_message: "GetColor"}
    __ctx := LampHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *LampHSM) SetColor(color string) {
    __params := map[string]any{
        "color": color,
    }
    __e := LampHSMFrameEvent{_message: "SetColor", _parameters: __params}
    __ctx := LampHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *LampHSM) IsLampOn() bool {
    __e := LampHSMFrameEvent{_message: "IsLampOn"}
    __ctx := LampHSMFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *LampHSM) _state_On(__e *LampHSMFrameEvent) {
    if __e._message == "<$" {
        s.__turnOffLamp()
    } else if __e._message == "$>" {
        s.__turnOnLamp()
    } else if __e._message == "IsLampOn" {
        s._context_stack[len(s._context_stack)-1]._return = s.lamp_on
        return
    } else if __e._message == "TurnOff" {
        __compartment := newLampHSMCompartment("Off")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else {
        s._state_ColorBehavior(__e)
    }
}

func (s *LampHSM) _state_ColorBehavior(__e *LampHSMFrameEvent) {
    if __e._message == "GetColor" {
        s._context_stack[len(s._context_stack)-1]._return = s.color
        return
    } else if __e._message == "SetColor" {
        color := __e._parameters["color"].(string)
        _ = color
        s.color = color
    }
}

func (s *LampHSM) _state_Off(__e *LampHSMFrameEvent) {
    if __e._message == "IsLampOn" {
        s._context_stack[len(s._context_stack)-1]._return = s.lamp_on
        return
    } else if __e._message == "TurnOn" {
        __compartment := newLampHSMCompartment("On")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else {
        s._state_ColorBehavior(__e)
    }
}

func (s *LampHSM) __turnOnLamp() {
                s.lamp_on = true
}

func (s *LampHSM) __turnOffLamp() {
                s.lamp_on = false
}

func main() {
	fmt.Println("=== Test 32: Doc Lamp HSM ===")
	lamp := NewLampHSM()

	// Set initial color since Go zero-inits to ""
	lamp.SetColor("white")

	// Color behavior available in both states
	if lamp.GetColor() != "white" {
		fmt.Printf("FAIL: Expected 'white', got '%s'\n", lamp.GetColor())
		os.Exit(1)
	}
	lamp.SetColor("red")
	if lamp.GetColor() != "red" {
		fmt.Printf("FAIL: Expected 'red', got '%s'\n", lamp.GetColor())
		os.Exit(1)
	}

	// Turn on
	lamp.TurnOn()
	if lamp.IsLampOn() != true {
		fmt.Println("FAIL: Lamp should be on")
		os.Exit(1)
	}

	// Color still works when on
	lamp.SetColor("green")
	if lamp.GetColor() != "green" {
		fmt.Printf("FAIL: Expected 'green', got '%s'\n", lamp.GetColor())
		os.Exit(1)
	}

	// Turn off
	lamp.TurnOff()
	if lamp.IsLampOn() != false {
		fmt.Println("FAIL: Lamp should be off")
		os.Exit(1)
	}

	// Color still works when off
	if lamp.GetColor() != "green" {
		fmt.Printf("FAIL: Expected 'green', got '%s'\n", lamp.GetColor())
		os.Exit(1)
	}

	fmt.Println("PASS: HSM lamp works correctly")
}
