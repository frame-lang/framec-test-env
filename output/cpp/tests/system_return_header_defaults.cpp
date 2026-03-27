#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class SystemReturnHeaderDefaultsCppFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SystemReturnHeaderDefaultsCppFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SystemReturnHeaderDefaultsCppFrameContext {
public:
    SystemReturnHeaderDefaultsCppFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SystemReturnHeaderDefaultsCppFrameContext(SystemReturnHeaderDefaultsCppFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SystemReturnHeaderDefaultsCppCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SystemReturnHeaderDefaultsCppFrameEvent> forward_event;
    std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment> parent_compartment;

    explicit SystemReturnHeaderDefaultsCppCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment> clone() const {
        auto c = std::make_unique<SystemReturnHeaderDefaultsCppCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class SystemReturnHeaderDefaultsCpp {
private:
    std::vector<std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment>> _state_stack;
    std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment> __compartment;
    std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment> __next_compartment;
    std::vector<SystemReturnHeaderDefaultsCppFrameContext> _context_stack;

    void __kernel(SystemReturnHeaderDefaultsCppFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SystemReturnHeaderDefaultsCppFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SystemReturnHeaderDefaultsCppFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SystemReturnHeaderDefaultsCppFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SystemReturnHeaderDefaultsCppFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        }
    }

    void __transition(std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(SystemReturnHeaderDefaultsCppFrameEvent& __e) {
        if (__e._message == "a1") {
            if (x < 5) {
                return;
            } else {
                _context_stack.back()._return = std::any(0);
                return;;
            }
        } else if (__e._message == "a2") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            return;
        } else if (__e._message == "a3") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            _context_stack.back()._return = std::any(a);
            return;;
        }
    }

    void bump_x(int delta) {
                    x = x + delta;
    }

public:
    int x = 3;

    SystemReturnHeaderDefaultsCpp() {
        __compartment = std::make_unique<SystemReturnHeaderDefaultsCppCompartment>("Idle");
        SystemReturnHeaderDefaultsCppFrameEvent __frame_event("$>");
        SystemReturnHeaderDefaultsCppFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int a1() {
        SystemReturnHeaderDefaultsCppFrameEvent __e("a1");
        SystemReturnHeaderDefaultsCppFrameContext __ctx(std::move(__e), std::any(10));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int a2(int a) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        SystemReturnHeaderDefaultsCppFrameEvent __e("a2", std::move(__params));
        SystemReturnHeaderDefaultsCppFrameContext __ctx(std::move(__e), std::any(a));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int a3(int a) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        SystemReturnHeaderDefaultsCppFrameEvent __e("a3", std::move(__params));
        SystemReturnHeaderDefaultsCppFrameContext __ctx(std::move(__e), std::any(x + a));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

// TAP test harness
int main() {
    printf("TAP version 14\n");
    printf("1..1\n");
    try {
        SystemReturnHeaderDefaultsCpp s;
        if (s.a1() != 10) {
            printf("not ok 1 - system_return_header_defaults # a1() default failed\n");
            return 1;
        }
        if (s.a2(42) != 42) {
            printf("not ok 1 - system_return_header_defaults # a2(42) default failed\n");
            return 1;
        }
        if (s.a3(7) != 7) {
            printf("not ok 1 - system_return_header_defaults # a3(7) failed, got %d\n", s.a3(7));
            return 1;
        }
        printf("ok 1 - system_return_header_defaults\n");
    } catch (...) {
        printf("not ok 1 - system_return_header_defaults\n");
    }
    return 0;
}
