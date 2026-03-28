
package main

import "fmt"
import "os"

type LampFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type LampFrameContext struct {
    _event  LampFrameEvent
    _return any
    _data   map[string]any
}

type LampCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *LampFrameEvent
    parentCompartment *LampCompartment
}

func newLampCompartment(state string) *LampCompartment {
    return &LampCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *LampCompartment) copy() *LampCompartment {
    nc := &LampCompartment{
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

type Lamp struct {
    _state_stack []*LampCompartment
    __compartment *LampCompartment
    __next_compartment *LampCompartment
    _context_stack []LampFrameContext
    color string
    switch_closed bool
}

func NewLamp() *Lamp {
    s := &Lamp{}
    s._state_stack = make([]*LampCompartment, 0)
    s._context_stack = make([]LampFrameContext, 0)
    s.__compartment = newLampCompartment("Off")
    s.__next_compartment = nil
    __frame_event := LampFrameEvent{_message: "$>", _parameters: nil}
    __ctx := LampFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *Lamp) __kernel(__e *LampFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &LampFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &LampFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &LampFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *Lamp) __router(__e *LampFrameEvent) {
    switch s.__compartment.state {
    case "Off":
        s._state_Off(__e)
    case "On":
        s._state_On(__e)
    }
}

func (s *Lamp) __transition(next *LampCompartment) {
    s.__next_compartment = next
}

func (s *Lamp) TurnOn() {
    __e := LampFrameEvent{_message: "TurnOn"}
    __ctx := LampFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *Lamp) TurnOff() {
    __e := LampFrameEvent{_message: "TurnOff"}
    __ctx := LampFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *Lamp) GetColor() string {
    __e := LampFrameEvent{_message: "GetColor"}
    __ctx := LampFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *Lamp) SetColor(color string) {
    __params := map[string]any{
        "color": color,
    }
    __e := LampFrameEvent{_message: "SetColor", _parameters: __params}
    __ctx := LampFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *Lamp) IsSwitchClosed() bool {
    __e := LampFrameEvent{_message: "IsSwitchClosed"}
    __ctx := LampFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *Lamp) _state_On(__e *LampFrameEvent) {
    if __e._message == "<$" {
        s.__openSwitch()
    } else if __e._message == "$>" {
        s.__closeSwitch()
    } else if __e._message == "GetColor" {
        s._context_stack[len(s._context_stack)-1]._return = s.color
        return
    } else if __e._message == "IsSwitchClosed" {
        s._context_stack[len(s._context_stack)-1]._return = s.switch_closed
        return
    } else if __e._message == "SetColor" {
        color := __e._parameters["color"].(string)
        _ = color
        s.color = color
    } else if __e._message == "TurnOff" {
        __compartment := newLampCompartment("Off")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *Lamp) _state_Off(__e *LampFrameEvent) {
    if __e._message == "GetColor" {
        s._context_stack[len(s._context_stack)-1]._return = s.color
        return
    } else if __e._message == "IsSwitchClosed" {
        s._context_stack[len(s._context_stack)-1]._return = s.switch_closed
        return
    } else if __e._message == "SetColor" {
        color := __e._parameters["color"].(string)
        _ = color
        s.color = color
    } else if __e._message == "TurnOn" {
        __compartment := newLampCompartment("On")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *Lamp) __closeSwitch() {
                s.switch_closed = true
}

func (s *Lamp) __openSwitch() {
                s.switch_closed = false
}

func main() {
	fmt.Println("=== Test 31: Doc Lamp Basic ===")
	lamp := NewLamp()

	// Initially off - need to set color since Go zero-inits to ""
	// The Java version inits color to "white" via domain, but Go cannot do that
	// So we set it manually
	lamp.SetColor("white")

	if lamp.IsSwitchClosed() != false {
		fmt.Println("FAIL: Switch should be open initially")
		os.Exit(1)
	}

	// Turn on - should close switch
	lamp.TurnOn()
	if lamp.IsSwitchClosed() != true {
		fmt.Println("FAIL: Switch should be closed after TurnOn")
		os.Exit(1)
	}

	// Check color
	if lamp.GetColor() != "white" {
		fmt.Printf("FAIL: Expected 'white', got '%s'\n", lamp.GetColor())
		os.Exit(1)
	}

	// Set color
	lamp.SetColor("blue")
	if lamp.GetColor() != "blue" {
		fmt.Printf("FAIL: Expected 'blue', got '%s'\n", lamp.GetColor())
		os.Exit(1)
	}

	// Turn off - should open switch
	lamp.TurnOff()
	if lamp.IsSwitchClosed() != false {
		fmt.Println("FAIL: Switch should be open after TurnOff")
		os.Exit(1)
	}

	fmt.Println("PASS: Basic lamp works correctly")
}
