#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class SysXFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SysXFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SysXFrameContext {
public:
    SysXFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SysXFrameContext(SysXFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SysXCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SysXFrameEvent> forward_event;
    std::unique_ptr<SysXCompartment> parent_compartment;

    explicit SysXCompartment(const std::string& state) : state(state) {}
};

class SysX {
private:
    std::unique_ptr<SysXCompartment> __compartment;
    std::unique_ptr<SysXCompartment> __next_compartment;
    std::vector<std::unique_ptr<SysXCompartment>> _state_stack;
    std::vector<SysXFrameContext> _context_stack;

    void __kernel(SysXFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SysXFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SysXFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SysXFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SysXFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        }
    }

    void __transition(std::unique_ptr<SysXCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_A(SysXFrameEvent& __e) {
        if (__e._message == "e") {
            {
            auto __comp = std::make_unique<SysXCompartment>("B()");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_B(SysXFrameEvent& __e) {
    }

public:
    SysX() {
        __compartment = std::make_unique<SysXCompartment>("A");
        SysXFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void e() {
        SysXFrameEvent __e("e");
        SysXFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

};

// Stub functions for placeholder calls
void native() {}
void x() {}

// TAP test harness
int main() {
    printf("TAP version 14\n");
    printf("1..1\n");
    try {
        SysX s;
        s.e();
        printf("ok 1 - transition_state_id_exec\n");
    } catch (...) {
        printf("not ok 1 - transition_state_id_exec\n");
    }
    return 0;
}
