#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>
#include <cmath>

int helper_function(int x) {
    return x * 2;
}

class NativeCodeFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    NativeCodeFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class NativeCodeFrameContext {
public:
    NativeCodeFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    NativeCodeFrameContext(NativeCodeFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class NativeCodeCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<NativeCodeFrameEvent> forward_event;
    std::unique_ptr<NativeCodeCompartment> parent_compartment;

    explicit NativeCodeCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<NativeCodeCompartment> clone() const {
        auto c = std::make_unique<NativeCodeCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class NativeCode {
private:
    std::vector<std::unique_ptr<NativeCodeCompartment>> _state_stack;
    std::unique_ptr<NativeCodeCompartment> __compartment;
    std::unique_ptr<NativeCodeCompartment> __next_compartment;
    std::vector<NativeCodeFrameContext> _context_stack;

    void __kernel(NativeCodeFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            NativeCodeFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                NativeCodeFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    NativeCodeFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(NativeCodeFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    void __transition(std::unique_ptr<NativeCodeCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Active(NativeCodeFrameEvent& __e) {
        if (__e._message == "compute") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            int temp = value + 10;
            int result = helper_function(temp);
            printf("Computed: %d -> %d\n", value, result);
            _context_stack.back()._return = std::any(result);
            return;;
        } else if (__e._message == "use_math") {
            double result = sqrt(16.0) + M_PI;
            printf("Math result: %f\n", result);
            _context_stack.back()._return = std::any(result);
            return;;
        }
    }

public:
    NativeCode() {
        __compartment = std::make_unique<NativeCodeCompartment>("Active");
        NativeCodeFrameEvent __frame_event("$>");
        NativeCodeFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int compute(int value) {
        std::unordered_map<std::string, std::any> __params;
        __params["value"] = value;
        NativeCodeFrameEvent __e("compute", std::move(__params));
        NativeCodeFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    double use_math() {
        NativeCodeFrameEvent __e("use_math");
        NativeCodeFrameContext __ctx(std::move(__e), std::any(double()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<double>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 04: Native Code Preservation ===\n");
    NativeCode s;

    int result = s.compute(5);
    int expected = (5 + 10) * 2;
    if (result != expected) {
        printf("FAIL: Expected %d, got %d\n", expected, result);
        assert(false);
    }
    printf("compute(5) = %d\n", result);

    double mathResult = s.use_math();
    double expectedMath = sqrt(16.0) + M_PI;
    if (fabs(mathResult - expectedMath) >= 0.001) {
        printf("FAIL: Expected ~%f, got %f\n", expectedMath, mathResult);
        assert(false);
    }
    printf("use_math() = %f\n", mathResult);

    printf("PASS: Native code preservation works correctly\n");
    return 0;
}
