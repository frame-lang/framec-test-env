#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class ActionTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ActionTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ActionTestFrameContext {
public:
    ActionTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ActionTestFrameContext(ActionTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ActionTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ActionTestFrameEvent> forward_event;
    std::unique_ptr<ActionTestCompartment> parent_compartment;

    explicit ActionTestCompartment(const std::string& state) : state(state) {}
};

class ActionTest {
private:
    std::unique_ptr<ActionTestCompartment> __compartment;
    std::unique_ptr<ActionTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<ActionTestCompartment>> _state_stack;
    std::vector<ActionTestFrameContext> _context_stack;

    int action_count;

    void __kernel(ActionTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ActionTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ActionTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ActionTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ActionTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<ActionTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(ActionTestFrameEvent& __e) {
        if (__e._message == "do_work") {
            {
            ActionTest_log_action(self, "Starting work");
            _context_stack.back()._return = self->action_count;
            return;
            }
            return;
        }
    }

public:
    ActionTest() {
        __compartment = std::make_unique<ActionTestCompartment>("Start");
        ActionTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int do_work() {
        ActionTestFrameEvent __e("do_work");
        ActionTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void log_action() {
        {
        std::cout << "Action: " << msg << std::endl;
        self->action_count = self->action_count + 1;
        }
    }

};

int main() {
    std::cout << "=== Test 21: Basic Actions ===" << std::endl;
    ActionTest a;

    int count = a.do_work();
    std::cout << "Action count: " << count << std::endl;
    assert(count == 1);

    count = a.do_work();
    std::cout << "Action count: " << count << std::endl;
    assert(count == 2);

    std::cout << "PASS: Basic actions work correctly" << std::endl;
    return 0;
}
