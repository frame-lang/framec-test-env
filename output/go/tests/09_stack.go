
package main

import "fmt"
import "os"

type StackOpsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type StackOpsFrameContext struct {
    _event  StackOpsFrameEvent
    _return any
    _data   map[string]any
}

type StackOpsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *StackOpsFrameEvent
    parentCompartment *StackOpsCompartment
}

func newStackOpsCompartment(state string) *StackOpsCompartment {
    return &StackOpsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *StackOpsCompartment) copy() *StackOpsCompartment {
    nc := &StackOpsCompartment{
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

type StackOps struct {
    _state_stack []*StackOpsCompartment
    __compartment *StackOpsCompartment
    __next_compartment *StackOpsCompartment
    _context_stack []StackOpsFrameContext
}

func NewStackOps() *StackOps {
    s := &StackOps{}
    s._state_stack = make([]*StackOpsCompartment, 0)
    s._context_stack = make([]StackOpsFrameContext, 0)
    s.__compartment = newStackOpsCompartment("Main")
    s.__next_compartment = nil
    __frame_event := StackOpsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := StackOpsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *StackOps) __kernel(__e *StackOpsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &StackOpsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &StackOpsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &StackOpsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *StackOps) __router(__e *StackOpsFrameEvent) {
    switch s.__compartment.state {
    case "Main":
        s._state_Main(__e)
    case "Sub":
        s._state_Sub(__e)
    }
}

func (s *StackOps) __transition(next *StackOpsCompartment) {
    s.__next_compartment = next
}

func (s *StackOps) PushAndGo() {
    __e := StackOpsFrameEvent{_message: "PushAndGo"}
    __ctx := StackOpsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StackOps) PopBack() {
    __e := StackOpsFrameEvent{_message: "PopBack"}
    __ctx := StackOpsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *StackOps) DoWork() string {
    __e := StackOpsFrameEvent{_message: "DoWork"}
    __ctx := StackOpsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StackOps) GetState() string {
    __e := StackOpsFrameEvent{_message: "GetState"}
    __ctx := StackOpsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *StackOps) _state_Main(__e *StackOpsFrameEvent) {
    if __e._message == "DoWork" {
        s._context_stack[len(s._context_stack)-1]._return = "Working in Main"
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Main"
        return
    } else if __e._message == "PopBack" {
        fmt.Println("Cannot pop - nothing on stack in Main")
    } else if __e._message == "PushAndGo" {
        fmt.Println("Pushing Main to stack, going to Sub")
        s._state_stack = append(s._state_stack, s.__compartment.copy())
        __compartment := newStackOpsCompartment("Sub")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *StackOps) _state_Sub(__e *StackOpsFrameEvent) {
    if __e._message == "DoWork" {
        s._context_stack[len(s._context_stack)-1]._return = "Working in Sub"
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Sub"
        return
    } else if __e._message == "PopBack" {
        fmt.Println("Popping back to previous state")
        __popped := s._state_stack[len(s._state_stack)-1]
        s._state_stack = s._state_stack[:len(s._state_stack)-1]
        s.__transition(__popped)
        return
    } else if __e._message == "PushAndGo" {
        fmt.Println("Already in Sub")
    }
}

func main() {
	fmt.Println("=== Test 09: Stack Push/Pop ===")
	sm := NewStackOps()

	// Initial state should be Main
	state := sm.GetState()
	if state != "Main" {
		fmt.Printf("FAIL: Expected 'Main', got '%s'\n", state)
		os.Exit(1)
	}
	fmt.Printf("Initial state: %s\n", state)

	// Do work in Main
	work := sm.DoWork()
	if work != "Working in Main" {
		fmt.Printf("FAIL: Expected 'Working in Main', got '%s'\n", work)
		os.Exit(1)
	}
	fmt.Printf("DoWork(): %s\n", work)

	// Push and go to Sub
	sm.PushAndGo()
	state = sm.GetState()
	if state != "Sub" {
		fmt.Printf("FAIL: Expected 'Sub', got '%s'\n", state)
		os.Exit(1)
	}
	fmt.Printf("After PushAndGo(): %s\n", state)

	// Do work in Sub
	work = sm.DoWork()
	if work != "Working in Sub" {
		fmt.Printf("FAIL: Expected 'Working in Sub', got '%s'\n", work)
		os.Exit(1)
	}
	fmt.Printf("DoWork(): %s\n", work)

	// Pop back to Main
	sm.PopBack()
	state = sm.GetState()
	if state != "Main" {
		fmt.Printf("FAIL: Expected 'Main' after pop, got '%s'\n", state)
		os.Exit(1)
	}
	fmt.Printf("After PopBack(): %s\n", state)

	fmt.Println("PASS: Stack push/pop works correctly")
}
