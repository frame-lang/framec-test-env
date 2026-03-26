#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


// Test: Equality operators in Frame handlers
// Tests: ==, !=

#include <iostream>
#include <string>
#include <cassert>

class EqualityTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    EqualityTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class EqualityTestFrameContext {
public:
    EqualityTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    EqualityTestFrameContext(EqualityTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class EqualityTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<EqualityTestFrameEvent> forward_event;
    std::unique_ptr<EqualityTestCompartment> parent_compartment;

    explicit EqualityTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<EqualityTestCompartment> clone() const {
        auto c = std::make_unique<EqualityTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class EqualityTest {
private:
    std::vector<std::unique_ptr<EqualityTestCompartment>> _state_stack;
    std::unique_ptr<EqualityTestCompartment> __compartment;
    std::unique_ptr<EqualityTestCompartment> __next_compartment;
    std::vector<EqualityTestFrameContext> _context_stack;

    void __kernel(EqualityTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            EqualityTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                EqualityTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    EqualityTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(EqualityTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<EqualityTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(EqualityTestFrameEvent& __e) {
        if (__e._message == "set_values") {
            auto x = std::any_cast<int>(__e._parameters.at("x"));
            auto y = std::any_cast<int>(__e._parameters.at("y"));
            a = x;
            b = y;
        } else if (__e._message == "test_equal") {
            if (a == b) {
                _context_stack.back()._return = std::any(true);
            } else {
                _context_stack.back()._return = std::any(false);
            }
        } else if (__e._message == "test_not_equal") {
            if (a != b) {
                _context_stack.back()._return = std::any(true);
            } else {
                _context_stack.back()._return = std::any(false);
            }
        }
    }

public:
    int a = 5;
    int b = 5;

    EqualityTest() {
        __compartment = std::make_unique<EqualityTestCompartment>("Ready");
        EqualityTestFrameEvent __frame_event("$>");
        EqualityTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    bool test_equal() {
        EqualityTestFrameEvent __e("test_equal");
        EqualityTestFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    bool test_not_equal() {
        EqualityTestFrameEvent __e("test_not_equal");
        EqualityTestFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void set_values(int x, int y) {
        std::unordered_map<std::string, std::any> __params;
        __params["x"] = x;
        __params["y"] = y;
        EqualityTestFrameEvent __e("set_values", std::move(__params));
        EqualityTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

int main() {
    printf("TAP version 14\n");
    printf("1..4\n");

    EqualityTest s;

    // a=5, b=5: 5 == 5 is true
    if (s.test_equal()) {
        printf("ok 1 - 5 == 5 is true\n");
    } else {
        printf("not ok 1 - 5 == 5 is true\n");
    }

    // a=5, b=5: 5 != 5 is false
    if (!s.test_not_equal()) {
        printf("ok 2 - 5 != 5 is false\n");
    } else {
        printf("not ok 2 - 5 != 5 is false\n");
    }

    // Change values: a=5, b=3
    s.set_values(5, 3);

    // a=5, b=3: 5 == 3 is false
    if (!s.test_equal()) {
        printf("ok 3 - 5 == 3 is false\n");
    } else {
        printf("not ok 3 - 5 == 3 is false\n");
    }

    // a=5, b=3: 5 != 3 is true
    if (s.test_not_equal()) {
        printf("ok 4 - 5 != 3 is true\n");
    } else {
        printf("not ok 4 - 5 != 3 is true\n");
    }

    return 0;
}
