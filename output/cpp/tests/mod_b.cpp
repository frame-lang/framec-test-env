#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class S2FrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    S2FrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class S2FrameContext {
public:
    S2FrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    S2FrameContext(S2FrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class S2Compartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<S2FrameEvent> forward_event;
    std::unique_ptr<S2Compartment> parent_compartment;

    explicit S2Compartment(const std::string& state) : state(state) {}

    std::unique_ptr<S2Compartment> clone() const {
        auto c = std::make_unique<S2Compartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class S2 {
private:
    std::vector<std::unique_ptr<S2Compartment>> _state_stack;
    std::unique_ptr<S2Compartment> __compartment;
    std::unique_ptr<S2Compartment> __next_compartment;
    std::vector<S2FrameContext> _context_stack;

    void __kernel(S2FrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            S2FrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                S2FrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    S2FrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(S2FrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "A") {
            _state_A(__e);
        }
    }

    void __transition(std::unique_ptr<S2Compartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_A(S2FrameEvent& __e) {
        if (__e._message == "e") {
            auto __new_compartment = std::make_unique<S2Compartment>("A");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    S2() {
        __compartment = std::make_unique<S2Compartment>("A");
        S2FrameEvent __frame_event("$>");
        S2FrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void e() {
        S2FrameEvent __e("e");
        S2FrameContext __ctx(std::move(__e));
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
        S2 s;
        s.e();
        printf("ok 1 - mod_b\n");
    } catch (...) {
        printf("not ok 1 - mod_b\n");
    }
    return 0;
}
