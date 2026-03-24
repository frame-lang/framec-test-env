#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class InterfaceReturnTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    InterfaceReturnTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class InterfaceReturnTestFrameContext {
public:
    InterfaceReturnTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    InterfaceReturnTestFrameContext(InterfaceReturnTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class InterfaceReturnTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<InterfaceReturnTestFrameEvent> forward_event;
    std::unique_ptr<InterfaceReturnTestCompartment> parent_compartment;

    explicit InterfaceReturnTestCompartment(const std::string& state) : state(state) {}
};

class InterfaceReturnTest {
private:
    std::unique_ptr<InterfaceReturnTestCompartment> __compartment;
    std::unique_ptr<InterfaceReturnTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<InterfaceReturnTestCompartment>> _state_stack;
    std::vector<InterfaceReturnTestFrameContext> _context_stack;

    void __kernel(InterfaceReturnTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            InterfaceReturnTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                InterfaceReturnTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    InterfaceReturnTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(InterfaceReturnTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<InterfaceReturnTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(InterfaceReturnTestFrameEvent& __e) {
        if (__e._message == "get_value") {
            {
            _context_stack.back()._return = 42;
            return;
            }
            return;
        } else if (__e._message == "get_name") {
            {
            _context_stack.back()._return = std::string("Frame");
            return;
            }
            return;
        }
    }

public:
    InterfaceReturnTest() {
        __compartment = std::make_unique<InterfaceReturnTestCompartment>("Ready");
        InterfaceReturnTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int get_value() {
        InterfaceReturnTestFrameEvent __e("get_value");
        InterfaceReturnTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_name() {
        InterfaceReturnTestFrameEvent __e("get_name");
        InterfaceReturnTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    InterfaceReturnTest s;
    assert(s.get_value() == 42);
    assert(s.get_name() == "Frame");
    std::cout << "PASS: 01 interface return" << std::endl;
    return 0;
}
