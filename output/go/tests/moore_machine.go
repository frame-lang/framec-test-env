
package main

import "fmt"

// Moore Machine - output depends ONLY on state (output on entry)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

type MooreMachineFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type MooreMachineFrameContext struct {
    _event  MooreMachineFrameEvent
    _return any
    _data   map[string]any
}

type MooreMachineCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *MooreMachineFrameEvent
    parentCompartment *MooreMachineCompartment
}

func newMooreMachineCompartment(state string) *MooreMachineCompartment {
    return &MooreMachineCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *MooreMachineCompartment) copy() *MooreMachineCompartment {
    nc := &MooreMachineCompartment{
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

type MooreMachine struct {
    _state_stack []*MooreMachineCompartment
    __compartment *MooreMachineCompartment
    __next_compartment *MooreMachineCompartment
    _context_stack []MooreMachineFrameContext
    current_output int
}

func NewMooreMachine() *MooreMachine {
    s := &MooreMachine{}
    s._state_stack = make([]*MooreMachineCompartment, 0)
    s._context_stack = make([]MooreMachineFrameContext, 0)
    s.__compartment = newMooreMachineCompartment("Q0")
    s.__next_compartment = nil
    __frame_event := MooreMachineFrameEvent{_message: "$>", _parameters: nil}
    __ctx := MooreMachineFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *MooreMachine) __kernel(__e *MooreMachineFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &MooreMachineFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &MooreMachineFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &MooreMachineFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *MooreMachine) __router(__e *MooreMachineFrameEvent) {
    switch s.__compartment.state {
    case "Q0":
        s._state_Q0(__e)
    case "Q1":
        s._state_Q1(__e)
    case "Q2":
        s._state_Q2(__e)
    case "Q3":
        s._state_Q3(__e)
    case "Q4":
        s._state_Q4(__e)
    }
}

func (s *MooreMachine) __transition(next *MooreMachineCompartment) {
    s.__next_compartment = next
}

func (s *MooreMachine) I0() {
    __e := MooreMachineFrameEvent{_message: "I0"}
    __ctx := MooreMachineFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *MooreMachine) I1() {
    __e := MooreMachineFrameEvent{_message: "I1"}
    __ctx := MooreMachineFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *MooreMachine) _state_Q4(__e *MooreMachineFrameEvent) {
    if __e._message == "$>" {
        s.setOutput(1)
    } else if __e._message == "I0" {
        __compartment := newMooreMachineCompartment("Q1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        __compartment := newMooreMachineCompartment("Q3")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MooreMachine) _state_Q2(__e *MooreMachineFrameEvent) {
    if __e._message == "$>" {
        s.setOutput(0)
    } else if __e._message == "I0" {
        __compartment := newMooreMachineCompartment("Q4")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        __compartment := newMooreMachineCompartment("Q2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MooreMachine) _state_Q0(__e *MooreMachineFrameEvent) {
    if __e._message == "$>" {
        s.setOutput(0)
    } else if __e._message == "I0" {
        __compartment := newMooreMachineCompartment("Q1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        __compartment := newMooreMachineCompartment("Q2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MooreMachine) _state_Q1(__e *MooreMachineFrameEvent) {
    if __e._message == "$>" {
        s.setOutput(0)
    } else if __e._message == "I0" {
        __compartment := newMooreMachineCompartment("Q1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        __compartment := newMooreMachineCompartment("Q3")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MooreMachine) _state_Q3(__e *MooreMachineFrameEvent) {
    if __e._message == "$>" {
        s.setOutput(1)
    } else if __e._message == "I0" {
        __compartment := newMooreMachineCompartment("Q4")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "I1" {
        __compartment := newMooreMachineCompartment("Q2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *MooreMachine) setOutput(value int) {
                s.current_output = value
}

func (s *MooreMachine) GetOutput() int {
                return s.current_output
}

func main() {
	fmt.Println("TAP version 14")
	fmt.Println("1..5")

	m := NewMooreMachine()

	// Initial state Q0 has output 0
	if m.GetOutput() == 0 {
		fmt.Println("ok 1 - moore initial state Q0 has output 0")
	} else {
		fmt.Printf("not ok 1 - moore initial state Q0 has output 0 # got %v\n", m.GetOutput())
	}

	// i_0: Q0 -> Q1 (output 0)
	m.I0()
	if m.GetOutput() == 0 {
		fmt.Println("ok 2 - moore Q1 has output 0")
	} else {
		fmt.Printf("not ok 2 - moore Q1 has output 0 # got %v\n", m.GetOutput())
	}

	// i_1: Q1 -> Q3 (output 1)
	m.I1()
	if m.GetOutput() == 1 {
		fmt.Println("ok 3 - moore Q3 has output 1")
	} else {
		fmt.Printf("not ok 3 - moore Q3 has output 1 # got %v\n", m.GetOutput())
	}

	// i_0: Q3 -> Q4 (output 1)
	m.I0()
	if m.GetOutput() == 1 {
		fmt.Println("ok 4 - moore Q4 has output 1")
	} else {
		fmt.Printf("not ok 4 - moore Q4 has output 1 # got %v\n", m.GetOutput())
	}

	// i_0: Q4 -> Q1 (output 0)
	m.I0()
	if m.GetOutput() == 0 {
		fmt.Println("ok 5 - moore Q1 has output 0 again")
	} else {
		fmt.Printf("not ok 5 - moore Q1 has output 0 again # got %v\n", m.GetOutput())
	}

	fmt.Println("# PASS - Moore machine outputs depend ONLY on state")
}
