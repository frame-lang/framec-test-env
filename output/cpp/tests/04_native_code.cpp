#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


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
};

class NativeCode {
private:
    std::unique_ptr<NativeCodeCompartment> __compartment;
    std::unique_ptr<NativeCodeCompartment> __next_compartment;
    std::vector<std::unique_ptr<NativeCodeCompartment>> _state_stack;
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
            {
            // Native code with local variables
            int temp = value + 10;
            int result = helper_function(temp);
            std::cout << "Computed: " << value << " -> " << result << std::endl;
            _context_stack.back()._return = result;
            return;
            }
            return;
        } else if (__e._message == "use_math") {
            {
            // Using imported math functions
            double result = sqrt(16.0) + M_PI;
            std::cout << "Math result: " << result << std::endl;
            _context_stack.back()._return = result;
            return;
            }
            return;
        }
    }

public:
    NativeCode() {
        __compartment = std::make_unique<NativeCodeCompartment>("Active");
        NativeCodeFrameEvent __frame_event("$>");
        __kernel(__frame_event);
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
    std::cout << "=== Test 04: Native Code Preservation ===" << std::endl;
    NativeCode s;

    // Test native code in handler with helper function
    int result = s.compute(5);
    int expected = (5 + 10) * 2;  // 30
    assert(result == expected);
    std::cout << "compute(5) = " << result << std::endl;

    // Test imported module usage
    double math_result = s.use_math();
    double expected_math = sqrt(16.0) + M_PI;
    assert(std::abs(math_result - expected_math) < 0.001);
    std::cout << "use_math() = " << math_result << std::endl;

    std::cout << "PASS: 04 native code" << std::endl;
    return 0;
}
