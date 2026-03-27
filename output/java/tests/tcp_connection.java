import java.util.*;


import java.util.*;

// TCP Connection State Machine (simplified RFC 793)
// Two Frame systems -- TcpClient and TcpServer -- communicating through
// direct method calls simulating packet exchange.

class TcpServerFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    TcpServerFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    TcpServerFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TcpServerFrameContext {
    TcpServerFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    TcpServerFrameContext(TcpServerFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class TcpServerCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    TcpServerFrameEvent forward_event;
    TcpServerCompartment parent_compartment;

    TcpServerCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    TcpServerCompartment copy() {
        TcpServerCompartment c = new TcpServerCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TcpServer {
    private ArrayList<TcpServerCompartment> _state_stack;
    private TcpServerCompartment __compartment;
    private TcpServerCompartment __next_compartment;
    private ArrayList<TcpServerFrameContext> _context_stack;
    public String last_data = "";

    public TcpServer() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new TcpServerCompartment("Closed");
        __next_compartment = null;
        TcpServerFrameEvent __frame_event = new TcpServerFrameEvent("$>");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Closed")) {
            _state_Closed(__e);
        } else if (state_name.equals("Listen")) {
            _state_Listen(__e);
        } else if (state_name.equals("SynReceived")) {
            _state_SynReceived(__e);
        } else if (state_name.equals("Established")) {
            _state_Established(__e);
        } else if (state_name.equals("CloseWait")) {
            _state_CloseWait(__e);
        } else if (state_name.equals("LastAck")) {
            _state_LastAck(__e);
        } else if (state_name.equals("FinWait1")) {
            _state_FinWait1(__e);
        } else if (state_name.equals("FinWait2")) {
            _state_FinWait2(__e);
        } else if (state_name.equals("Closing")) {
            _state_Closing(__e);
        } else if (state_name.equals("TimeWait")) {
            _state_TimeWait(__e);
        }
    }

    private void __transition(TcpServerCompartment next) {
        __next_compartment = next;
    }

    public void listen() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("listen");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void receive_syn() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_syn");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void receive_ack() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_ack");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void receive_fin() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_fin");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void receive_data(String data) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("data", data);
        TcpServerFrameEvent __e = new TcpServerFrameEvent("receive_data", __params);
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void close() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("close");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        TcpServerFrameEvent __e = new TcpServerFrameEvent("get_state");
        TcpServerFrameContext __ctx = new TcpServerFrameContext(__e, "Unknown");
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_SynReceived(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "SynReceived";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpServerCompartment("Established");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_FinWait2(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "FinWait2";
            return;
        } else if (__e._message.equals("receive_fin")) {
            var __compartment = new TcpServerCompartment("TimeWait");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Established(TcpServerFrameEvent __e) {
        if (__e._message.equals("close")) {
            var __compartment = new TcpServerCompartment("FinWait1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Established";
            return;
        } else if (__e._message.equals("receive_data")) {
            var data = (String) __e._parameters.get("data");
            this.last_data = data;
        } else if (__e._message.equals("receive_fin")) {
            var __compartment = new TcpServerCompartment("CloseWait");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Closed(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Closed";
            return;
        } else if (__e._message.equals("listen")) {
            var __compartment = new TcpServerCompartment("Listen");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Closing(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Closing";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpServerCompartment("TimeWait");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_TimeWait(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "TimeWait";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpServerCompartment("Closed");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_FinWait1(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "FinWait1";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpServerCompartment("FinWait2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("receive_fin")) {
            var __compartment = new TcpServerCompartment("Closing");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_LastAck(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "LastAck";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpServerCompartment("Closed");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Listen(TcpServerFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Listen";
            return;
        } else if (__e._message.equals("receive_syn")) {
            var __compartment = new TcpServerCompartment("SynReceived");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_CloseWait(TcpServerFrameEvent __e) {
        if (__e._message.equals("close")) {
            var __compartment = new TcpServerCompartment("LastAck");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "CloseWait";
            return;
        }
    }
}


class TcpClientFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    TcpClientFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    TcpClientFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TcpClientFrameContext {
    TcpClientFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    TcpClientFrameContext(TcpClientFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class TcpClientCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    TcpClientFrameEvent forward_event;
    TcpClientCompartment parent_compartment;

    TcpClientCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    TcpClientCompartment copy() {
        TcpClientCompartment c = new TcpClientCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TcpClient {
    private ArrayList<TcpClientCompartment> _state_stack;
    private TcpClientCompartment __compartment;
    private TcpClientCompartment __next_compartment;
    private ArrayList<TcpClientFrameContext> _context_stack;
    public int sent_count = 0;

    public TcpClient() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new TcpClientCompartment("Closed");
        __next_compartment = null;
        TcpClientFrameEvent __frame_event = new TcpClientFrameEvent("$>");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Closed")) {
            _state_Closed(__e);
        } else if (state_name.equals("SynSent")) {
            _state_SynSent(__e);
        } else if (state_name.equals("Established")) {
            _state_Established(__e);
        } else if (state_name.equals("FinWait1")) {
            _state_FinWait1(__e);
        } else if (state_name.equals("FinWait2")) {
            _state_FinWait2(__e);
        } else if (state_name.equals("Closing")) {
            _state_Closing(__e);
        } else if (state_name.equals("TimeWait")) {
            _state_TimeWait(__e);
        } else if (state_name.equals("CloseWait")) {
            _state_CloseWait(__e);
        } else if (state_name.equals("LastAck")) {
            _state_LastAck(__e);
        }
    }

    private void __transition(TcpClientCompartment next) {
        __next_compartment = next;
    }

    public void connect() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("connect");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void receive_syn_ack() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("receive_syn_ack");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void receive_ack() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("receive_ack");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void receive_fin() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("receive_fin");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void send_data(String data) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("data", data);
        TcpClientFrameEvent __e = new TcpClientFrameEvent("send_data", __params);
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void close() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("close");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        TcpClientFrameEvent __e = new TcpClientFrameEvent("get_state");
        TcpClientFrameContext __ctx = new TcpClientFrameContext(__e, "Unknown");
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_SynSent(TcpClientFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "SynSent";
            return;
        } else if (__e._message.equals("receive_syn_ack")) {
            var __compartment = new TcpClientCompartment("Established");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Closed(TcpClientFrameEvent __e) {
        if (__e._message.equals("connect")) {
            var __compartment = new TcpClientCompartment("SynSent");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Closed";
            return;
        }
    }

    private void _state_TimeWait(TcpClientFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "TimeWait";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpClientCompartment("Closed");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Closing(TcpClientFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Closing";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpClientCompartment("TimeWait");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_FinWait2(TcpClientFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "FinWait2";
            return;
        } else if (__e._message.equals("receive_fin")) {
            var __compartment = new TcpClientCompartment("TimeWait");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_CloseWait(TcpClientFrameEvent __e) {
        if (__e._message.equals("close")) {
            var __compartment = new TcpClientCompartment("LastAck");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "CloseWait";
            return;
        }
    }

    private void _state_FinWait1(TcpClientFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "FinWait1";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpClientCompartment("FinWait2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("receive_fin")) {
            var __compartment = new TcpClientCompartment("Closing");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_LastAck(TcpClientFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "LastAck";
            return;
        } else if (__e._message.equals("receive_ack")) {
            var __compartment = new TcpClientCompartment("Closed");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Established(TcpClientFrameEvent __e) {
        if (__e._message.equals("close")) {
            var __compartment = new TcpClientCompartment("FinWait1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Established";
            return;
        } else if (__e._message.equals("receive_fin")) {
            var __compartment = new TcpClientCompartment("CloseWait");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("send_data")) {
            var data = (String) __e._parameters.get("data");
            this.sent_count += 1;
        }
    }
}

// ============================================================
// Test Harness
// ============================================================

class Main {
    static void assert_state(Object system, String expected, String label) throws Exception {
        String actual;
        if (system instanceof TcpServer) {
            actual = (String) ((TcpServer) system).get_state();
        } else {
            actual = (String) ((TcpClient) system).get_state();
        }
        if (!actual.equals(expected)) {
            System.out.println("FAIL: " + label + " -- expected '" + expected + "', got '" + actual + "'");
            throw new Exception("State assertion failed: " + label);
        }
    }

    static void test_happy_path() throws Exception {
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

        System.out.println("PASS: TCP happy path");
    }

    static void test_simultaneous_close() throws Exception {
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

        System.out.println("PASS: TCP simultaneous close");
    }

    public static void main(String[] args) {
        try {
            test_happy_path();
            test_simultaneous_close();
            System.out.println("PASS: All TCP connection tests passed");
        } catch (Exception ex) {
            System.out.println("FAIL: " + ex.getMessage());
            System.exit(1);
        }
    }
}
