#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class StateVarBasicFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    StateVarBasicFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class StateVarBasicFrameContext {
public:
    StateVarBasicFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    StateVarBasicFrameContext(StateVarBasicFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class StateVarBasicCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<StateVarBasicFrameEvent> forward_event;
    std::unique_ptr<StateVarBasicCompartment> parent_compartment;

    explicit StateVarBasicCompartment(const std::string& state) : state(state) {}
};

class StateVarBasic {
private:
    std::unique_ptr<StateVarBasicCompartment> __compartment;
    std::unique_ptr<StateVarBasicCompartment> __next_compartment;
    std::vector<std::unique_ptr<StateVarBasicCompartment>> _state_stack;
    std::vector<StateVarBasicFrameContext> _context_stack;

    void __kernel(StateVarBasicFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            StateVarBasicFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                StateVarBasicFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    StateVarBasicFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(StateVarBasicFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Counter") {
            _state_Counter(__e);
        }
    }

    void __transition(std::unique_ptr<StateVarBasicCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Counter(StateVarBasicFrameEvent& __e) {
        if (__e._message == "increment") {
            {
            __compartment->state_vars["count"] = std::any(std::any_cast<int>(__compartment->state_vars["count"]) + 1);
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["count"]);
            return;
            }
            return;
        } else if (__e._message == "get_count") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["count"]);
            return;
            }
            return;
        } else if (__e._message == "reset") {
            {
            __compartment->state_vars["count"] = std::any(0);
            }
            return;
        }
    }

public:
    StateVarBasic() {
        __compartment = std::make_unique<StateVarBasicCompartment>("Counter");
        __compartment->state_vars["count"] = 0;
        StateVarBasicFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int increment() {
        StateVarBasicFrameEvent __e("increment");
        StateVarBasicFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_count() {
        StateVarBasicFrameEvent __e("get_count");
        StateVarBasicFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void reset() {
        StateVarBasicFrameEvent __e("reset");
        StateVarBasicFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

};

int main() {
    std::cout << "=== Test 10: State Variable Basic ===" << std::endl;
    StateVarBasic s;

    // Initial value should be 0
    assert(s.get_count() == 0);
    std::cout << "Initial count: " << s.get_count() << std::endl;

    // Increment should return new value
    int result = s.increment();
    assert(result == 1);
    std::cout << "After first increment: " << result << std::endl;

    // Second increment
    result = s.increment();
    assert(result == 2);
    std::cout << "After second increment: " << result << std::endl;

    // Reset should set back to 0
    s.reset();
    assert(s.get_count() == 0);
    std::cout << "After reset: " << s.get_count() << std::endl;

    std::cout << "PASS: 10 state var basic" << std::endl;
    return 0;
}
