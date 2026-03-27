#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class CallMismatchFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    CallMismatchFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class CallMismatchFrameContext {
public:
    CallMismatchFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    CallMismatchFrameContext(CallMismatchFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class CallMismatchCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<CallMismatchFrameEvent> forward_event;
    std::unique_ptr<CallMismatchCompartment> parent_compartment;

    explicit CallMismatchCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<CallMismatchCompartment> clone() const {
        auto c = std::make_unique<CallMismatchCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class CallMismatch {
private:
    std::vector<std::unique_ptr<CallMismatchCompartment>> _state_stack;
    std::unique_ptr<CallMismatchCompartment> __compartment;
    std::unique_ptr<CallMismatchCompartment> __next_compartment;
    std::vector<CallMismatchFrameContext> _context_stack;

    void __kernel(CallMismatchFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            CallMismatchFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                CallMismatchFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    CallMismatchFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(CallMismatchFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "S") {
            _state_S(__e);
        }
    }

    void __transition(std::unique_ptr<CallMismatchCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_S(CallMismatchFrameEvent& __e) {
        if (__e._message == "e") {
            this->handle();
        }
    }

    void log(std::string message) {
                    // log sink
                    this->last = message;
    }

    void handle() {
                    // Calls 'log' without _action_ prefix; wrappers should preserve FRM names
                    this->log(std::string("hello"));
    }

public:
    std::string last = "";

    CallMismatch() {
        __compartment = std::make_unique<CallMismatchCompartment>("S");
        CallMismatchFrameEvent __frame_event("$>");
        CallMismatchFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void e() {
        CallMismatchFrameEvent __e("e");
        CallMismatchFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

// Stub functions for placeholder calls
void native() {}
void x() {}

// TAP test harness
int main() {
    printf("TAP version 14\n");
    printf("1..1\n");
    try {
        CallMismatch s;
        s.e();
        printf("ok 1 - actions_call_wrappers\n");
    } catch (...) {
        printf("not ok 1 - actions_call_wrappers\n");
    }
    return 0;
}
