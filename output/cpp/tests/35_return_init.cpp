#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Test: Interface method return_init
// Validates that interface methods can have default return values

class ReturnInitTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ReturnInitTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ReturnInitTestFrameContext {
public:
    ReturnInitTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ReturnInitTestFrameContext(ReturnInitTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ReturnInitTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ReturnInitTestFrameEvent> forward_event;
    std::unique_ptr<ReturnInitTestCompartment> parent_compartment;

    explicit ReturnInitTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<ReturnInitTestCompartment> clone() const {
        auto c = std::make_unique<ReturnInitTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class ReturnInitTest {
private:
    std::vector<std::unique_ptr<ReturnInitTestCompartment>> _state_stack;
    std::unique_ptr<ReturnInitTestCompartment> __compartment;
    std::unique_ptr<ReturnInitTestCompartment> __next_compartment;
    std::vector<ReturnInitTestFrameContext> _context_stack;

    void __kernel(ReturnInitTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ReturnInitTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ReturnInitTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ReturnInitTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ReturnInitTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    void __transition(std::unique_ptr<ReturnInitTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(ReturnInitTestFrameEvent& __e) {
        if (__e._message == "$>") {
            // Start state enter (no-op)
        } else if (__e._message == "get_count") {
            // Don't set return - should use default 0
        } else if (__e._message == "get_flag") {
            // Don't set return - should use default false
        } else if (__e._message == "get_status") {
            // Don't set return - should use default "unknown"
        } else if (__e._message == "trigger") {
            auto __new_compartment = std::make_unique<ReturnInitTestCompartment>("Active");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Active(ReturnInitTestFrameEvent& __e) {
        if (__e._message == "$>") {
            // Active state enter (no-op)
        } else if (__e._message == "get_count") {
            _context_stack.back()._return = std::any(42);
        } else if (__e._message == "get_flag") {
            _context_stack.back()._return = std::any(true);
        } else if (__e._message == "get_status") {
            _context_stack.back()._return = std::any(std::string("active"));
        } else if (__e._message == "trigger") {
            auto __new_compartment = std::make_unique<ReturnInitTestCompartment>("Start");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    ReturnInitTest() {
        __compartment = std::make_unique<ReturnInitTestCompartment>("Start");
        ReturnInitTestFrameEvent __frame_event("$>");
        ReturnInitTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_status() {
        ReturnInitTestFrameEvent __e("get_status");
        ReturnInitTestFrameContext __ctx(std::move(__e), std::any(std::string("unknown")));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_count() {
        ReturnInitTestFrameEvent __e("get_count");
        ReturnInitTestFrameContext __ctx(std::move(__e), std::any(0));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    bool get_flag() {
        ReturnInitTestFrameEvent __e("get_flag");
        ReturnInitTestFrameContext __ctx(std::move(__e), std::any(false));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void trigger() {
        ReturnInitTestFrameEvent __e("trigger");
        ReturnInitTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

int main() {
    printf("TAP version 14\n");
    printf("1..6\n");

    ReturnInitTest s;

    // Test 1: Default string return
    if (s.get_status() == "unknown") {
        printf("ok 1 - default string return is 'unknown'\n");
    } else {
        printf("not ok 1 - default string return is 'unknown'\n");
    }

    // Test 2: Default int return
    if (s.get_count() == 0) {
        printf("ok 2 - default int return is 0\n");
    } else {
        printf("not ok 2 - default int return is 0\n");
    }

    // Test 3: Default bool return
    if (s.get_flag() == false) {
        printf("ok 3 - default bool return is false\n");
    } else {
        printf("not ok 3 - default bool return is false\n");
    }

    s.trigger();

    // Test 4: Explicit string return overrides default
    if (s.get_status() == "active") {
        printf("ok 4 - explicit return overrides default string\n");
    } else {
        printf("not ok 4 - explicit return overrides default string\n");
    }

    // Test 5: Explicit int return overrides default
    if (s.get_count() == 42) {
        printf("ok 5 - explicit return overrides default int\n");
    } else {
        printf("not ok 5 - explicit return overrides default int\n");
    }

    // Test 6: Explicit bool return overrides default
    if (s.get_flag() == true) {
        printf("ok 6 - explicit return overrides default bool\n");
    } else {
        printf("not ok 6 - explicit return overrides default bool\n");
    }

    printf("# PASS - return_init provides default return values\n");
    return 0;
}
