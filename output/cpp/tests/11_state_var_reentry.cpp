#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <cassert>

class StateVarReentryFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    StateVarReentryFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class StateVarReentryFrameContext {
public:
    StateVarReentryFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    StateVarReentryFrameContext(StateVarReentryFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class StateVarReentryCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<StateVarReentryFrameEvent> forward_event;
    std::unique_ptr<StateVarReentryCompartment> parent_compartment;

    explicit StateVarReentryCompartment(const std::string& state) : state(state) {}
};

class StateVarReentry {
private:
    std::unique_ptr<StateVarReentryCompartment> __compartment;
    std::unique_ptr<StateVarReentryCompartment> __next_compartment;
    std::vector<std::unique_ptr<StateVarReentryCompartment>> _state_stack;
    std::vector<StateVarReentryFrameContext> _context_stack;

    void __kernel(StateVarReentryFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            StateVarReentryFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                StateVarReentryFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    StateVarReentryFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(StateVarReentryFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Counter") {
            _state_Counter(__e);
        } else if (state_name == "Other") {
            _state_Other(__e);
        }
    }

    void __transition(std::unique_ptr<StateVarReentryCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Counter(StateVarReentryFrameEvent& __e) {
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
        } else if (__e._message == "go_other") {
            {
            auto __comp = std::make_unique<StateVarReentryCompartment>("Other");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Other(StateVarReentryFrameEvent& __e) {
        if (__e._message == "come_back") {
            {
            auto __comp = std::make_unique<StateVarReentryCompartment>("Counter");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "increment") {
            {
            _context_stack.back()._return = -1;
            return;
            }
            return;
        } else if (__e._message == "get_count") {
            {
            _context_stack.back()._return = -1;
            return;
            }
            return;
        }
    }

public:
    StateVarReentry() {
        __compartment = std::make_unique<StateVarReentryCompartment>("Counter");
        __compartment->state_vars["count"] = 0;
        StateVarReentryFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int increment() {
        StateVarReentryFrameEvent __e("increment");
        StateVarReentryFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_count() {
        StateVarReentryFrameEvent __e("get_count");
        StateVarReentryFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void go_other() {
        StateVarReentryFrameEvent __e("go_other");
        StateVarReentryFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void come_back() {
        StateVarReentryFrameEvent __e("come_back");
        StateVarReentryFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 11: State Variable Reentry ===" << std::endl;
    StateVarReentry s;

    // Increment a few times
    s.increment();
    s.increment();
    int count = s.get_count();
    assert(count == 2);
    std::cout << "Count before leaving: " << count << std::endl;

    // Leave the state
    s.go_other();
    std::cout << "Transitioned to Other state" << std::endl;

    // Come back - state var should be reinitialized to 0
    s.come_back();
    count = s.get_count();
    assert(count == 0);
    std::cout << "Count after re-entering Counter: " << count << std::endl;

    // Increment again to verify it works
    int result = s.increment();
    assert(result == 1);
    std::cout << "After increment: " << result << std::endl;

    std::cout << "PASS: State variables reinitialize on state reentry" << std::endl;
    return 0;
}
