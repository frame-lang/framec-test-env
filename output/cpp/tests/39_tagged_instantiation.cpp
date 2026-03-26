#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

// Test 39: Tagged System Instantiation
// Validates the @@System() syntax for tracked instantiation

class CalculatorFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    CalculatorFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class CalculatorFrameContext {
public:
    CalculatorFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    CalculatorFrameContext(CalculatorFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class CalculatorCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<CalculatorFrameEvent> forward_event;
    std::unique_ptr<CalculatorCompartment> parent_compartment;

    explicit CalculatorCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<CalculatorCompartment> clone() const {
        auto c = std::make_unique<CalculatorCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class Calculator {
private:
    std::vector<std::unique_ptr<CalculatorCompartment>> _state_stack;
    std::unique_ptr<CalculatorCompartment> __compartment;
    std::unique_ptr<CalculatorCompartment> __next_compartment;
    std::vector<CalculatorFrameContext> _context_stack;

    void __kernel(CalculatorFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            CalculatorFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                CalculatorFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    CalculatorFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(CalculatorFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<CalculatorCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(CalculatorFrameEvent& __e) {
        if (__e._message == "add") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            result = a + b;
            _context_stack.back()._return = std::any(result);
            return;;
        } else if (__e._message == "get_result") {
            _context_stack.back()._return = std::any(result);
            return;;
        }
    }

public:
    int result = 0;

    Calculator() {
        __compartment = std::make_unique<CalculatorCompartment>("Ready");
        CalculatorFrameEvent __frame_event("$>");
        CalculatorFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int add(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        CalculatorFrameEvent __e("add", std::move(__params));
        CalculatorFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_result() {
        CalculatorFrameEvent __e("get_result");
        CalculatorFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

class CounterFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    CounterFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class CounterFrameContext {
public:
    CounterFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    CounterFrameContext(CounterFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class CounterCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<CounterFrameEvent> forward_event;
    std::unique_ptr<CounterCompartment> parent_compartment;

    explicit CounterCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<CounterCompartment> clone() const {
        auto c = std::make_unique<CounterCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class Counter {
private:
    std::vector<std::unique_ptr<CounterCompartment>> _state_stack;
    std::unique_ptr<CounterCompartment> __compartment;
    std::unique_ptr<CounterCompartment> __next_compartment;
    std::vector<CounterFrameContext> _context_stack;

    void __kernel(CounterFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            CounterFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                CounterFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    CounterFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(CounterFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    void __transition(std::unique_ptr<CounterCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Active(CounterFrameEvent& __e) {
        if (__e._message == "get_count") {
            _context_stack.back()._return = std::any(count);
            return;;
        } else if (__e._message == "increment") {
            count = count + 1;
        }
    }

public:
    int count = 0;

    Counter() {
        __compartment = std::make_unique<CounterCompartment>("Active");
        CounterFrameEvent __frame_event("$>");
        CounterFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void increment() {
        CounterFrameEvent __e("increment");
        CounterFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_count() {
        CounterFrameEvent __e("get_count");
        CounterFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 39: Tagged System Instantiation ===\n");

    Calculator calc = Calculator();
    Counter counter = Counter();

    int result = calc.add(3, 4);
    if (result != 7) {
        printf("FAIL: Expected 7, got %d\n", result);
        assert(false);
    }
    printf("Calculator.add(3, 4) = %d\n", result);

    result = calc.get_result();
    if (result != 7) {
        printf("FAIL: Expected 7, got %d\n", result);
        assert(false);
    }
    printf("Calculator.get_result() = %d\n", result);

    counter.increment();
    counter.increment();
    counter.increment();
    int count = counter.get_count();
    if (count != 3) {
        printf("FAIL: Expected 3, got %d\n", count);
        assert(false);
    }
    printf("Counter after 3 increments: %d\n", count);

    printf("PASS: Tagged instantiation works correctly\n");
    return 0;
}
