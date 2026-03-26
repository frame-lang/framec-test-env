#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class SFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SFrameContext {
public:
    SFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SFrameContext(SFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SFrameEvent> forward_event;
    std::unique_ptr<SCompartment> parent_compartment;

    explicit SCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<SCompartment> clone() const {
        auto c = std::make_unique<SCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class S {
private:
    std::vector<std::unique_ptr<SCompartment>> _state_stack;
    std::unique_ptr<SCompartment> __compartment;
    std::unique_ptr<SCompartment> __next_compartment;
    std::vector<SFrameContext> _context_stack;

    void __kernel(SFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        }
    }

    void __transition(std::unique_ptr<SCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_A(SFrameEvent& __e) {
        if (__e._message == "e") {
            if (true) {
                _state_stack.push_back(__compartment->clone());
                auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
                __transition(std::move(__popped));
                return;
            } else {
                _state_stack.push_back(__compartment->clone());
                auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
                __transition(std::move(__popped));
                return;
            auto __new_compartment = std::make_unique<SCompartment>("B");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
            }
        }
    }

    void _state_B(SFrameEvent& __e) {
        if (__e._message == "e") {
        }
    }

public:
    S() {
        __compartment = std::make_unique<SCompartment>("A");
        SFrameEvent __frame_event("$>");
        SFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void e() {
        SFrameEvent __e("e");
        SFrameContext __ctx(std::move(__e));
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
        S s;
        s.e();
        printf("ok 1 - nested_stack_then_transition\n");
    } catch (...) {
        printf("not ok 1 - nested_stack_then_transition\n");
    }
    return 0;
}
