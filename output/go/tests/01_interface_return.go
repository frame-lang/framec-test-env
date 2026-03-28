
package main

import "fmt"
import "os"

// =============================================================================
// Test 01: Interface Return
// =============================================================================
// Validates that event handler returns work correctly via the context stack.
// Tests both syntaxes:
//   - return value     (sugar - expands to @@:return = value)
//   - @@:return = value (explicit context assignment)
// =============================================================================

type InterfaceReturnFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type InterfaceReturnFrameContext struct {
    _event  InterfaceReturnFrameEvent
    _return any
    _data   map[string]any
}

type InterfaceReturnCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *InterfaceReturnFrameEvent
    parentCompartment *InterfaceReturnCompartment
}

func newInterfaceReturnCompartment(state string) *InterfaceReturnCompartment {
    return &InterfaceReturnCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *InterfaceReturnCompartment) copy() *InterfaceReturnCompartment {
    nc := &InterfaceReturnCompartment{
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

type InterfaceReturn struct {
    _state_stack []*InterfaceReturnCompartment
    __compartment *InterfaceReturnCompartment
    __next_compartment *InterfaceReturnCompartment
    _context_stack []InterfaceReturnFrameContext
}

func NewInterfaceReturn() *InterfaceReturn {
    s := &InterfaceReturn{}
    s._state_stack = make([]*InterfaceReturnCompartment, 0)
    s._context_stack = make([]InterfaceReturnFrameContext, 0)
    s.__compartment = newInterfaceReturnCompartment("Active")
    s.__next_compartment = nil
    __frame_event := InterfaceReturnFrameEvent{_message: "$>", _parameters: nil}
    __ctx := InterfaceReturnFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *InterfaceReturn) __kernel(__e *InterfaceReturnFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &InterfaceReturnFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &InterfaceReturnFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &InterfaceReturnFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *InterfaceReturn) __router(__e *InterfaceReturnFrameEvent) {
    switch s.__compartment.state {
    case "Active":
        s._state_Active(__e)
    }
}

func (s *InterfaceReturn) __transition(next *InterfaceReturnCompartment) {
    s.__next_compartment = next
}

func (s *InterfaceReturn) BoolReturn() bool {
    __e := InterfaceReturnFrameEvent{_message: "BoolReturn"}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) IntReturn() int {
    __e := InterfaceReturnFrameEvent{_message: "IntReturn"}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) StringReturn() string {
    __e := InterfaceReturnFrameEvent{_message: "StringReturn"}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) ConditionalReturn(x int) string {
    __params := map[string]any{
        "x": x,
    }
    __e := InterfaceReturnFrameEvent{_message: "ConditionalReturn", _parameters: __params}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) ComputedReturn(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := InterfaceReturnFrameEvent{_message: "ComputedReturn", _parameters: __params}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) ExplicitBool() bool {
    __e := InterfaceReturnFrameEvent{_message: "ExplicitBool"}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result bool
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(bool) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) ExplicitInt() int {
    __e := InterfaceReturnFrameEvent{_message: "ExplicitInt"}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) ExplicitString() string {
    __e := InterfaceReturnFrameEvent{_message: "ExplicitString"}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) ExplicitConditional(x int) string {
    __params := map[string]any{
        "x": x,
    }
    __e := InterfaceReturnFrameEvent{_message: "ExplicitConditional", _parameters: __params}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) ExplicitComputed(a int, b int) int {
    __params := map[string]any{
        "a": a,
        "b": b,
    }
    __e := InterfaceReturnFrameEvent{_message: "ExplicitComputed", _parameters: __params}
    __ctx := InterfaceReturnFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result int
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(int) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *InterfaceReturn) _state_Active(__e *InterfaceReturnFrameEvent) {
    if __e._message == "BoolReturn" {
        s._context_stack[len(s._context_stack)-1]._return = true
        return
    } else if __e._message == "ComputedReturn" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        result := a * b + 10
        s._context_stack[len(s._context_stack)-1]._return = result
        return
    } else if __e._message == "ConditionalReturn" {
        x := __e._parameters["x"].(int)
        _ = x
        if x < 0 {
            s._context_stack[len(s._context_stack)-1]._return = "negative"
            return
        } else if x == 0 {
            s._context_stack[len(s._context_stack)-1]._return = "zero"
            return
        } else {
            s._context_stack[len(s._context_stack)-1]._return = "positive"
            return
        }
    } else if __e._message == "ExplicitBool" {
        s._context_stack[len(s._context_stack)-1]._return = true
    } else if __e._message == "ExplicitComputed" {
        a := __e._parameters["a"].(int)
        _ = a
        b := __e._parameters["b"].(int)
        _ = b
        result := a * b + 10
        s._context_stack[len(s._context_stack)-1]._return = result
    } else if __e._message == "ExplicitConditional" {
        x := __e._parameters["x"].(int)
        _ = x
        if x < 0 {
            s._context_stack[len(s._context_stack)-1]._return = "negative"
            return
        } else if x == 0 {
            s._context_stack[len(s._context_stack)-1]._return = "zero"
            return
        } else {
            s._context_stack[len(s._context_stack)-1]._return = "positive"
        }
    } else if __e._message == "ExplicitInt" {
        s._context_stack[len(s._context_stack)-1]._return = 42
    } else if __e._message == "ExplicitString" {
        s._context_stack[len(s._context_stack)-1]._return = "Frame"
    } else if __e._message == "IntReturn" {
        s._context_stack[len(s._context_stack)-1]._return = 42
        return
    } else if __e._message == "StringReturn" {
        s._context_stack[len(s._context_stack)-1]._return = "Frame"
        return
    }
}

func main() {
	fmt.Println("=== Test 01: Interface Return (Go) ===")
	s := NewInterfaceReturn()
	errors := []string{}

	fmt.Println("-- Testing 'return value' sugar --")

	r1 := s.BoolReturn()
	if r1 != true {
		errors = append(errors, fmt.Sprintf("BoolReturn: expected true, got %v", r1))
	} else {
		fmt.Printf("1. BoolReturn() = %v\n", r1)
	}

	r2 := s.IntReturn()
	if r2 != 42 {
		errors = append(errors, fmt.Sprintf("IntReturn: expected 42, got %d", r2))
	} else {
		fmt.Printf("2. IntReturn() = %d\n", r2)
	}

	r3 := s.StringReturn()
	if r3 != "Frame" {
		errors = append(errors, fmt.Sprintf("StringReturn: expected 'Frame', got '%s'", r3))
	} else {
		fmt.Printf("3. StringReturn() = '%s'\n", r3)
	}

	r4 := s.ConditionalReturn(-5)
	if r4 != "negative" {
		errors = append(errors, fmt.Sprintf("ConditionalReturn(-5): expected 'negative', got '%s'", r4))
	}
	r4 = s.ConditionalReturn(0)
	if r4 != "zero" {
		errors = append(errors, fmt.Sprintf("ConditionalReturn(0): expected 'zero', got '%s'", r4))
	}
	r4 = s.ConditionalReturn(10)
	if r4 != "positive" {
		errors = append(errors, fmt.Sprintf("ConditionalReturn(10): expected 'positive', got '%s'", r4))
	} else {
		fmt.Println("4. ConditionalReturn(-5,0,10) = 'negative','zero','positive'")
	}

	r5 := s.ComputedReturn(3, 4)
	if r5 != 22 {
		errors = append(errors, fmt.Sprintf("ComputedReturn(3,4): expected 22, got %d", r5))
	} else {
		fmt.Printf("5. ComputedReturn(3,4) = %d\n", r5)
	}

	fmt.Println("-- Testing '@@:return = value' explicit --")

	r6 := s.ExplicitBool()
	if r6 != true {
		errors = append(errors, fmt.Sprintf("ExplicitBool: expected true, got %v", r6))
	} else {
		fmt.Printf("6. ExplicitBool() = %v\n", r6)
	}

	r7 := s.ExplicitInt()
	if r7 != 42 {
		errors = append(errors, fmt.Sprintf("ExplicitInt: expected 42, got %d", r7))
	} else {
		fmt.Printf("7. ExplicitInt() = %d\n", r7)
	}

	r8 := s.ExplicitString()
	if r8 != "Frame" {
		errors = append(errors, fmt.Sprintf("ExplicitString: expected 'Frame', got '%s'", r8))
	} else {
		fmt.Printf("8. ExplicitString() = '%s'\n", r8)
	}

	r9 := s.ExplicitConditional(-5)
	if r9 != "negative" {
		errors = append(errors, fmt.Sprintf("ExplicitConditional(-5): expected 'negative', got '%s'", r9))
	}
	r9 = s.ExplicitConditional(0)
	if r9 != "zero" {
		errors = append(errors, fmt.Sprintf("ExplicitConditional(0): expected 'zero', got '%s'", r9))
	}
	r9 = s.ExplicitConditional(10)
	if r9 != "positive" {
		errors = append(errors, fmt.Sprintf("ExplicitConditional(10): expected 'positive', got '%s'", r9))
	} else {
		fmt.Println("9. ExplicitConditional(-5,0,10) = 'negative','zero','positive'")
	}

	r10 := s.ExplicitComputed(3, 4)
	if r10 != 22 {
		errors = append(errors, fmt.Sprintf("ExplicitComputed(3,4): expected 22, got %d", r10))
	} else {
		fmt.Printf("10. ExplicitComputed(3,4) = %d\n", r10)
	}

	if len(errors) > 0 {
		for _, e := range errors {
			fmt.Println("FAIL: " + e)
		}
		os.Exit(1)
	} else {
		fmt.Println("PASS: All interface return tests passed")
	}
}
