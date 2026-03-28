#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class WithTransitionFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    WithTransitionFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class WithTransitionFrameContext {
public:
    WithTransitionFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    WithTransitionFrameContext(WithTransitionFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class WithTransitionCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<WithTransitionFrameEvent> forward_event;
    std::unique_ptr<WithTransitionCompartment> parent_compartment;

    explicit WithTransitionCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<WithTransitionCompartment> clone() const {
        auto c = std::make_unique<WithTransitionCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class WithTransition {
private:
    std::vector<std::unique_ptr<WithTransitionCompartment>> _state_stack;
    std::unique_ptr<WithTransitionCompartment> __compartment;
    std::unique_ptr<WithTransitionCompartment> __next_compartment;
    std::vector<WithTransitionFrameContext> _context_stack;

    void __kernel(WithTransitionFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            WithTransitionFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                WithTransitionFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    WithTransitionFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(WithTransitionFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "First") {
            _state_First(__e);
        } else if (state_name == "Second") {
            _state_Second(__e);
        }
    }

    void __transition(std::unique_ptr<WithTransitionCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Second(WithTransitionFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Second"));
            return;;
        } else if (__e._message == "next") {
            printf("Transitioning: Second -> First\n");
            auto __new_compartment = std::make_unique<WithTransitionCompartment>("First");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_First(WithTransitionFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("First"));
            return;;
        } else if (__e._message == "next") {
            printf("Transitioning: First -> Second\n");
            auto __new_compartment = std::make_unique<WithTransitionCompartment>("Second");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    WithTransition() {
        __compartment = std::make_unique<WithTransitionCompartment>("First");
        WithTransitionFrameEvent __frame_event("$>");
        WithTransitionFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void next() {
        WithTransitionFrameEvent __e("next");
        WithTransitionFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        WithTransitionFrameEvent __e("get_state");
        WithTransitionFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 03: State Transitions ===\n");
    WithTransition s;

    std::string state = s.get_state();
    if (state != "First") {
        printf("FAIL: Expected 'First', got '%s'\n", state.c_str());
        assert(false);
    }
    printf("Initial state: %s\n", state.c_str());

    s.next();
    state = s.get_state();
    if (state != "Second") {
        printf("FAIL: Expected 'Second', got '%s'\n", state.c_str());
        assert(false);
    }
    printf("After first next(): %s\n", state.c_str());

    s.next();
    state = s.get_state();
    if (state != "First") {
        printf("FAIL: Expected 'First', got '%s'\n", state.c_str());
        assert(false);
    }
    printf("After second next(): %s\n", state.c_str());

    printf("PASS: State transitions work correctly\n");
    return 0;
}
