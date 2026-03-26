#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


// Test: Logical operators in Frame handlers
// Tests: &&, ||, !

#include <iostream>
#include <string>
#include <cassert>

class LogicalTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    LogicalTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class LogicalTestFrameContext {
public:
    LogicalTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    LogicalTestFrameContext(LogicalTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class LogicalTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<LogicalTestFrameEvent> forward_event;
    std::unique_ptr<LogicalTestCompartment> parent_compartment;

    explicit LogicalTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<LogicalTestCompartment> clone() const {
        auto c = std::make_unique<LogicalTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class LogicalTest {
private:
    std::vector<std::unique_ptr<LogicalTestCompartment>> _state_stack;
    std::unique_ptr<LogicalTestCompartment> __compartment;
    std::unique_ptr<LogicalTestCompartment> __next_compartment;
    std::vector<LogicalTestFrameContext> _context_stack;

    void __kernel(LogicalTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            LogicalTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                LogicalTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    LogicalTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(LogicalTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<LogicalTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(LogicalTestFrameEvent& __e) {
        if (__e._message == "set_values") {
            auto x = std::any_cast<bool>(__e._parameters.at("x"));
            auto y = std::any_cast<bool>(__e._parameters.at("y"));
            a = x;
            b = y;
        } else if (__e._message == "test_and") {
            if (a && b) {
                _context_stack.back()._return = std::any(true);
            } else {
                _context_stack.back()._return = std::any(false);
            }
        } else if (__e._message == "test_not") {
            if (!a) {
                _context_stack.back()._return = std::any(true);
            } else {
                _context_stack.back()._return = std::any(false);
            }
        } else if (__e._message == "test_or") {
            if (a || b) {
                _context_stack.back()._return = std::any(true);
            } else {
                _context_stack.back()._return = std::any(false);
            }
        }
    }

public:
    bool a = true;
    bool b = false;

    LogicalTest() {
        __compartment = std::make_unique<LogicalTestCompartment>("Ready");
        LogicalTestFrameEvent __frame_event("$>");
        LogicalTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    bool test_and() {
        LogicalTestFrameEvent __e("test_and");
        LogicalTestFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    bool test_or() {
        LogicalTestFrameEvent __e("test_or");
        LogicalTestFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    bool test_not() {
        LogicalTestFrameEvent __e("test_not");
        LogicalTestFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void set_values(bool x, bool y) {
        std::unordered_map<std::string, std::any> __params;
        __params["x"] = x;
        __params["y"] = y;
        LogicalTestFrameEvent __e("set_values", std::move(__params));
        LogicalTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

int main() {
    printf("TAP version 14\n");
    printf("1..6\n");

    LogicalTest s;

    // a=true, b=false: true && false = false
    if (!s.test_and()) {
        printf("ok 1 - true && false is false\n");
    } else {
        printf("not ok 1 - true && false is false\n");
    }

    // a=true, b=false: true || false = true
    if (s.test_or()) {
        printf("ok 2 - true || false is true\n");
    } else {
        printf("not ok 2 - true || false is true\n");
    }

    // a=true: !true = false
    if (!s.test_not()) {
        printf("ok 3 - !true is false\n");
    } else {
        printf("not ok 3 - !true is false\n");
    }

    // Change values: a=true, b=true
    s.set_values(true, true);

    // true && true = true
    if (s.test_and()) {
        printf("ok 4 - true && true is true\n");
    } else {
        printf("not ok 4 - true && true is true\n");
    }

    // Change values: a=false, b=false
    s.set_values(false, false);

    // false || false = false
    if (!s.test_or()) {
        printf("ok 5 - false || false is false\n");
    } else {
        printf("not ok 5 - false || false is false\n");
    }

    // !false = true
    if (s.test_not()) {
        printf("ok 6 - !false is true\n");
    } else {
        printf("not ok 6 - !false is true\n");
    }

    return 0;
}
