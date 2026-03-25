#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <cassert>

// NOTE: Default return value syntax (method(): type = default) not yet implemented.
// This test validates behavior when handler doesn't set @@:return.

class SystemReturnDefaultTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SystemReturnDefaultTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SystemReturnDefaultTestFrameContext {
public:
    SystemReturnDefaultTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SystemReturnDefaultTestFrameContext(SystemReturnDefaultTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SystemReturnDefaultTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SystemReturnDefaultTestFrameEvent> forward_event;
    std::unique_ptr<SystemReturnDefaultTestCompartment> parent_compartment;

    explicit SystemReturnDefaultTestCompartment(const std::string& state) : state(state) {}
};

class SystemReturnDefaultTest {
private:
    std::unique_ptr<SystemReturnDefaultTestCompartment> __compartment;
    std::unique_ptr<SystemReturnDefaultTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<SystemReturnDefaultTestCompartment>> _state_stack;
    std::vector<SystemReturnDefaultTestFrameContext> _context_stack;

    void __kernel(SystemReturnDefaultTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SystemReturnDefaultTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SystemReturnDefaultTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SystemReturnDefaultTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SystemReturnDefaultTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<SystemReturnDefaultTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(SystemReturnDefaultTestFrameEvent& __e) {
        if (__e._message == "handler_sets_value") {
            {
            _context_stack.back()._return = 42;
            return;
            }
            return;
        } else if (__e._message == "handler_no_return") {
            {
            // Does not set return - should return 0 (default)
            __compartment->state_vars["count"] = std::any(std::any_cast<int>(__compartment->state_vars["count"]) + 1);
            }
            return;
        } else if (__e._message == "get_count") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["count"]);
            return;
            }
            return;
        }
    }

public:
    SystemReturnDefaultTest() {
        __compartment = std::make_unique<SystemReturnDefaultTestCompartment>("Start");
        __compartment->state_vars["count"] = 0;
        SystemReturnDefaultTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int handler_sets_value() {
        SystemReturnDefaultTestFrameEvent __e("handler_sets_value");
        SystemReturnDefaultTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int handler_no_return() {
        SystemReturnDefaultTestFrameEvent __e("handler_no_return");
        SystemReturnDefaultTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_count() {
        SystemReturnDefaultTestFrameEvent __e("get_count");
        SystemReturnDefaultTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 14: System Return Default Behavior ===" << std::endl;
    SystemReturnDefaultTest s;

    // Test 1: Handler explicitly sets return value
    int result = s.handler_sets_value();
    assert(result == 42);
    std::cout << "1. handler_sets_value() = " << result << std::endl;

    // Test 2: Handler does NOT set return - should return 0 (default)
    result = s.handler_no_return();
    assert(result == 0);
    std::cout << "2. handler_no_return() = " << result << std::endl;

    // Test 3: Verify handler was called (side effect check)
    int count = s.get_count();
    assert(count == 1);
    std::cout << "3. Handler was called, count = " << count << std::endl;

    // Test 4: Call again to verify idempotence
    result = s.handler_no_return();
    assert(result == 0);
    count = s.get_count();
    assert(count == 2);
    std::cout << "4. Second call: result=" << result << ", count=" << count << std::endl;

    std::cout << "PASS: System return default behavior works correctly" << std::endl;
    return 0;
}
