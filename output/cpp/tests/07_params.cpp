#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class WithParamsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    WithParamsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class WithParamsFrameContext {
public:
    WithParamsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    WithParamsFrameContext(WithParamsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class WithParamsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<WithParamsFrameEvent> forward_event;
    std::unique_ptr<WithParamsCompartment> parent_compartment;

    explicit WithParamsCompartment(const std::string& state) : state(state) {}
};

class WithParams {
private:
    std::unique_ptr<WithParamsCompartment> __compartment;
    std::unique_ptr<WithParamsCompartment> __next_compartment;
    std::vector<std::unique_ptr<WithParamsCompartment>> _state_stack;
    std::vector<WithParamsFrameContext> _context_stack;

    int total = 0;;

    void __kernel(WithParamsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            WithParamsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                WithParamsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    WithParamsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(WithParamsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Running") {
            _state_Running(__e);
        }
    }

    void __transition(std::unique_ptr<WithParamsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(WithParamsFrameEvent& __e) {
        if (__e._message == "start") {
            auto initial = std::any_cast<int>(__e._parameters.at("initial"));
            {
            total = initial;
            std::cout << "Started with initial value: " << initial << std::endl;
            auto __comp = std::make_unique<WithParamsCompartment>("Running");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "add") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            {
            std::cout << "Cannot add in Idle state" << std::endl;
            }
            return;
        } else if (__e._message == "multiply") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            {
            _context_stack.back()._return = 0;
            return;
            }
            return;
        } else if (__e._message == "get_total") {
            {
            _context_stack.back()._return = total;
            return;
            }
            return;
        }
    }

    void _state_Running(WithParamsFrameEvent& __e) {
        if (__e._message == "start") {
            auto initial = std::any_cast<int>(__e._parameters.at("initial"));
            {
            std::cout << "Already running" << std::endl;
            }
            return;
        } else if (__e._message == "add") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            {
            total += value;
            std::cout << "Added " << value << ", total is now " << total << std::endl;
            }
            return;
        } else if (__e._message == "multiply") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            {
            int result = a * b;
            total += result;
            std::cout << "Multiplied " << a << " * " << b << " = " << result << ", total is now " << total << std::endl;
            _context_stack.back()._return = result;
            return;
            }
            return;
        } else if (__e._message == "get_total") {
            {
            _context_stack.back()._return = total;
            return;
            }
            return;
        }
    }

public:
    WithParams() {
        __compartment = std::make_unique<WithParamsCompartment>("Idle");
        total = 0;;
        WithParamsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void start(int initial) {
        std::unordered_map<std::string, std::any> __params;
        __params["initial"] = initial;
        WithParamsFrameEvent __e("start", std::move(__params));
        WithParamsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void add(int value) {
        std::unordered_map<std::string, std::any> __params;
        __params["value"] = value;
        WithParamsFrameEvent __e("add", std::move(__params));
        WithParamsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int multiply(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        WithParamsFrameEvent __e("multiply", std::move(__params));
        WithParamsFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_total() {
        WithParamsFrameEvent __e("get_total");
        WithParamsFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 07: Handler Parameters ===" << std::endl;
    WithParams s;

    // Initial total should be 0
    int total = s.get_total();
    assert(total == 0);

    // Start with initial value
    s.start(100);
    total = s.get_total();
    assert(total == 100);
    std::cout << "After start(100): total = " << total << std::endl;

    // Add value
    s.add(25);
    total = s.get_total();
    assert(total == 125);
    std::cout << "After add(25): total = " << total << std::endl;

    // Multiply with two params
    int result = s.multiply(3, 5);
    assert(result == 15);
    total = s.get_total();
    assert(total == 140);
    std::cout << "After multiply(3,5): result = " << result << ", total = " << total << std::endl;

    std::cout << "PASS: 07 params" << std::endl;
    return 0;
}
