
package main

import "fmt"
import "os"

type WithParamsFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type WithParamsFrameContext struct {
    _event  WithParamsFrameEvent
    _return any
    _data   map[string]any
}

type WithParamsCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *WithParamsFrameEvent
    parentCompartment *WithParamsCompartment
}

func newWithParamsCompartment(state string) *WithParamsCompartment {
    return &WithParamsCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *WithParamsCompartment) copy() *WithParamsCompartment {
    nc := &WithParamsCompartment{
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

type WithParams struct {
    _state_stack []*WithParamsCompartment
    __compartment *WithParamsCompartment
    __next_compartment *WithParamsCompartment
    _context_stack []WithParamsFrameContext
    total int
}

func NewWithParams() *WithParams {
    s := &WithParams{}
    s._state_stack = make([]*WithParamsCompartment, 0)
    s._context_stack = make([]WithParamsFrameContext, 0)
    s.__compartment = newWithParamsCompartment("Idle")
    s.__next_compartment = nil
    __frame_event := WithParamsFrameEvent{_message: "$>", _parameters: nil}
    __ctx := WithParamsFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *WithParams) __kernel(__e *WithParamsFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &WithParamsFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &WithParamsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &WithParamsFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *WithParams) __router(__e *WithParamsFrameEvent) {
    switch s.__compartment.state {
    case "Idle":
        s._state_Idle(__e)
    case "Running":
        s._state_Running(__e)
    }
}

func (s *WithParams) __transition(next *WithParamsCompartment) {
    s.__next_compartment = next
}

func (s *WithParams) Start(initial int) {
    __params := map[string]any{
        "initial": initial,
    }
    __e := WithParamsFrameEvent{_message: "Start", _parameters: __params}
    __ctx := WithParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *WithParams) Add(value int) {
    __params := map[string]any{
        "value": value,
    }
    __e := WithParamsFrameEvent{_message: "Add", _parameters: __params}
    __ctx := WithParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *WithParams) Multiply(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := WithParamsFrameEvent{_message: "Multiply", _parameters: __params}
    __ctx := WithParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *WithParams) GetTotal() int {
    __e := WithParamsFrameEvent{_message: "GetTotal"}
    __ctx := WithParamsFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *WithParams) _state_Idle(__e *WithParamsFrameEvent) {
    if __e._message == "Add" {
        value := __e._parameters["value"].(int)
        _ = value
        fmt.Println("Cannot add in Idle state")
    } else if __e._message == "GetTotal" {
        s._context_stack[len(s._context_stack)-1]._return = s.total
        return
    } else if __e._message == "Multiply" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        s._context_stack[len(s._context_stack)-1]._return = 0
        return
    } else if __e._message == "Start" {
        initial := __e._parameters["initial"].(int)
        _ = initial
        s.total = initial
        fmt.Printf("Started with initial value: %d\n", initial)
        __compartment := newWithParamsCompartment("Running")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *WithParams) _state_Running(__e *WithParamsFrameEvent) {
    if __e._message == "Add" {
        value := __e._parameters["value"].(int)
        _ = value
        s.total += value
        fmt.Printf("Added %d, total is now %d\n", value, s.total)
    } else if __e._message == "GetTotal" {
        s._context_stack[len(s._context_stack)-1]._return = s.total
        return
    } else if __e._message == "Multiply" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        result := a * b
        s.total += result
        fmt.Printf("Multiplied %d * %d = %d, total is now %d\n", a, b, result, s.total)
        s._context_stack[len(s._context_stack)-1]._return = result
        return
    } else if __e._message == "Start" {
        initial := __e._parameters["initial"].(int)
        _ = initial
        fmt.Println("Already running")
    }
}

func main() {
	fmt.Println("=== Test 07: Handler Parameters ===")
	sm := NewWithParams()

	// Initial total should be 0
	total := sm.GetTotal()
	if total != 0 {
		fmt.Printf("FAIL: Expected initial total=0, got %d\n", total)
		os.Exit(1)
	}

	// Start with initial value
	sm.Start(100)
	total = sm.GetTotal()
	if total != 100 {
		fmt.Printf("FAIL: Expected total=100, got %d\n", total)
		os.Exit(1)
	}
	fmt.Printf("After Start(100): total = %d\n", total)

	// Add value
	sm.Add(25)
	total = sm.GetTotal()
	if total != 125 {
		fmt.Printf("FAIL: Expected total=125, got %d\n", total)
		os.Exit(1)
	}
	fmt.Printf("After Add(25): total = %d\n", total)

	// Multiply with two params
	result := sm.Multiply(3, 5)
	if result != 15 {
		fmt.Printf("FAIL: Expected multiply result=15, got %d\n", result)
		os.Exit(1)
	}
	total = sm.GetTotal()
	if total != 140 {
		fmt.Printf("FAIL: Expected total=140, got %d\n", total)
		os.Exit(1)
	}
	fmt.Printf("After Multiply(3,5): result = %d, total = %d\n", result, total)

	fmt.Println("PASS: Handler parameters work correctly")
}
