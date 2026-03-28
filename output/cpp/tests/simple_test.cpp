#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>



#include <iostream>
#include <string>
#include <cassert>

class SimpleDockerFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SimpleDockerFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SimpleDockerFrameContext {
public:
    SimpleDockerFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SimpleDockerFrameContext(SimpleDockerFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SimpleDockerCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SimpleDockerFrameEvent> forward_event;
    std::unique_ptr<SimpleDockerCompartment> parent_compartment;

    explicit SimpleDockerCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<SimpleDockerCompartment> clone() const {
        auto c = std::make_unique<SimpleDockerCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class SimpleDocker {
private:
    std::vector<std::unique_ptr<SimpleDockerCompartment>> _state_stack;
    std::unique_ptr<SimpleDockerCompartment> __compartment;
    std::unique_ptr<SimpleDockerCompartment> __next_compartment;
    std::vector<SimpleDockerFrameContext> _context_stack;

    void __kernel(SimpleDockerFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SimpleDockerFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SimpleDockerFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SimpleDockerFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SimpleDockerFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "End") {
            _state_End(__e);
        }
    }

    void __transition(std::unique_ptr<SimpleDockerCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(SimpleDockerFrameEvent& __e) {
        if (__e._message == "run") {
            printf("SUCCESS: Hello from Docker\n");
            auto __new_compartment = std::make_unique<SimpleDockerCompartment>("End");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_End(SimpleDockerFrameEvent& __e) {

    }

public:
    SimpleDocker() {
        __compartment = std::make_unique<SimpleDockerCompartment>("Start");
        SimpleDockerFrameEvent __frame_event("$>");
        SimpleDockerFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void run() {
        SimpleDockerFrameEvent __e("run");
        SimpleDockerFrameContext __ctx(std::move(__e));
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
        SimpleDocker s;
        printf("ok 1 - simple_test\n");
    } catch (...) {
        printf("not ok 1 - simple_test\n");
    }
    return 0;
}
