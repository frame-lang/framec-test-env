
package main

import "fmt"
import "os"
import "strings"

type ContextDataTestFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type ContextDataTestFrameContext struct {
    _event  ContextDataTestFrameEvent
    _return any
    _data   map[string]any
}

type ContextDataTestCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *ContextDataTestFrameEvent
    parentCompartment *ContextDataTestCompartment
}

func newContextDataTestCompartment(state string) *ContextDataTestCompartment {
    return &ContextDataTestCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *ContextDataTestCompartment) copy() *ContextDataTestCompartment {
    nc := &ContextDataTestCompartment{
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

type ContextDataTest struct {
    _state_stack []*ContextDataTestCompartment
    __compartment *ContextDataTestCompartment
    __next_compartment *ContextDataTestCompartment
    _context_stack []ContextDataTestFrameContext
}

func NewContextDataTest() *ContextDataTest {
    s := &ContextDataTest{}
    s._state_stack = make([]*ContextDataTestCompartment, 0)
    s._context_stack = make([]ContextDataTestFrameContext, 0)
    s.__compartment = newContextDataTestCompartment("Start")
    s.__next_compartment = nil
    __frame_event := ContextDataTestFrameEvent{_message: "$>", _parameters: nil}
    __ctx := ContextDataTestFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *ContextDataTest) __kernel(__e *ContextDataTestFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &ContextDataTestFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &ContextDataTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &ContextDataTestFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *ContextDataTest) __router(__e *ContextDataTestFrameEvent) {
    switch s.__compartment.state {
    case "Start":
        s._state_Start(__e)
    case "End":
        s._state_End(__e)
    }
}

func (s *ContextDataTest) __transition(next *ContextDataTestCompartment) {
    s.__next_compartment = next
}

func (s *ContextDataTest) ProcessWithData(value int) string {
    __params := map[string]any{
        "value": value,
    }
    __e := ContextDataTestFrameEvent{_message: "ProcessWithData", _parameters: __params}
    __ctx := ContextDataTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextDataTest) CheckDataIsolation() string {
    __e := ContextDataTestFrameEvent{_message: "CheckDataIsolation"}
    __ctx := ContextDataTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextDataTest) TransitionPreservesData(x int) string {
    __params := map[string]any{
        "x": x,
    }
    __e := ContextDataTestFrameEvent{_message: "TransitionPreservesData", _parameters: __params}
    __ctx := ContextDataTestFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *ContextDataTest) _state_End(__e *ContextDataTestFrameEvent) {
    if __e._message == "$>" {
        // Enter handler can access data set by previous handlers
        trace := s._context_stack[len(s._context_stack)-1]._data["trace"].([]string)
        trace = append(trace, "enter")
        s._context_stack[len(s._context_stack)-1]._data["trace"] = trace
        s._context_stack[len(s._context_stack)-1]._data["ended_in"] = "End"

        // Build final result from accumulated data
        trace_str := strings.Join(trace, ",")
        started := s._context_stack[len(s._context_stack)-1]._data["started_in"]
        ended := s._context_stack[len(s._context_stack)-1]._data["ended_in"]
        val := s._context_stack[len(s._context_stack)-1]._data["value"]
        s._context_stack[len(s._context_stack)-1]._return = fmt.Sprintf("from=%v,to=%v,value=%v,trace=%s", started, ended, val, trace_str)
    }
}

func (s *ContextDataTest) _state_Start(__e *ContextDataTestFrameEvent) {
    if __e._message == "<$" {
        // Exit handler can access data set by event handler
        trace := s._context_stack[len(s._context_stack)-1]._data["trace"].([]string)
        trace = append(trace, "exit")
        s._context_stack[len(s._context_stack)-1]._data["trace"] = trace
    } else if __e._message == "CheckDataIsolation" {
        // Set data, call another method, verify our data preserved
        s._context_stack[len(s._context_stack)-1]._data["outer"] = "outer_value"

        // This creates its own context with its own data
        inner_result := s.ProcessWithData(99)

        // Our data should still be here
        outer_val := s._context_stack[len(s._context_stack)-1]._data["outer"]
        s._context_stack[len(s._context_stack)-1]._return = fmt.Sprintf("outer_data=%v,inner=%s", outer_val, inner_result)
    } else if __e._message == "ProcessWithData" {
        value := __e._parameters["value"].(int)
        _ = value
        // Set data in handler
        s._context_stack[len(s._context_stack)-1]._data["input"] = value
        // Read data back using context stack directly
        input := s._context_stack[len(s._context_stack)-1]._data["input"]
        s._context_stack[len(s._context_stack)-1]._return = fmt.Sprintf("processed:%v", input)
    } else if __e._message == "TransitionPreservesData" {
        x := __e._parameters["x"].(int)
        _ = x
        // Set data, transition, verify data available in lifecycle handlers
        s._context_stack[len(s._context_stack)-1]._data["started_in"] = "Start"
        s._context_stack[len(s._context_stack)-1]._data["value"] = x
        s._context_stack[len(s._context_stack)-1]._data["trace"] = []string{"handler"}
        __compartment := newContextDataTestCompartment("End")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func main() {
	fmt.Println("=== Test 38: Context Data ===")

	// Test 1: Basic data set/get
	s1 := NewContextDataTest()
	result := s1.ProcessWithData(42)
	if result != "processed:42" {
		fmt.Printf("FAIL: Expected 'processed:42', got '%s'\n", result)
		os.Exit(1)
	}
	fmt.Printf("1. ProcessWithData(42) = '%s'\n", result)

	// Test 2: Data isolation between nested calls
	s2 := NewContextDataTest()
	result = s2.CheckDataIsolation()
	expected := "outer_data=outer_value,inner=processed:99"
	if result != expected {
		fmt.Printf("FAIL: Expected '%s', got '%s'\n", expected, result)
		os.Exit(1)
	}
	fmt.Printf("2. CheckDataIsolation() = '%s'\n", result)

	// Test 3: Data preserved across transition (handler -> <$ -> $>)
	s3 := NewContextDataTest()
	result = s3.TransitionPreservesData(100)
	if !strings.Contains(result, "from=Start") {
		fmt.Printf("FAIL: Expected 'from=Start' in '%s'\n", result)
		os.Exit(1)
	}
	if !strings.Contains(result, "to=End") {
		fmt.Printf("FAIL: Expected 'to=End' in '%s'\n", result)
		os.Exit(1)
	}
	if !strings.Contains(result, "value=100") {
		fmt.Printf("FAIL: Expected 'value=100' in '%s'\n", result)
		os.Exit(1)
	}
	fmt.Printf("3. TransitionPreservesData(100) = '%s'\n", result)

	fmt.Println("PASS: Context data works correctly")
}
