#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class SystemReturnTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SystemReturnTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SystemReturnTestFrameContext {
public:
    SystemReturnTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SystemReturnTestFrameContext(SystemReturnTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SystemReturnTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SystemReturnTestFrameEvent> forward_event;
    std::unique_ptr<SystemReturnTestCompartment> parent_compartment;

    explicit SystemReturnTestCompartment(const std::string& state) : state(state) {}
};

class SystemReturnTest {
private:
    std::unique_ptr<SystemReturnTestCompartment> __compartment;
    std::unique_ptr<SystemReturnTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<SystemReturnTestCompartment>> _state_stack;
    std::vector<SystemReturnTestFrameContext> _context_stack;

    void __kernel(SystemReturnTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SystemReturnTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SystemReturnTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SystemReturnTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SystemReturnTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Calculator") {
            _state_Calculator(__e);
        }
    }

    void __transition(std::unique_ptr<SystemReturnTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Calculator(SystemReturnTestFrameEvent& __e) {
        if (__e._message == "add") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            {
            _context_stack.back()._return = a + b;
            return;
            }
            return;
        } else if (__e._message == "multiply") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            {
            _context_stack.back()._return = a * b;
            }
            return;
        } else if (__e._message == "greet") {
            auto name = std::any_cast<std::string>(__e._parameters.at("name"));
            {
            _context_stack.back()._return = std::string("Hello, ") + name + std::string("!");
            return;
            }
            return;
        } else if (__e._message == "get_value") {
            {
            __compartment->state_vars["value"] = std::any(42);
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["value"]);
            return;
            }
            return;
        }
    }

public:
    SystemReturnTest() {
        __compartment = std::make_unique<SystemReturnTestCompartment>("Calculator");
        __compartment->state_vars["value"] = 0;
        SystemReturnTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int add(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        SystemReturnTestFrameEvent __e("add", std::move(__params));
        SystemReturnTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int multiply(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        SystemReturnTestFrameEvent __e("multiply", std::move(__params));
        SystemReturnTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string greet(std::string name) {
        std::unordered_map<std::string, std::any> __params;
        __params["name"] = name;
        SystemReturnTestFrameEvent __e("greet", std::move(__params));
        SystemReturnTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_value() {
        SystemReturnTestFrameEvent __e("get_value");
        SystemReturnTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 13: System Return ===" << std::endl;
    SystemReturnTest calc;

    // Test return sugar
    int result = calc.add(3, 5);
    assert(result == 8);
    std::cout << "add(3, 5) = " << result << std::endl;

    // Test @@:return = expr
    result = calc.multiply(4, 7);
    assert(result == 28);
    std::cout << "multiply(4, 7) = " << result << std::endl;

    // Test string return
    std::string greeting = calc.greet("World");
    assert(greeting == "Hello, World!");
    std::cout << "greet('World') = " << greeting << std::endl;

    // Test return with state variable
    int value = calc.get_value();
    assert(value == 42);
    std::cout << "get_value() = " << value << std::endl;

    std::cout << "PASS: 13 system return" << std::endl;
    return 0;
}
