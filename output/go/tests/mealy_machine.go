
package main

import "fmt"

// Mealy Machine - output depends on state AND input (output on transitions)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

type MealyMachineFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type MealyMachineFrameContext struct {
    _event  MealyMachineFrameEvent
    _return any
    _data   map[string]any
}

type MealyMachineCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *MealyMachineFrameEvent
    parentCompartment *MealyMachineCompartment
}

func newMealyMachineCompartment(state string) *MealyMachineCompartment {
    return &MealyMachineCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *MealyMachineCompartment) copy() *MealyMachineCompartment {
    nc := &MealyMachineCompartment{
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

type MealyMachine struct {
    _state_stack []*MealyMachineCompartment
    __compartment *MealyMachineCompartment
    __next_compartment *MealyMachineCompartment
    _context_stack []MealyMachineFrameContext
    last_output int
}

func NewMealyMachine() *MealyMachine {
    s := &MealyMachine{}
    s._state_stack = make([]*MealyMachineCompartment, 0)
    s._context_stack = make([]MealyMachineFrameContext, 0)
    s.__compartment = newMealyMachineCompartment("Q0")
    s.__next_compartment = nil
    __frame_event := MealyMachineFrameEvent{_message: "$>", _parameters: nil}
    __ctx := MealyMachineFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *MealyMachine) __kernel(__e *MealyMachineFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &MealyMachineFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &MealyMachineFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &MealyMachineFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *MealyMachine) __router(__e *MealyMachineFrameEvent) {
    switch s.__compartment.state {
    case "Q0":
        s._state_Q0(__e)
    case "Q1":
        s._state_Q1(__e)
    case "Q2":
        s._state_Q2(__e)
    }
}

func (s *MealyMachine) __transition(next *MealyMachineCompartment) {
    s.__next_compartment = next
}

func (s *MealyMachine) I0() {
    __e := MealyMachineFrameEvent{_message: "I0"}
    __ctx := MealyMachineFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *MealyMachine) I1() {
    __e := MealyMachineFrameEvent{_message: "I1"}
    __ctx := MealyMachineFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *MealyMachine) _state_Q0(__e *MealyMachineFrameEvent) {
    if __e._message == "I0" {
        s.emitOutput(0)
        __compartment := newMealyMachineCompartment("Q1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        s.emitOutput(0)
        __compartment := newMealyMachineCompartment("Q2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MealyMachine) _state_Q2(__e *MealyMachineFrameEvent) {
    if __e._message == "I0" {
        s.emitOutput(1)
        __compartment := newMealyMachineCompartment("Q1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        s.emitOutput(0)
        __compartment := newMealyMachineCompartment("Q2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MealyMachine) _state_Q1(__e *MealyMachineFrameEvent) {
    if __e._message == "I0" {
        s.emitOutput(0)
        __compartment := newMealyMachineCompartment("Q1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        s.emitOutput(1)
        __compartment := newMealyMachineCompartment("Q2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MealyMachine) emitOutput(value int) {
                s.last_output = value
}

func (s *MealyMachine) GetLastOutput() int {
                return s.last_output
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..4")

	m := NewMealyMachine()

	m.I0() // Q0 -> Q1, output 0
	if m.GetLastOutput() == 0 {
		fmt.Println("ok 1 - mealy i_0 from Q0 outputs 0")
	} else {
		fmt.Printf("not ok 1 - mealy i_0 from Q0 outputs 0 # got %v\n", m.GetLastOutput())
	}

	m.I0() // Q1 -> Q1, output 0
	if m.GetLastOutput() == 0 {
		fmt.Println("ok 2 - mealy i_0 from Q1 outputs 0")
	} else {
		fmt.Printf("not ok 2 - mealy i_0 from Q1 outputs 0 # got %v\n", m.GetLastOutput())
	}

	m.I1() // Q1 -> Q2, output 1
	if m.GetLastOutput() == 1 {
		fmt.Println("ok 3 - mealy i_1 from Q1 outputs 1")
	} else {
		fmt.Printf("not ok 3 - mealy i_1 from Q1 outputs 1 # got %v\n", m.GetLastOutput())
	}

	m.I0() // Q2 -> Q1, output 1
	if m.GetLastOutput() == 1 {
		fmt.Println("ok 4 - mealy i_0 from Q2 outputs 1")
	} else {
		fmt.Printf("not ok 4 - mealy i_0 from Q2 outputs 1 # got %v\n", m.GetLastOutput())
	}

	fmt.Println("# PASS - Mealy machine outputs depend on state AND input")
}
