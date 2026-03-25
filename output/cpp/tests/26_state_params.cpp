#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class StateParamsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    StateParamsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class StateParamsFrameContext {
public:
    StateParamsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    StateParamsFrameContext(StateParamsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class StateParamsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<StateParamsFrameEvent> forward_event;
    std::unique_ptr<StateParamsCompartment> parent_compartment;

    explicit StateParamsCompartment(const std::string& state) : state(state) {}
};

class StateParams {
private:
    std::unique_ptr<StateParamsCompartment> __compartment;
    std::unique_ptr<StateParamsCompartment> __next_compartment;
    std::vector<std::unique_ptr<StateParamsCompartment>> _state_stack;
    std::vector<StateParamsFrameContext> _context_stack;

    void __kernel(StateParamsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            StateParamsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                StateParamsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    StateParamsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(StateParamsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Counter") {
            _state_Counter(__e);
        }
    }

    void __transition(std::unique_ptr<StateParamsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(StateParamsFrameEvent& __e) {
        if (__e._message == "start") {
            auto val = std::any_cast<int>(__e._parameters.at("val"));
            {
            auto __comp = std::make_unique<StateParamsCompartment>("Counter(val)");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "get_value") {
            {
            _context_stack.back()._return = 0;
            return;
            }
            return;
        }
    }

    void _state_Counter(StateParamsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            // Access state param via compartment - using string key "0"
            __compartment->state_vars["count"] = std::any(this->__compartment->state_args["0"]);
            int count_val = std::any_cast<int>(__compartment->state_vars["count"]);
            printf("Counter entered with initial=%d\n", count_val);
            }
            return;
        } else if (__e._message == "get_value") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["count"]);
            return;
            }
            return;
        }
    }

public:
    StateParams() {
        __compartment = std::make_unique<StateParamsCompartment>("Idle");
        StateParamsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void start(int val) {
        std::unordered_map<std::string, std::any> __params;
        __params["val"] = val;
        StateParamsFrameEvent __e("start", std::move(__params));
        StateParamsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_value() {
        StateParamsFrameEvent __e("get_value");
        StateParamsFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 26: State Parameters ===\n");
    StateParams s;

    int val = s.get_value();
    if (val != 0) {
        printf("FAIL: Expected 0 in Idle, got %d\n", val);
        assert(false);
    }
    printf("Initial value: %d\n", val);

    s.start(42);
    val = s.get_value();
    if (val != 42) {
        printf("FAIL: Expected 42 in Counter from state param, got %d\n", val);
        assert(false);
    }
    printf("Value after transition: %d\n", val);

    printf("PASS: State parameters work correctly\n");
    return 0;
}
