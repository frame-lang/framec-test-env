#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// TCP Connection State Machine (simplified RFC 793)

class TcpServerFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    TcpServerFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class TcpServerFrameContext {
public:
    TcpServerFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    TcpServerFrameContext(TcpServerFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class TcpServerCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<TcpServerFrameEvent> forward_event;
    std::unique_ptr<TcpServerCompartment> parent_compartment;

    explicit TcpServerCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<TcpServerCompartment> clone() const {
        auto c = std::make_unique<TcpServerCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class TcpServer {
private:
    std::vector<std::unique_ptr<TcpServerCompartment>> _state_stack;
    std::unique_ptr<TcpServerCompartment> __compartment;
    std::unique_ptr<TcpServerCompartment> __next_compartment;
    std::vector<TcpServerFrameContext> _context_stack;

    void __kernel(TcpServerFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            TcpServerFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                TcpServerFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    TcpServerFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(TcpServerFrameEvent& __e) {
        const auto& state_name = __compartment->state;
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

    void __transition(std::unique_ptr<TcpServerCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Closing(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Closing"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("TimeWait");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_TimeWait(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("TimeWait"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("Closed");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_CloseWait(TcpServerFrameEvent& __e) {
        if (__e._message == "close") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("LastAck");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("CloseWait"));
            return;;
        }
    }

    void _state_LastAck(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("LastAck"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("Closed");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_FinWait2(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("FinWait2"));
            return;;
        } else if (__e._message == "receive_fin") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("TimeWait");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_SynReceived(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("SynReceived"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("Established");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_FinWait1(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("FinWait1"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("FinWait2");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "receive_fin") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("Closing");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Listen(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Listen"));
            return;;
        } else if (__e._message == "receive_syn") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("SynReceived");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Established(TcpServerFrameEvent& __e) {
        if (__e._message == "close") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("FinWait1");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Established"));
            return;;
        } else if (__e._message == "receive_data") {
            auto data = std::any_cast<std::string>(__e._parameters.at("data"));
            last_data = data;
        } else if (__e._message == "receive_fin") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("CloseWait");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Closed(TcpServerFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Closed"));
            return;;
        } else if (__e._message == "listen") {
            auto __new_compartment = std::make_unique<TcpServerCompartment>("Listen");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    std::string last_data = "";

    TcpServer() {
        __compartment = std::make_unique<TcpServerCompartment>("Closed");
        TcpServerFrameEvent __frame_event("$>");
        TcpServerFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void listen() {
        TcpServerFrameEvent __e("listen");
        TcpServerFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void receive_syn() {
        TcpServerFrameEvent __e("receive_syn");
        TcpServerFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void receive_ack() {
        TcpServerFrameEvent __e("receive_ack");
        TcpServerFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void receive_fin() {
        TcpServerFrameEvent __e("receive_fin");
        TcpServerFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void receive_data(std::string data) {
        std::unordered_map<std::string, std::any> __params;
        __params["data"] = data;
        TcpServerFrameEvent __e("receive_data", std::move(__params));
        TcpServerFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void close() {
        TcpServerFrameEvent __e("close");
        TcpServerFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        TcpServerFrameEvent __e("get_state");
        TcpServerFrameContext __ctx(std::move(__e), std::any(std::string("Unknown")));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};


class TcpClientFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    TcpClientFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class TcpClientFrameContext {
public:
    TcpClientFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    TcpClientFrameContext(TcpClientFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class TcpClientCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<TcpClientFrameEvent> forward_event;
    std::unique_ptr<TcpClientCompartment> parent_compartment;

    explicit TcpClientCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<TcpClientCompartment> clone() const {
        auto c = std::make_unique<TcpClientCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class TcpClient {
private:
    std::vector<std::unique_ptr<TcpClientCompartment>> _state_stack;
    std::unique_ptr<TcpClientCompartment> __compartment;
    std::unique_ptr<TcpClientCompartment> __next_compartment;
    std::vector<TcpClientFrameContext> _context_stack;

    void __kernel(TcpClientFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            TcpClientFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                TcpClientFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    TcpClientFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(TcpClientFrameEvent& __e) {
        const auto& state_name = __compartment->state;
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

    void __transition(std::unique_ptr<TcpClientCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_CloseWait(TcpClientFrameEvent& __e) {
        if (__e._message == "close") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("LastAck");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("CloseWait"));
            return;;
        }
    }

    void _state_FinWait2(TcpClientFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("FinWait2"));
            return;;
        } else if (__e._message == "receive_fin") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("TimeWait");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Closed(TcpClientFrameEvent& __e) {
        if (__e._message == "connect") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("SynSent");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Closed"));
            return;;
        }
    }

    void _state_FinWait1(TcpClientFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("FinWait1"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("FinWait2");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "receive_fin") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("Closing");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_SynSent(TcpClientFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("SynSent"));
            return;;
        } else if (__e._message == "receive_syn_ack") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("Established");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Established(TcpClientFrameEvent& __e) {
        if (__e._message == "close") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("FinWait1");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Established"));
            return;;
        } else if (__e._message == "receive_fin") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("CloseWait");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "send_data") {
            auto data = std::any_cast<std::string>(__e._parameters.at("data"));
            sent_count += 1;
        }
    }

    void _state_LastAck(TcpClientFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("LastAck"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("Closed");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_TimeWait(TcpClientFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("TimeWait"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("Closed");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Closing(TcpClientFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Closing"));
            return;;
        } else if (__e._message == "receive_ack") {
            auto __new_compartment = std::make_unique<TcpClientCompartment>("TimeWait");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    int sent_count = 0;

    TcpClient() {
        __compartment = std::make_unique<TcpClientCompartment>("Closed");
        TcpClientFrameEvent __frame_event("$>");
        TcpClientFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void connect() {
        TcpClientFrameEvent __e("connect");
        TcpClientFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void receive_syn_ack() {
        TcpClientFrameEvent __e("receive_syn_ack");
        TcpClientFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void receive_ack() {
        TcpClientFrameEvent __e("receive_ack");
        TcpClientFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void receive_fin() {
        TcpClientFrameEvent __e("receive_fin");
        TcpClientFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void send_data(std::string data) {
        std::unordered_map<std::string, std::any> __params;
        __params["data"] = data;
        TcpClientFrameEvent __e("send_data", std::move(__params));
        TcpClientFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void close() {
        TcpClientFrameEvent __e("close");
        TcpClientFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        TcpClientFrameEvent __e("get_state");
        TcpClientFrameContext __ctx(std::move(__e), std::any(std::string("Unknown")));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

// ============================================================
// Test Harness
// ============================================================

template<typename T>
void assert_state(T& system, const std::string& expected, const std::string& label) {
    std::string actual = system.get_state();
    if (actual != expected) {
        printf("FAIL: %s - expected '%s', got '%s'\n", label.c_str(), expected.c_str(), actual.c_str());
        assert(false);
    }
}

void test_happy_path() {
    TcpServer server;
    TcpClient client;

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

    printf("PASS: TCP happy path\n");
}

void test_simultaneous_close() {
    TcpServer server;
    TcpClient client;

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

    printf("PASS: TCP simultaneous close\n");
}

int main() {
    test_happy_path();
    test_simultaneous_close();
    printf("PASS: All TCP connection tests passed\n");
    return 0;
}
