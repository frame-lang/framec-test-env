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

    std::unique_ptr<WithParamsCompartment> clone() const {
        auto c = std::make_unique<WithParamsCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class WithParams {
private:
    std::vector<std::unique_ptr<WithParamsCompartment>> _state_stack;
    std::unique_ptr<WithParamsCompartment> __compartment;
    std::unique_ptr<WithParamsCompartment> __next_compartment;
    std::vector<WithParamsFrameContext> _context_stack;

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
        if (__e._message == "add") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            printf("Cannot add in Idle state\n");
        } else if (__e._message == "get_total") {
            _context_stack.back()._return = std::any(total);
            return;;
        } else if (__e._message == "multiply") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            _context_stack.back()._return = std::any(0);
            return;;
        } else if (__e._message == "start") {
            auto initial = std::any_cast<int>(__e._parameters.at("initial"));
            total = initial;
            printf("Started with initial value: %d\n", initial);
            auto __new_compartment = std::make_unique<WithParamsCompartment>("Running");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Running(WithParamsFrameEvent& __e) {
        if (__e._message == "add") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            total += value;
            printf("Added %d, total is now %d\n", value, total);
        } else if (__e._message == "get_total") {
            _context_stack.back()._return = std::any(total);
            return;;
        } else if (__e._message == "multiply") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            int result = a * b;
            total += result;
            printf("Multiplied %d * %d = %d, total is now %d\n", a, b, result, total);
            _context_stack.back()._return = std::any(result);
            return;;
        } else if (__e._message == "start") {
            auto initial = std::any_cast<int>(__e._parameters.at("initial"));
            printf("Already running\n");
        }
    }

public:
    int total = 0;

    WithParams() {
        __compartment = std::make_unique<WithParamsCompartment>("Idle");
        WithParamsFrameEvent __frame_event("$>");
        WithParamsFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
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
    printf("=== Test 07: Handler Parameters ===\n");
    WithParams s;

    int total = s.get_total();
    if (total != 0) {
        printf("FAIL: Expected initial total=0, got %d\n", total);
        assert(false);
    }

    s.start(100);
    total = s.get_total();
    if (total != 100) {
        printf("FAIL: Expected total=100, got %d\n", total);
        assert(false);
    }
    printf("After start(100): total = %d\n", total);

    s.add(25);
    total = s.get_total();
    if (total != 125) {
        printf("FAIL: Expected total=125, got %d\n", total);
        assert(false);
    }
    printf("After add(25): total = %d\n", total);

    int result = s.multiply(3, 5);
    if (result != 15) {
        printf("FAIL: Expected multiply result=15, got %d\n", result);
        assert(false);
    }
    total = s.get_total();
    if (total != 140) {
        printf("FAIL: Expected total=140, got %d\n", total);
        assert(false);
    }
    printf("After multiply(3,5): result = %d, total = %d\n", result, total);

    printf("PASS: Handler parameters work correctly\n");
    return 0;
}
