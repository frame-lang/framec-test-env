#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


// Test: Ternary/conditional expressions in Frame handlers
// C++ uses: cond ? a : b

#include <iostream>
#include <string>
#include <cassert>

class TernaryTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    TernaryTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class TernaryTestFrameContext {
public:
    TernaryTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    TernaryTestFrameContext(TernaryTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class TernaryTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<TernaryTestFrameEvent> forward_event;
    std::unique_ptr<TernaryTestCompartment> parent_compartment;

    explicit TernaryTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<TernaryTestCompartment> clone() const {
        auto c = std::make_unique<TernaryTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class TernaryTest {
private:
    std::vector<std::unique_ptr<TernaryTestCompartment>> _state_stack;
    std::unique_ptr<TernaryTestCompartment> __compartment;
    std::unique_ptr<TernaryTestCompartment> __next_compartment;
    std::vector<TernaryTestFrameContext> _context_stack;

    void __kernel(TernaryTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            TernaryTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                TernaryTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    TernaryTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(TernaryTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<TernaryTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(TernaryTestFrameEvent& __e) {
        if (__e._message == "get_value") {
            auto result = cond ? 100 : 200;
            _context_stack.back()._return = std::any(result);
        } else if (__e._message == "set_condition") {
            auto c = std::any_cast<bool>(__e._parameters.at("c"));
            cond = c;
        }
    }

public:
    bool cond = true;

    TernaryTest() {
        __compartment = std::make_unique<TernaryTestCompartment>("Ready");
        TernaryTestFrameEvent __frame_event("$>");
        TernaryTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_value() {
        TernaryTestFrameEvent __e("get_value");
        TernaryTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void set_condition(bool c) {
        std::unordered_map<std::string, std::any> __params;
        __params["c"] = c;
        TernaryTestFrameEvent __e("set_condition", std::move(__params));
        TernaryTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

int main() {
    printf("TAP version 14\n");
    printf("1..2\n");

    TernaryTest s;

    // cond=true: should return 100
    auto v1 = s.get_value();
    if (v1 == 100) {
        printf("ok 1 - cond=true returns 100\n");
    } else {
        printf("not ok 1 - cond=true returns 100 # got %d\n", v1);
    }

    // cond=false: should return 200
    s.set_condition(false);
    auto v2 = s.get_value();
    if (v2 == 200) {
        printf("ok 2 - cond=false returns 200\n");
    } else {
        printf("not ok 2 - cond=false returns 200 # got %d\n", v2);
    }

    return 0;
}
