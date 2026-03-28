
package main

import "fmt"
import "os"

type OperationsTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type OperationsTestFrameContext struct {
    _event  OperationsTestFrameEvent
    _return any
    _data   map[string]any
}

type OperationsTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *OperationsTestFrameEvent
    parentCompartment *OperationsTestCompartment
}

func newOperationsTestCompartment(state string) *OperationsTestCompartment {
    return &OperationsTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *OperationsTestCompartment) copy() *OperationsTestCompartment {
    nc := &OperationsTestCompartment{
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

type OperationsTest struct {
    _state_stack []*OperationsTestCompartment
    __compartment *OperationsTestCompartment
    __next_compartment *OperationsTestCompartment
    _context_stack []OperationsTestFrameContext
    last_result int
}

func NewOperationsTest() *OperationsTest {
    s := &OperationsTest{}
    s._state_stack = make([]*OperationsTestCompartment, 0)
    s._context_stack = make([]OperationsTestFrameContext, 0)
    s.__compartment = newOperationsTestCompartment("Ready")
    s.__next_compartment = nil
    __frame_event := OperationsTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := OperationsTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *OperationsTest) __kernel(__e *OperationsTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &OperationsTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &OperationsTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &OperationsTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *OperationsTest) __router(__e *OperationsTestFrameEvent) {
    switch s.__compartment.state {
    case "Ready":
        s._state_Ready(__e)
    }
}

func (s *OperationsTest) __transition(next *OperationsTestCompartment) {
    s.__next_compartment = next
}

func (s *OperationsTest) Compute(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := OperationsTestFrameEvent{_message: "Compute", _parameters: __params}
    __ctx := OperationsTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *OperationsTest) GetLastResult() int {
    __e := OperationsTestFrameEvent{_message: "GetLastResult"}
    __ctx := OperationsTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *OperationsTest) _state_Ready(__e *OperationsTestFrameEvent) {
    if __e._message == "Compute" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        // Use instance operations
        sum_val := s.Add(a, b)
        prod_val := s.Multiply(a, b)
        last_result := sum_val + prod_val
        s._context_stack[len(s._context_stack)-1]._return = last_result
        return
    } else if __e._message == "GetLastResult" {
        s._context_stack[len(s._context_stack)-1]._return = s.last_result
        return
    }
}

func (s *OperationsTest) Add(x int, y int) int {
                return x + y
}

func (s *OperationsTest) Multiply(x int, y int) int {
                return x * y
}

func Factorial(n int) int {
                if n <= 1 {
                    return 1
                }
                return n * Factorial(n - 1)
}

func IsEven(n int) bool {
                return n % 2 == 0
}

func main() {
	fmt.Println("=== Test 22: Operations Basic (Go) ===")
	sm := NewOperationsTest()

	// Test 1: Instance operations
	result := sm.Add(3, 4)
	if result != 7 {
		fmt.Printf("FAIL: Expected 7, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("1. Add(3, 4) = %d\n", result)

	result = sm.Multiply(3, 4)
	if result != 12 {
		fmt.Printf("FAIL: Expected 12, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("2. Multiply(3, 4) = %d\n", result)

	// Test 2: Operations used in handler
	result = sm.Compute(3, 4)
	// compute returns Add(3,4) + Multiply(3,4) = 7 + 12 = 19
	if result != 19 {
		fmt.Printf("FAIL: Expected 19, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("3. Compute(3, 4) = %d\n", result)

	// Test 3: Static operations
	result = Factorial(5)
	if result != 120 {
		fmt.Printf("FAIL: Expected 120, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("4. Factorial(5) = %d\n", result)

	is_even := IsEven(4)
	if is_even != true {
		fmt.Printf("FAIL: Expected true, got %v\n", is_even)
		os.Exit(1)
	}
	fmt.Printf("5. IsEven(4) = %v\n", is_even)

	is_even = IsEven(7)
	if is_even != false {
		fmt.Printf("FAIL: Expected false, got %v\n", is_even)
		os.Exit(1)
	}
	fmt.Printf("6. IsEven(7) = %v\n", is_even)

	// Test 4: Static via package
	result = Factorial(4)
	if result != 24 {
		fmt.Printf("FAIL: Expected 24, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("7. Factorial(4) = %d\n", result)

	fmt.Println("PASS: Operations basic works correctly")
}
