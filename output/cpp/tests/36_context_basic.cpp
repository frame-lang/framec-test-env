#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

// Test: Basic System Context Access
// Validates @@.param, @@:return, @@:event syntax

class ContextBasicTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ContextBasicTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ContextBasicTestFrameContext {
public:
    ContextBasicTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ContextBasicTestFrameContext(ContextBasicTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ContextBasicTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ContextBasicTestFrameEvent> forward_event;
    std::unique_ptr<ContextBasicTestCompartment> parent_compartment;

    explicit ContextBasicTestCompartment(const std::string& state) : state(state) {}
};

class ContextBasicTest {
private:
    std::unique_ptr<ContextBasicTestCompartment> __compartment;
    std::unique_ptr<ContextBasicTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<ContextBasicTestCompartment>> _state_stack;
    std::vector<ContextBasicTestFrameContext> _context_stack;

    void __kernel(ContextBasicTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ContextBasicTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ContextBasicTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ContextBasicTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ContextBasicTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<ContextBasicTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(ContextBasicTestFrameEvent& __e) {
        if (__e._message == "add") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            {
            _context_stack.back()._return = @@.a + @@.b;
            }
            return;
        } else if (__e._message == "get_event_name") {
            {
            _context_stack.back()._return = @@:event;
            }
            return;
        } else if (__e._message == "greet") {
            auto name = std::any_cast<std::string>(__e._parameters.at("name"));
            {
            std::string result = std::string("Hello, ") + @@.name + "!";
            _context_stack.back()._return = result;
            }
            return;
        }
    }

public:
    ContextBasicTest() {
        __compartment = std::make_unique<ContextBasicTestCompartment>("Ready");
        ContextBasicTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int add(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        ContextBasicTestFrameEvent __e("add", std::move(__params));
        ContextBasicTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_event_name() {
        ContextBasicTestFrameEvent __e("get_event_name");
        ContextBasicTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string greet(std::string name) {
        std::unordered_map<std::string, std::any> __params;
        __params["name"] = name;
        ContextBasicTestFrameEvent __e("greet", std::move(__params));
        ContextBasicTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 36: Context Basic ===\n");
    ContextBasicTest s;

    int result1 = s.add(3, 5);
    if (result1 != 8) {
        printf("FAIL: Expected 8, got %d\n", result1);
        assert(false);
    }
    printf("1. add(3, 5) = %d\n", result1);

    std::string eventName = s.get_event_name();
    if (eventName != "get_event_name") {
        printf("FAIL: Expected 'get_event_name', got '%s'\n", eventName.c_str());
        assert(false);
    }
    printf("2. @@:event = '%s'\n", eventName.c_str());

    std::string greeting = s.greet("World");
    if (greeting != "Hello, World!") {
        printf("FAIL: Expected 'Hello, World!', got '%s'\n", greeting.c_str());
        assert(false);
    }
    printf("3. greet('World') = '%s'\n", greeting.c_str());

    printf("PASS: Context basic access works correctly\n");
    return 0;
}
