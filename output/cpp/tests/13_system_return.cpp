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

    std::unique_ptr<SystemReturnTestCompartment> clone() const {
        auto c = std::make_unique<SystemReturnTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class SystemReturnTest {
private:
    std::vector<std::unique_ptr<SystemReturnTestCompartment>> _state_stack;
    std::unique_ptr<SystemReturnTestCompartment> __compartment;
    std::unique_ptr<SystemReturnTestCompartment> __next_compartment;
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
        auto* __sv_comp = __compartment.get();
        while (__sv_comp && __sv_comp->state != "Calculator") { __sv_comp = __sv_comp->parent_compartment.get(); }
        if (__e._message == "$>") {
            if (__compartment->state_vars.count("value") == 0) { __compartment->state_vars["value"] = std::any(0); }
        } else if (__e._message == "add") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            _context_stack.back()._return = std::any(a + b);
            return;;
        } else if (__e._message == "get_value") {
            __sv_comp->state_vars["value"] = std::any(42);
            _context_stack.back()._return = std::any(std::any_cast<int>(__sv_comp->state_vars["value"]));
            return;;
        } else if (__e._message == "greet") {
            auto name = std::any_cast<std::string>(__e._parameters.at("name"));
            _context_stack.back()._return = std::any(std::string("Hello, ") + name + "!");
            return;;
        } else if (__e._message == "multiply") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            _context_stack.back()._return = std::any(a * b);
        }
    }

public:
    SystemReturnTest() {
        __compartment = std::make_unique<SystemReturnTestCompartment>("Calculator");
        SystemReturnTestFrameEvent __frame_event("$>");
        SystemReturnTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
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
    printf("=== Test 13: System Return ===\n");
    SystemReturnTest calc;

    int result = calc.add(3, 5);
    if (result != 8) {
        printf("FAIL: Expected 8, got %d\n", result);
        assert(false);
    }
    printf("add(3, 5) = %d\n", result);

    result = calc.multiply(4, 7);
    if (result != 28) {
        printf("FAIL: Expected 28, got %d\n", result);
        assert(false);
    }
    printf("multiply(4, 7) = %d\n", result);

    std::string greeting = calc.greet("World");
    if (greeting != "Hello, World!") {
        printf("FAIL: Expected 'Hello, World!', got '%s'\n", greeting.c_str());
        assert(false);
    }
    printf("greet('World') = %s\n", greeting.c_str());

    int value = calc.get_value();
    if (value != 42) {
        printf("FAIL: Expected 42, got %d\n", value);
        assert(false);
    }
    printf("get_value() = %d\n", value);

    printf("PASS: System return works correctly\n");
    return 0;
}
