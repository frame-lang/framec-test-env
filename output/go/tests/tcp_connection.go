
package main

import (
	"fmt"
	"os"
)

// TCP Connection State Machine (simplified RFC 793)
// Two Frame systems -- TcpClient and TcpServer -- communicating through
// direct method calls simulating packet exchange.

type TcpServerFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type TcpServerFrameContext struct {
    _event  TcpServerFrameEvent
    _return any
    _data   map[string]any
}

type TcpServerCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *TcpServerFrameEvent
    parentCompartment *TcpServerCompartment
}

func newTcpServerCompartment(state string) *TcpServerCompartment {
    return &TcpServerCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *TcpServerCompartment) copy() *TcpServerCompartment {
    nc := &TcpServerCompartment{
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

type TcpServer struct {
    _state_stack []*TcpServerCompartment
    __compartment *TcpServerCompartment
    __next_compartment *TcpServerCompartment
    _context_stack []TcpServerFrameContext
    last_data string
}

func NewTcpServer() *TcpServer {
    s := &TcpServer{}
    s._state_stack = make([]*TcpServerCompartment, 0)
    s._context_stack = make([]TcpServerFrameContext, 0)
    s.__compartment = newTcpServerCompartment("Closed")
    s.__next_compartment = nil
    __frame_event := TcpServerFrameEvent{_message: "$>", _parameters: nil}
    __ctx := TcpServerFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *TcpServer) __kernel(__e *TcpServerFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &TcpServerFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &TcpServerFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &TcpServerFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *TcpServer) __router(__e *TcpServerFrameEvent) {
    switch s.__compartment.state {
    case "Closed":
        s._state_Closed(__e)
    case "Listen":
        s._state_Listen(__e)
    case "SynReceived":
        s._state_SynReceived(__e)
    case "Established":
        s._state_Established(__e)
    case "CloseWait":
        s._state_CloseWait(__e)
    case "LastAck":
        s._state_LastAck(__e)
    case "FinWait1":
        s._state_FinWait1(__e)
    case "FinWait2":
        s._state_FinWait2(__e)
    case "Closing":
        s._state_Closing(__e)
    case "TimeWait":
        s._state_TimeWait(__e)
    }
}

func (s *TcpServer) __transition(next *TcpServerCompartment) {
    s.__next_compartment = next
}

func (s *TcpServer) Listen() {
    __e := TcpServerFrameEvent{_message: "Listen"}
    __ctx := TcpServerFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpServer) ReceiveSyn() {
    __e := TcpServerFrameEvent{_message: "ReceiveSyn"}
    __ctx := TcpServerFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpServer) ReceiveAck() {
    __e := TcpServerFrameEvent{_message: "ReceiveAck"}
    __ctx := TcpServerFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpServer) ReceiveFin() {
    __e := TcpServerFrameEvent{_message: "ReceiveFin"}
    __ctx := TcpServerFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpServer) ReceiveData(data string) {
    __params := map[string]any{
        "data": data,
    }
    __e := TcpServerFrameEvent{_message: "ReceiveData", _parameters: __params}
    __ctx := TcpServerFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpServer) Close() {
    __e := TcpServerFrameEvent{_message: "Close"}
    __ctx := TcpServerFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpServer) GetState() string {
    __e := TcpServerFrameEvent{_message: "GetState"}
    __ctx := TcpServerFrameContext{_event: __e, _return: "Unknown", _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *TcpServer) _state_SynReceived(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "SynReceived"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpServerCompartment("Established")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_FinWait2(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "FinWait2"
        return
    } else if __e._message == "ReceiveFin" {
        __compartment := newTcpServerCompartment("TimeWait")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_Listen(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Listen"
        return
    } else if __e._message == "ReceiveSyn" {
        __compartment := newTcpServerCompartment("SynReceived")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_LastAck(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "LastAck"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpServerCompartment("Closed")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_CloseWait(__e *TcpServerFrameEvent) {
    if __e._message == "Close" {
        __compartment := newTcpServerCompartment("LastAck")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "CloseWait"
        return
    }
}

func (s *TcpServer) _state_FinWait1(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "FinWait1"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpServerCompartment("FinWait2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "ReceiveFin" {
        __compartment := newTcpServerCompartment("Closing")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_Established(__e *TcpServerFrameEvent) {
    if __e._message == "Close" {
        __compartment := newTcpServerCompartment("FinWait1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Established"
        return
    } else if __e._message == "ReceiveData" {
        data := __e._parameters["data"].(string)
        _ = data
        s.last_data = data
    } else if __e._message == "ReceiveFin" {
        __compartment := newTcpServerCompartment("CloseWait")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_Closed(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Closed"
        return
    } else if __e._message == "Listen" {
        __compartment := newTcpServerCompartment("Listen")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_Closing(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Closing"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpServerCompartment("TimeWait")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpServer) _state_TimeWait(__e *TcpServerFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "TimeWait"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpServerCompartment("Closed")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}


type TcpClientFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type TcpClientFrameContext struct {
    _event  TcpClientFrameEvent
    _return any
    _data   map[string]any
}

type TcpClientCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *TcpClientFrameEvent
    parentCompartment *TcpClientCompartment
}

func newTcpClientCompartment(state string) *TcpClientCompartment {
    return &TcpClientCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *TcpClientCompartment) copy() *TcpClientCompartment {
    nc := &TcpClientCompartment{
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

type TcpClient struct {
    _state_stack []*TcpClientCompartment
    __compartment *TcpClientCompartment
    __next_compartment *TcpClientCompartment
    _context_stack []TcpClientFrameContext
    sent_count int
}

func NewTcpClient() *TcpClient {
    s := &TcpClient{}
    s._state_stack = make([]*TcpClientCompartment, 0)
    s._context_stack = make([]TcpClientFrameContext, 0)
    s.__compartment = newTcpClientCompartment("Closed")
    s.__next_compartment = nil
    __frame_event := TcpClientFrameEvent{_message: "$>", _parameters: nil}
    __ctx := TcpClientFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *TcpClient) __kernel(__e *TcpClientFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &TcpClientFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &TcpClientFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &TcpClientFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *TcpClient) __router(__e *TcpClientFrameEvent) {
    switch s.__compartment.state {
    case "Closed":
        s._state_Closed(__e)
    case "SynSent":
        s._state_SynSent(__e)
    case "Established":
        s._state_Established(__e)
    case "FinWait1":
        s._state_FinWait1(__e)
    case "FinWait2":
        s._state_FinWait2(__e)
    case "Closing":
        s._state_Closing(__e)
    case "TimeWait":
        s._state_TimeWait(__e)
    case "CloseWait":
        s._state_CloseWait(__e)
    case "LastAck":
        s._state_LastAck(__e)
    }
}

func (s *TcpClient) __transition(next *TcpClientCompartment) {
    s.__next_compartment = next
}

func (s *TcpClient) Connect() {
    __e := TcpClientFrameEvent{_message: "Connect"}
    __ctx := TcpClientFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpClient) ReceiveSynAck() {
    __e := TcpClientFrameEvent{_message: "ReceiveSynAck"}
    __ctx := TcpClientFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpClient) ReceiveAck() {
    __e := TcpClientFrameEvent{_message: "ReceiveAck"}
    __ctx := TcpClientFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpClient) ReceiveFin() {
    __e := TcpClientFrameEvent{_message: "ReceiveFin"}
    __ctx := TcpClientFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpClient) SendData(data string) {
    __params := map[string]any{
        "data": data,
    }
    __e := TcpClientFrameEvent{_message: "SendData", _parameters: __params}
    __ctx := TcpClientFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpClient) Close() {
    __e := TcpClientFrameEvent{_message: "Close"}
    __ctx := TcpClientFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *TcpClient) GetState() string {
    __e := TcpClientFrameEvent{_message: "GetState"}
    __ctx := TcpClientFrameContext{_event: __e, _return: "Unknown", _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *TcpClient) _state_CloseWait(__e *TcpClientFrameEvent) {
    if __e._message == "Close" {
        __compartment := newTcpClientCompartment("LastAck")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "CloseWait"
        return
    }
}

func (s *TcpClient) _state_SynSent(__e *TcpClientFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "SynSent"
        return
    } else if __e._message == "ReceiveSynAck" {
        __compartment := newTcpClientCompartment("Established")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpClient) _state_FinWait1(__e *TcpClientFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "FinWait1"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpClientCompartment("FinWait2")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "ReceiveFin" {
        __compartment := newTcpClientCompartment("Closing")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpClient) _state_LastAck(__e *TcpClientFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "LastAck"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpClientCompartment("Closed")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpClient) _state_TimeWait(__e *TcpClientFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "TimeWait"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpClientCompartment("Closed")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpClient) _state_Established(__e *TcpClientFrameEvent) {
    if __e._message == "Close" {
        __compartment := newTcpClientCompartment("FinWait1")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Established"
        return
    } else if __e._message == "ReceiveFin" {
        __compartment := newTcpClientCompartment("CloseWait")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "SendData" {
        data := __e._parameters["data"].(string)
        _ = data
        s.sent_count += 1
    }
}

func (s *TcpClient) _state_Closed(__e *TcpClientFrameEvent) {
    if __e._message == "Connect" {
        __compartment := newTcpClientCompartment("SynSent")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Closed"
        return
    }
}

func (s *TcpClient) _state_Closing(__e *TcpClientFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Closing"
        return
    } else if __e._message == "ReceiveAck" {
        __compartment := newTcpClientCompartment("TimeWait")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *TcpClient) _state_FinWait2(__e *TcpClientFrameEvent) {
    if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "FinWait2"
        return
    } else if __e._message == "ReceiveFin" {
        __compartment := newTcpClientCompartment("TimeWait")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

// ============================================================
// Test Harness
// ============================================================

func assertServerState(server *TcpServer, expected string, label string) {
	actual := server.GetState()
	if actual != expected {
		fmt.Printf("FAIL: %s -- expected '%s', got '%s'\n", label, expected, actual)
		os.Exit(1)
	}
}

func assertClientState(client *TcpClient, expected string, label string) {
	actual := client.GetState()
	if actual != expected {
		fmt.Printf("FAIL: %s -- expected '%s', got '%s'\n", label, expected, actual)
		os.Exit(1)
	}
}

func testHappyPath() {
	server := NewTcpServer()
	client := NewTcpClient()

	assertServerState(server, "Closed", "server initial")
	assertClientState(client, "Closed", "client initial")

	server.Listen()
	assertServerState(server, "Listen", "server listen")

	client.Connect()
	assertClientState(client, "SynSent", "client syn sent")

	server.ReceiveSyn()
	assertServerState(server, "SynReceived", "server syn received")

	client.ReceiveSynAck()
	assertClientState(client, "Established", "client established")

	server.ReceiveAck()
	assertServerState(server, "Established", "server established")

	client.SendData("hello")
	server.ReceiveData("hello")

	client.Close()
	assertClientState(client, "FinWait1", "client fin wait 1")

	server.ReceiveFin()
	assertServerState(server, "CloseWait", "server close wait")

	client.ReceiveAck()
	assertClientState(client, "FinWait2", "client fin wait 2")

	server.Close()
	assertServerState(server, "LastAck", "server last ack")

	client.ReceiveFin()
	assertClientState(client, "TimeWait", "client time wait")

	server.ReceiveAck()
	assertServerState(server, "Closed", "server closed")

	client.ReceiveAck()
	assertClientState(client, "Closed", "client closed")

	fmt.Println("PASS: TCP happy path")
}

func testSimultaneousClose() {
	server := NewTcpServer()
	client := NewTcpClient()

	server.Listen()
	client.Connect()
	server.ReceiveSyn()
	client.ReceiveSynAck()
	server.ReceiveAck()

	client.Close()
	server.Close()
	assertClientState(client, "FinWait1", "client fin wait 1")
	assertServerState(server, "FinWait1", "server fin wait 1")

	client.ReceiveFin()
	server.ReceiveFin()
	assertClientState(client, "Closing", "client closing")
	assertServerState(server, "Closing", "server closing")

	client.ReceiveAck()
	server.ReceiveAck()
	assertClientState(client, "TimeWait", "client time wait")
	assertServerState(server, "TimeWait", "server time wait")

	client.ReceiveAck()
	server.ReceiveAck()
	assertClientState(client, "Closed", "client closed")
	assertServerState(server, "Closed", "server closed")

	fmt.Println("PASS: TCP simultaneous close")
}

func main() {
	testHappyPath()
	testSimultaneousClose()
	fmt.Println("PASS: All TCP connection tests passed")
}
