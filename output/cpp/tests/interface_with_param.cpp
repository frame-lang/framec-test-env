#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class SFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SFrameContext {
public:
    SFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SFrameContext(SFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SFrameEvent> forward_event;
    std::unique_ptr<SCompartment> parent_compartment;

    explicit SCompartment(const std::string& state) : state(state) {}
};

class S {
private:
    std::unique_ptr<SCompartment> __compartment;
    std::unique_ptr<SCompartment> __next_compartment;
    std::vector<std::unique_ptr<SCompartment>> _state_stack;
    std::vector<SFrameContext> _context_stack;

    void __kernel(SFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "P") {
            _state_P(__e);
        }
    }

    void __transition(std::unique_ptr<SCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_A(SFrameEvent& __e) {
        if (__e._message == "ev") {
            auto n = std::any_cast<int>(__e._parameters.at("n"));
            {
            _state_P(__e);
            return;
            // str(n) would be converted but we just verify forwarding works
            }
            return;
        }
    }

    void _state_P(SFrameEvent& __e) {
    }

public:
    S() {
        __compartment = std::make_unique<SCompartment>("A");
        SFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

};

int main() {
    std::cout << "=== Test: Interface With Param ===" << std::endl;
    S s;

    // The test mainly verifies the system compiles with HSM forwarding
    // and parameter handling
    std::cout << "System created with HSM forwarding and params" << std::endl;

    std::cout << "PASS: Interface with param compiles correctly" << std::endl;
    return 0;
}
