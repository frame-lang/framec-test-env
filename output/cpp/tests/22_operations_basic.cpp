#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class OperationsTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    OperationsTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class OperationsTestFrameContext {
public:
    OperationsTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    OperationsTestFrameContext(OperationsTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class OperationsTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<OperationsTestFrameEvent> forward_event;
    std::unique_ptr<OperationsTestCompartment> parent_compartment;

    explicit OperationsTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<OperationsTestCompartment> clone() const {
        auto c = std::make_unique<OperationsTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class OperationsTest {
private:
    std::vector<std::unique_ptr<OperationsTestCompartment>> _state_stack;
    std::unique_ptr<OperationsTestCompartment> __compartment;
    std::unique_ptr<OperationsTestCompartment> __next_compartment;
    std::vector<OperationsTestFrameContext> _context_stack;

    void __kernel(OperationsTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            OperationsTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                OperationsTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    OperationsTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(OperationsTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<OperationsTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(OperationsTestFrameEvent& __e) {
        if (__e._message == "compute") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            int sum_val = this->add(a, b);
            int prod_val = this->multiply(a, b);
            int last_result = sum_val + prod_val;
            _context_stack.back()._return = std::any(last_result);
            return;;
        } else if (__e._message == "get_last_result") {
            _context_stack.back()._return = std::any(last_result);
            return;;
        }
    }

public:
    int last_result = 0;

    OperationsTest() {
        __compartment = std::make_unique<OperationsTestCompartment>("Ready");
        OperationsTestFrameEvent __frame_event("$>");
        OperationsTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int compute(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        OperationsTestFrameEvent __e("compute", std::move(__params));
        OperationsTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_last_result() {
        OperationsTestFrameEvent __e("get_last_result");
        OperationsTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int add(int x, int y) {
                    return x + y;
    }

    int multiply(int x, int y) {
                    return x * y;
    }

    static int factorial(int n) {
                    if (n <= 1) {
                        return 1;
                    }
                    return n * OperationsTest::factorial(n - 1);
    }

    static bool is_even(int n) {
                    return n % 2 == 0;
    }
};

int main() {
    printf("=== Test 22: Operations Basic (C++) ===\n");
    OperationsTest s;

    // Test 1: Instance operations
    int result = s.add(3, 4);
    if (result != 7) {
        printf("FAIL: Expected 7, got %d\n", result);
        assert(false);
    }
    printf("1. add(3, 4) = %d\n", result);

    result = s.multiply(3, 4);
    if (result != 12) {
        printf("FAIL: Expected 12, got %d\n", result);
        assert(false);
    }
    printf("2. multiply(3, 4) = %d\n", result);

    // Test 2: Operations used in handler
    result = s.compute(3, 4);
    if (result != 19) {
        printf("FAIL: Expected 19, got %d\n", result);
        assert(false);
    }
    printf("3. compute(3, 4) = %d\n", result);

    // Test 3: Static operations
    result = OperationsTest::factorial(5);
    if (result != 120) {
        printf("FAIL: Expected 120, got %d\n", result);
        assert(false);
    }
    printf("4. factorial(5) = %d\n", result);

    bool is_even = OperationsTest::is_even(4);
    if (is_even != true) {
        printf("FAIL: Expected true\n");
        assert(false);
    }
    printf("5. is_even(4) = true\n");

    is_even = OperationsTest::is_even(7);
    if (is_even != false) {
        printf("FAIL: Expected false\n");
        assert(false);
    }
    printf("6. is_even(7) = false\n");

    result = OperationsTest::factorial(4);
    if (result != 24) {
        printf("FAIL: Expected 24, got %d\n", result);
        assert(false);
    }
    printf("7. OperationsTest::factorial(4) = %d\n", result);

    printf("PASS: Operations basic works correctly\n");
    return 0;
}
