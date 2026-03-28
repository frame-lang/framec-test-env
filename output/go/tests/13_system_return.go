
package main

import "fmt"
import "os"

type SystemReturnTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type SystemReturnTestFrameContext struct {
    _event  SystemReturnTestFrameEvent
    _return any
    _data   map[string]any
}

type SystemReturnTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *SystemReturnTestFrameEvent
    parentCompartment *SystemReturnTestCompartment
}

func newSystemReturnTestCompartment(state string) *SystemReturnTestCompartment {
    return &SystemReturnTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *SystemReturnTestCompartment) copy() *SystemReturnTestCompartment {
    nc := &SystemReturnTestCompartment{
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

type SystemReturnTest struct {
    _state_stack []*SystemReturnTestCompartment
    __compartment *SystemReturnTestCompartment
    __next_compartment *SystemReturnTestCompartment
    _context_stack []SystemReturnTestFrameContext
}

func NewSystemReturnTest() *SystemReturnTest {
    s := &SystemReturnTest{}
    s._state_stack = make([]*SystemReturnTestCompartment, 0)
    s._context_stack = make([]SystemReturnTestFrameContext, 0)
    s.__compartment = newSystemReturnTestCompartment("Calculator")
    s.__next_compartment = nil
    __frame_event := SystemReturnTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := SystemReturnTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *SystemReturnTest) __kernel(__e *SystemReturnTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &SystemReturnTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &SystemReturnTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &SystemReturnTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *SystemReturnTest) __router(__e *SystemReturnTestFrameEvent) {
    switch s.__compartment.state {
    case "Calculator":
        s._state_Calculator(__e)
    }
}

func (s *SystemReturnTest) __transition(next *SystemReturnTestCompartment) {
    s.__next_compartment = next
}

func (s *SystemReturnTest) Add(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := SystemReturnTestFrameEvent{_message: "Add", _parameters: __params}
    __ctx := SystemReturnTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnTest) Multiply(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := SystemReturnTestFrameEvent{_message: "Multiply", _parameters: __params}
    __ctx := SystemReturnTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnTest) Greet(name string) string {
    __params := map[string]any{
        "name": name,
    }
    __e := SystemReturnTestFrameEvent{_message: "Greet", _parameters: __params}
    __ctx := SystemReturnTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnTest) GetValue() int {
    __e := SystemReturnTestFrameEvent{_message: "GetValue"}
    __ctx := SystemReturnTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *SystemReturnTest) _state_Calculator(__e *SystemReturnTestFrameEvent) {
    __sv_comp := s.__compartment
    for __sv_comp != nil && __sv_comp.state != "Calculator" { __sv_comp = __sv_comp.parentCompartment }
    if __e._message == "$>" {
        if _, ok := __sv_comp.stateVars["value"]; !ok {
            __sv_comp.stateVars["value"] = 0
        }
    } else if __e._message == "Add" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        s._context_stack[len(s._context_stack)-1]._return = a + b
        return
    } else if __e._message == "GetValue" {
        __sv_comp.stateVars["value"] = 42
        s._context_stack[len(s._context_stack)-1]._return = __sv_comp.stateVars["value"].(int)
        return
    } else if __e._message == "Greet" {
        name := __e._parameters["name"].(string)
        _ = name
        s._context_stack[len(s._context_stack)-1]._return = "Hello, " + name + "!"
        return
    } else if __e._message == "Multiply" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        s._context_stack[len(s._context_stack)-1]._return = a * b
    }
}

func main() {
	fmt.Println("=== Test 13: System Return ===")
	calc := NewSystemReturnTest()

	// Test return sugar
	result := calc.Add(3, 5)
	if result != 8 {
		fmt.Printf("FAIL: Expected 8, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("Add(3, 5) = %d\n", result)

	// Test @@:return = expr
	result = calc.Multiply(4, 7)
	if result != 28 {
		fmt.Printf("FAIL: Expected 28, got %d\n", result)
		os.Exit(1)
	}
	fmt.Printf("Multiply(4, 7) = %d\n", result)

	// Test string return
	greeting := calc.Greet("World")
	if greeting != "Hello, World!" {
		fmt.Printf("FAIL: Expected 'Hello, World!', got '%s'\n", greeting)
		os.Exit(1)
	}
	fmt.Printf("Greet('World') = %s\n", greeting)

	// Test return with state variable
	value := calc.GetValue()
	if value != 42 {
		fmt.Printf("FAIL: Expected 42, got %d\n", value)
		os.Exit(1)
	}
	fmt.Printf("GetValue() = %d\n", value)

	fmt.Println("PASS: System return works correctly")
}
