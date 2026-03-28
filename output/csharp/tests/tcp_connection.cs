using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// TCP Connection State Machine (simplified RFC 793)
// Two Frame systems -- TcpClient and TcpServer -- communicating through
// direct method calls simulating packet exchange.

class TcpServerFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public TcpServerFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public TcpServerFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TcpServerFrameContext {
    public TcpServerFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public TcpServerFrameContext(TcpServerFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class TcpServerCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public TcpServerFrameEvent forward_event;
    public TcpServerCompartment parent_compartment;

    public TcpServerCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public TcpServerCompartment Copy() {
        TcpServerCompartment c = new TcpServerCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TcpServer {
    private List<TcpServerCompartment> _state_stack;
    private TcpServerCompartment __compartment;
    private TcpServerCompartment __next_compartment;
    private List<TcpServerFrameContext> _context_stack;
    public string last_data = "";

    public TcpServer() {
        _state_stack = new List<TcpServerCompartment>();
        _context_stack = new List<TcpServerFrameContext>();
        __compartment = new TcpServerCompartment("Closed");
        __next_compartment = null;
        TcpServerFrameEvent __frame_event = new TcpServerFrameEvent("$>");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(TcpServerFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TcpServerFrameEvent exit_event = new TcpServerFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TcpServerFrameEvent enter_event = new TcpServerFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    TcpServerFrameEvent enter_event = new TcpServerFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TcpServerFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Closed") {
            _state_Closed(__e);
        } else if (state_name == "Listen") {
            _state_Listen(__e);
        } else if (state_name == "SynReceived") {
            _state_SynReceived(__e);
        } else if (state_name == "Established") {
            _state_Established(__e);
        } else if (state_name == "CloseWait") {
            _state_CloseWait(__e);
        } else if (state_name == "LastAck") {
            _state_LastAck(__e);
        } else if (state_name == "FinWait1") {
            _state_FinWait1(__e);
        } else if (state_name == "FinWait2") {
            _state_FinWait2(__e);
        } else if (state_name == "Closing") {
            _state_Closing(__e);
        } else if (state_name == "TimeWait") {
            _state_TimeWait(__e);
        }
    }

    private void __transition(TcpServerCompartment next) {
        __next_compartment = next;
    }

    public void listen() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("listen");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void receive_syn() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_syn");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void receive_ack() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_ack");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void receive_fin() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_fin");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void receive_data(string data) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["data"] = data;
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_data", __params);
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void close() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("close");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("get_state");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, "Unknown");
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_SynReceived(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "SynReceived";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpServerCompartment("Established");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_CloseWait(TcpServerFrameEvent __e) {
        if (__e._message == "close") {
            { var __new_compartment = new TcpServerCompartment("LastAck");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "CloseWait";
            return;
        }
    }

    private void _state_Established(TcpServerFrameEvent __e) {
        if (__e._message == "close") {
            { var __new_compartment = new TcpServerCompartment("FinWait1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Established";
            return;
        } else if (__e._message == "receive_data") {
            var data = (string) __e._parameters["data"];
            this.last_data = data;
        } else if (__e._message == "receive_fin") {
            { var __new_compartment = new TcpServerCompartment("CloseWait");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_LastAck(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "LastAck";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpServerCompartment("Closed");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Closing(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Closing";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpServerCompartment("TimeWait");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_FinWait1(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "FinWait1";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpServerCompartment("FinWait2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "receive_fin") {
            { var __new_compartment = new TcpServerCompartment("Closing");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_TimeWait(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "TimeWait";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpServerCompartment("Closed");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Listen(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Listen";
            return;
        } else if (__e._message == "receive_syn") {
            { var __new_compartment = new TcpServerCompartment("SynReceived");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Closed(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Closed";
            return;
        } else if (__e._message == "listen") {
            { var __new_compartment = new TcpServerCompartment("Listen");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_FinWait2(TcpServerFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "FinWait2";
            return;
        } else if (__e._message == "receive_fin") {
            { var __new_compartment = new TcpServerCompartment("TimeWait");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }
}


class TcpClientFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public TcpClientFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public TcpClientFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TcpClientFrameContext {
    public TcpClientFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public TcpClientFrameContext(TcpClientFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class TcpClientCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public TcpClientFrameEvent forward_event;
    public TcpClientCompartment parent_compartment;

    public TcpClientCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public TcpClientCompartment Copy() {
        TcpClientCompartment c = new TcpClientCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TcpClient {
    private List<TcpClientCompartment> _state_stack;
    private TcpClientCompartment __compartment;
    private TcpClientCompartment __next_compartment;
    private List<TcpClientFrameContext> _context_stack;
    public int sent_count = 0;

    public TcpClient() {
        _state_stack = new List<TcpClientCompartment>();
        _context_stack = new List<TcpClientFrameContext>();
        __compartment = new TcpClientCompartment("Closed");
        __next_compartment = null;
        TcpClientFrameEvent __frame_event = new TcpClientFrameEvent("$>");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(TcpClientFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TcpClientFrameEvent exit_event = new TcpClientFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TcpClientFrameEvent enter_event = new TcpClientFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    TcpClientFrameEvent enter_event = new TcpClientFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TcpClientFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Closed") {
            _state_Closed(__e);
        } else if (state_name == "SynSent") {
            _state_SynSent(__e);
        } else if (state_name == "Established") {
            _state_Established(__e);
        } else if (state_name == "FinWait1") {
            _state_FinWait1(__e);
        } else if (state_name == "FinWait2") {
            _state_FinWait2(__e);
        } else if (state_name == "Closing") {
            _state_Closing(__e);
        } else if (state_name == "TimeWait") {
            _state_TimeWait(__e);
        } else if (state_name == "CloseWait") {
            _state_CloseWait(__e);
        } else if (state_name == "LastAck") {
            _state_LastAck(__e);
        }
    }

    private void __transition(TcpClientCompartment next) {
        __next_compartment = next;
    }

    public void connect() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("connect");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void receive_syn_ack() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("receive_syn_ack");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void receive_ack() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("receive_ack");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void receive_fin() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("receive_fin");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void send_data(string data) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["data"] = data;
        TcpClientFrameEvent __e = new TcpClientFrameEvent("send_data", __params);
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void close() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("close");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("get_state");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, "Unknown");
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Established(TcpClientFrameEvent __e) {
        if (__e._message == "close") {
            { var __new_compartment = new TcpClientCompartment("FinWait1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Established";
            return;
        } else if (__e._message == "receive_fin") {
            { var __new_compartment = new TcpClientCompartment("CloseWait");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "send_data") {
            var data = (string) __e._parameters["data"];
            this.sent_count += 1;
        }
    }

    private void _state_FinWait1(TcpClientFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "FinWait1";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpClientCompartment("FinWait2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "receive_fin") {
            { var __new_compartment = new TcpClientCompartment("Closing");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_LastAck(TcpClientFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "LastAck";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpClientCompartment("Closed");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_FinWait2(TcpClientFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "FinWait2";
            return;
        } else if (__e._message == "receive_fin") {
            { var __new_compartment = new TcpClientCompartment("TimeWait");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Closing(TcpClientFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Closing";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpClientCompartment("TimeWait");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_CloseWait(TcpClientFrameEvent __e) {
        if (__e._message == "close") {
            { var __new_compartment = new TcpClientCompartment("LastAck");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "CloseWait";
            return;
        }
    }

    private void _state_SynSent(TcpClientFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "SynSent";
            return;
        } else if (__e._message == "receive_syn_ack") {
            { var __new_compartment = new TcpClientCompartment("Established");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_TimeWait(TcpClientFrameEvent __e) {
        if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "TimeWait";
            return;
        } else if (__e._message == "receive_ack") {
            { var __new_compartment = new TcpClientCompartment("Closed");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Closed(TcpClientFrameEvent __e) {
        if (__e._message == "connect") {
            { var __new_compartment = new TcpClientCompartment("SynSent");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Closed";
            return;
        }
    }
}

// ============================================================
// Test Harness
// ============================================================

class Program {
    static void assert_state(object system, string expected, string label) {
        string actual;
        if (system is TcpServer) {
            actual = (string) ((TcpServer) system).get_state();
        } else {
            actual = (string) ((TcpClient) system).get_state();
        }
        if (actual != expected) {
            Console.WriteLine("FAIL: " + label + " -- expected '" + expected + "', got '" + actual + "'");
            throw new Exception("State assertion failed: " + label);
        }
    }

    static void test_happy_path() {
        TcpServer server = new TcpServer();
        TcpClient client = new TcpClient();

        assert_state(server, "Closed", "server initial");
        assert_state(client, "Closed", "client initial");

        server.listen();
        assert_state(server, "Listen", "server listen");

        client.connect();
        assert_state(client, "SynSent", "client syn sent");

        server.receive_syn();
        assert_state(server, "SynReceived", "server syn received");

        client.receive_syn_ack();
        assert_state(client, "Established", "client established");

        server.receive_ack();
        assert_state(server, "Established", "server established");

        client.send_data("hello");
        server.receive_data("hello");

        client.close();
        assert_state(client, "FinWait1", "client fin wait 1");

        server.receive_fin();
        assert_state(server, "CloseWait", "server close wait");

        client.receive_ack();
        assert_state(client, "FinWait2", "client fin wait 2");

        server.close();
        assert_state(server, "LastAck", "server last ack");

        client.receive_fin();
        assert_state(client, "TimeWait", "client time wait");

        server.receive_ack();
        assert_state(server, "Closed", "server closed");

        client.receive_ack();
        assert_state(client, "Closed", "client closed");

        Console.WriteLine("PASS: TCP happy path");
    }

    static void test_simultaneous_close() {
        TcpServer server = new TcpServer();
        TcpClient client = new TcpClient();

        server.listen();
        client.connect();
        server.receive_syn();
        client.receive_syn_ack();
        server.receive_ack();

        client.close();
        server.close();
        assert_state(client, "FinWait1", "client fin wait 1");
        assert_state(server, "FinWait1", "server fin wait 1");

        client.receive_fin();
        server.receive_fin();
        assert_state(client, "Closing", "client closing");
        assert_state(server, "Closing", "server closing");

        client.receive_ack();
        server.receive_ack();
        assert_state(client, "TimeWait", "client time wait");
        assert_state(server, "TimeWait", "server time wait");

        client.receive_ack();
        server.receive_ack();
        assert_state(client, "Closed", "client closed");
        assert_state(server, "Closed", "server closed");

        Console.WriteLine("PASS: TCP simultaneous close");
    }

    static void Main(string[] args) {
        try {
            test_happy_path();
            test_simultaneous_close();
            Console.WriteLine("PASS: All TCP connection tests passed");
        } catch (Exception ex) {
            Console.WriteLine("FAIL: " + ex.Message);
            Environment.Exit(1);
        }
    }
}
