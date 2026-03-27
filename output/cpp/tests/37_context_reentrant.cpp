#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Test: Context Stack Reentrancy
// Validates that nested interface calls maintain separate contexts

class ContextReentrantTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ContextReentrantTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ContextReentrantTestFrameContext {
public:
    ContextReentrantTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ContextReentrantTestFrameContext(ContextReentrantTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ContextReentrantTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ContextReentrantTestFrameEvent> forward_event;
    std::unique_ptr<ContextReentrantTestCompartment> parent_compartment;

    explicit ContextReentrantTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<ContextReentrantTestCompartment> clone() const {
        auto c = std::make_unique<ContextReentrantTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class ContextReentrantTest {
private:
    std::vector<std::unique_ptr<ContextReentrantTestCompartment>> _state_stack;
    std::unique_ptr<ContextReentrantTestCompartment> __compartment;
    std::unique_ptr<ContextReentrantTestCompartment> __next_compartment;
    std::vector<ContextReentrantTestFrameContext> _context_stack;

    void __kernel(ContextReentrantTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ContextReentrantTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ContextReentrantTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ContextReentrantTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ContextReentrantTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<ContextReentrantTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(ContextReentrantTestFrameEvent& __e) {
        if (__e._message == "deeply_nested") {
            auto z = std::any_cast<int>(__e._parameters.at("z"));
            std::string outer_result = this->outer(z);
            _context_stack.back()._return = std::any(std::string("deep:") + std::to_string(z) + "," + outer_result);
        } else if (__e._message == "get_both") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            std::string result_a = this->inner(a);
            std::string result_b = this->inner(b);
            _context_stack.back()._return = std::any(std::string("a=") + std::to_string(a) + ",b=" + std::to_string(b) + ",results=" + result_a + "+" + result_b);
        } else if (__e._message == "inner") {
            auto y = std::any_cast<int>(__e._parameters.at("y"));
            _context_stack.back()._return = std::any(std::to_string(y));
        } else if (__e._message == "outer") {
            auto x = std::any_cast<int>(__e._parameters.at("x"));
            _context_stack.back()._return = std::any(std::string("outer_initial"));
            std::string inner_result = this->inner(x * 10);
            _context_stack.back()._return = std::any(std::string("outer:") + std::to_string(x) + ",inner:" + inner_result);
        }
    }

public:
    ContextReentrantTest() {
        __compartment = std::make_unique<ContextReentrantTestCompartment>("Ready");
        ContextReentrantTestFrameEvent __frame_event("$>");
        ContextReentrantTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string outer(int x) {
        std::unordered_map<std::string, std::any> __params;
        __params["x"] = x;
        ContextReentrantTestFrameEvent __e("outer", std::move(__params));
        ContextReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string inner(int y) {
        std::unordered_map<std::string, std::any> __params;
        __params["y"] = y;
        ContextReentrantTestFrameEvent __e("inner", std::move(__params));
        ContextReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string deeply_nested(int z) {
        std::unordered_map<std::string, std::any> __params;
        __params["z"] = z;
        ContextReentrantTestFrameEvent __e("deeply_nested", std::move(__params));
        ContextReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_both(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        ContextReentrantTestFrameEvent __e("get_both", std::move(__params));
        ContextReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 37: Context Reentrant ===\n");
    ContextReentrantTest s;

    // Test 1: Simple nesting
    std::string result = s.outer(5);
    std::string expected = "outer:5,inner:50";
    if (result != expected) {
        printf("FAIL: Expected '%s', got '%s'\n", expected.c_str(), result.c_str());
        assert(false);
    }
    printf("1. outer(5) = '%s'\n", result.c_str());

    // Test 2: Inner alone
    result = s.inner(42);
    if (result != "42") {
        printf("FAIL: Expected '42', got '%s'\n", result.c_str());
        assert(false);
    }
    printf("2. inner(42) = '%s'\n", result.c_str());

    // Test 3: Deep nesting
    result = s.deeply_nested(3);
    expected = "deep:3,outer:3,inner:30";
    if (result != expected) {
        printf("FAIL: Expected '%s', got '%s'\n", expected.c_str(), result.c_str());
        assert(false);
    }
    printf("3. deeply_nested(3) = '%s'\n", result.c_str());

    // Test 4: Multiple inner calls
    result = s.get_both(10, 20);
    expected = "a=10,b=20,results=10+20";
    if (result != expected) {
        printf("FAIL: Expected '%s', got '%s'\n", expected.c_str(), result.c_str());
        assert(false);
    }
    printf("4. get_both(10, 20) = '%s'\n", result.c_str());

    printf("PASS: Context reentrant works correctly\n");
    return 0;
}
