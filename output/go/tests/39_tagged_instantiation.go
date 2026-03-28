
package main

import "fmt"
import "os"

type CalculatorFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type CalculatorFrameContext struct {
    _event  CalculatorFrameEvent
    _return any
    _data   map[string]any
}

type CalculatorCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *CalculatorFrameEvent
    parentCompartment *CalculatorCompartment
}

func newCalculatorCompartment(state string) *CalculatorCompartment {
    return &CalculatorCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *CalculatorCompartment) copy() *CalculatorCompartment {
    nc := &CalculatorCompartment{
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

type Calculator struct {
    _state_stack []*CalculatorCompartment
    __compartment *CalculatorCompartment
    __next_compartment *CalculatorCompartment
    _context_stack []CalculatorFrameContext
    result int
}

func NewCalculator() *Calculator {
    s := &Calculator{}
    s._state_stack = make([]*CalculatorCompartment, 0)
    s._context_stack = make([]CalculatorFrameContext, 0)
    s.__compartment = newCalculatorCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := CalculatorFrameEvent{_message: "$>", _parameters: nil}
    __ctx := CalculatorFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *Calculator) __kernel(__e *CalculatorFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &CalculatorFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &CalculatorFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &CalculatorFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *Calculator) __router(__e *CalculatorFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *Calculator) __transition(next *CalculatorCompartment) {
    s.__next_compartment = next
}

func (s *Calculator) Add(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := CalculatorFrameEvent{_message: "Add", _parameters: __params}
    __ctx := CalculatorFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *Calculator) GetResult() int {
    __e := CalculatorFrameEvent{_message: "GetResult"}
    __ctx := CalculatorFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *Calculator) _state_Ready(__e *CalculatorFrameEvent) {
    if __e._message == "Add" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        s.result = a + b
        s._context_stack[len(s._context_stack)-1]._return = s.result
        return
    } else if __e._message == "GetResult" {
        s._context_stack[len(s._context_stack)-1]._return = s.result
        return
    }
}

type CounterFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type CounterFrameContext struct {
    _event  CounterFrameEvent
    _return any
    _data   map[string]any
}

type CounterCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *CounterFrameEvent
    parentCompartment *CounterCompartment
}

func newCounterCompartment(state string) *CounterCompartment {
    return &CounterCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *CounterCompartment) copy() *CounterCompartment {
    nc := &CounterCompartment{
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

type Counter struct {
    _state_stack []*CounterCompartment
    __compartment *CounterCompartment
    __next_compartment *CounterCompartment
    _context_stack []CounterFrameContext
    count int
}

func NewCounter() *Counter {
    s := &Counter{}
    s._state_stack = make([]*CounterCompartment, 0)
    s._context_stack = make([]CounterFrameContext, 0)
    s.__compartment = newCounterCompartment("Active")
    s.__next_compartment = nil
    __frame_event := CounterFrameEvent{_message: "$>", _parameters: nil}
    __ctx := CounterFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *Counter) __kernel(__e *CounterFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &CounterFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &CounterFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &CounterFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *Counter) __router(__e *CounterFrameEvent) {
    switch s.__compartment.state {
    case "Active":
        s._state_Active(__e)
    }
}

func (s *Counter) __transition(next *CounterCompartment) {
    s.__next_compartment = next
}

func (s *Counter) Increment() {
    __e := CounterFrameEvent{_message: "Increment"}
    __ctx := CounterFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *Counter) GetCount() int {
    __e := CounterFrameEvent{_message: "GetCount"}
    __ctx := CounterFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *Counter) _state_Active(__e *CounterFrameEvent) {
    if __e._message == "GetCount" {
        s._context_stack[len(s._context_stack)-1]._return = s.count
        return
    } else if __e._message == "Increment" {
        s.count = s.count + 1
    }
}

func main() {
	fmt.Println("=== Test 39: Tagged System Instantiation ===")

	// Tagged instantiation - validated at transpile time
	calc := NewCalculator()
	counter := NewCounter()

	// Test Calculator
	result := calc.Add(3, 4)
	if result != 7 {
		fmt.Printf("FAIL: Expected 7, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("Calculator.Add(3, 4) = %d\n", result)

	result = calc.GetResult()
	if result != 7 {
		fmt.Printf("FAIL: Expected 7, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("Calculator.GetResult() = %d\n", result)

	// Test Counter
	counter.Increment()
	counter.Increment()
	counter.Increment()
	count := counter.GetCount()
	if count != 3 {
		fmt.Printf("FAIL: Expected 3, got %d\n", count)
		os.Exit(1)
	}
	fmt.Printf("Counter after 3 increments: %d\n", count)

	fmt.Println("PASS: Tagged instantiation works correctly")
}
