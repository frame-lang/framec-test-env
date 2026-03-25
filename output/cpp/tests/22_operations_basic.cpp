#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <cassert>

class OperationTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    OperationTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class OperationTestFrameContext {
public:
    OperationTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    OperationTestFrameContext(OperationTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class OperationTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<OperationTestFrameEvent> forward_event;
    std::unique_ptr<OperationTestCompartment> parent_compartment;

    explicit OperationTestCompartment(const std::string& state) : state(state) {}
};

class OperationTest {
private:
    std::unique_ptr<OperationTestCompartment> __compartment;
    std::unique_ptr<OperationTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<OperationTestCompartment>> _state_stack;
    std::vector<OperationTestFrameContext> _context_stack;

    void __kernel(OperationTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            OperationTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                OperationTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    OperationTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(OperationTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<OperationTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(OperationTestFrameEvent& __e) {
        if (__e._message == "run_test") {
            {
            int result = OperationTest_double_value(self, 21);
            _context_stack.back()._return = result;
            return;
            }
            return;
        }
    }

public:
    OperationTest() {
        __compartment = std::make_unique<OperationTestCompartment>("Start");
        OperationTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int run_test() {
        OperationTestFrameEvent __e("run_test");
        OperationTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int double_value() {
        {
        return x * 2;
        }
    }

};

int main() {
    std::cout << "=== Test 22: Basic Operations ===" << std::endl;
    OperationTest o;

    int result = o.run_test();
    std::cout << "double_value(21) = " << result << std::endl;
    assert(result == 42);

    std::cout << "PASS: Basic operations work correctly" << std::endl;
    return 0;
}
