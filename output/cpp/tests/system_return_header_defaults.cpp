#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


// capability: @@:return header defaults and handler returns (C++).
//
// This fixture exercises:
// - Interface header defaults: a1(): int = 10, a2(a): int = a
// - Handler bodies that use:
//   - bare `return` (leave @@:return at the header default)
//   - `return expr` sugar (override @@:return)

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
};

class SystemReturnHeaderDefaultsCpp {
private:
    std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment> __compartment;
    std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment> __next_compartment;
    std::vector<std::unique_ptr<SystemReturnHeaderDefaultsCppCompartment>> _state_stack;
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
            {
            // Return default (10)
            return;
            }
            return;
        } else if (__e._message == "a2") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            {
            // Return default (parameter a)
            return;
            }
            return;
        } else if (__e._message == "a3") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            {
            // Override with explicit return
            _context_stack.back()._return = a * 2;
            return;
            }
            return;
        }
    }

public:
    SystemReturnHeaderDefaultsCpp() {
        __compartment = std::make_unique<SystemReturnHeaderDefaultsCppCompartment>("Idle");
        SystemReturnHeaderDefaultsCppFrameEvent __frame_event("$>");
        __kernel(__frame_event);
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
        SystemReturnHeaderDefaultsCppFrameContext __ctx(std::move(__e), std::any(a + 5));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

// TAP test harness
int main() {
    std::cout << "TAP version 14" << std::endl;
    std::cout << "1..1" << std::endl;

    SystemReturnHeaderDefaultsCpp s;

    // Test a1() - should return default 10
    int r1 = s.a1();
    if (r1 != 10) {
        std::cout << "not ok 1 - system_return_header_defaults # a1() expected 10, got " << r1 << std::endl;
        return 1;
    }

    // Test a2(5) - should return default which is 'a' (5)
    int r2 = s.a2(5);
    if (r2 != 5) {
        std::cout << "not ok 1 - system_return_header_defaults # a2(5) expected 5, got " << r2 << std::endl;
        return 1;
    }

    // Test a3(7) - returns explicit a*2 (14), not the default a+5 (12)
    int r3 = s.a3(7);
    if (r3 != 14) {
        std::cout << "not ok 1 - system_return_header_defaults # a3(7) expected 14, got " << r3 << std::endl;
        return 1;
    }

    std::cout << "ok 1 - system_return_header_defaults" << std::endl;

    return 0;
}
