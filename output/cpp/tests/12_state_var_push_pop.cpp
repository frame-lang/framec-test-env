#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <cassert>

class StateVarPushPopFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    StateVarPushPopFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class StateVarPushPopFrameContext {
public:
    StateVarPushPopFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    StateVarPushPopFrameContext(StateVarPushPopFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class StateVarPushPopCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<StateVarPushPopFrameEvent> forward_event;
    std::unique_ptr<StateVarPushPopCompartment> parent_compartment;

    explicit StateVarPushPopCompartment(const std::string& state) : state(state) {}
};

class StateVarPushPop {
private:
    std::unique_ptr<StateVarPushPopCompartment> __compartment;
    std::unique_ptr<StateVarPushPopCompartment> __next_compartment;
    std::vector<std::unique_ptr<StateVarPushPopCompartment>> _state_stack;
    std::vector<StateVarPushPopFrameContext> _context_stack;

    void __kernel(StateVarPushPopFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            StateVarPushPopFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                StateVarPushPopFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    StateVarPushPopFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(StateVarPushPopFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Counter") {
            _state_Counter(__e);
        } else if (state_name == "Other") {
            _state_Other(__e);
        }
    }

    void __transition(std::unique_ptr<StateVarPushPopCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Counter(StateVarPushPopFrameEvent& __e) {
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
        } else if (__e._message == "save_and_go") {
            {
            _state_stack.push_back(std::make_unique<StateVarPushPopCompartment>(__compartment->state));
            _state_stack.back()->state_vars = __compartment->state_vars;
            _state_stack.back()->state_args = __compartment->state_args;
            auto __comp = std::make_unique<StateVarPushPopCompartment>("Other");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Other(StateVarPushPopFrameEvent& __e) {
        if (__e._message == "restore") {
            {
            auto __popped = std::move(_state_stack.back());
            _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
            }
            return;
        } else if (__e._message == "increment") {
            {
            __compartment->state_vars["other_count"] = std::any(std::any_cast<int>(__compartment->state_vars["other_count"]) + 1);
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["other_count"]);
            return;
            }
            return;
        } else if (__e._message == "get_count") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["other_count"]);
            return;
            }
            return;
        }
    }

public:
    StateVarPushPop() {
        __compartment = std::make_unique<StateVarPushPopCompartment>("Counter");
        __compartment->state_vars["count"] = 0;
        StateVarPushPopFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int increment() {
        StateVarPushPopFrameEvent __e("increment");
        StateVarPushPopFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_count() {
        StateVarPushPopFrameEvent __e("get_count");
        StateVarPushPopFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void save_and_go() {
        StateVarPushPopFrameEvent __e("save_and_go");
        StateVarPushPopFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void restore() {
        StateVarPushPopFrameEvent __e("restore");
        StateVarPushPopFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 12: State Variable Push/Pop ===" << std::endl;
    StateVarPushPop s;

    // Increment counter to 3
    s.increment();
    s.increment();
    s.increment();
    int count = s.get_count();
    assert(count == 3);
    std::cout << "Counter before push: " << count << std::endl;

    // Push and go to Other state
    s.save_and_go();
    std::cout << "Pushed and transitioned to Other" << std::endl;

    // In Other state, count should be 100 (Other's state var)
    count = s.get_count();
    assert(count == 100);
    std::cout << "Other state count: " << count << std::endl;

    // Increment in Other
    s.increment();
    count = s.get_count();
    assert(count == 101);
    std::cout << "Other state after increment: " << count << std::endl;

    // Pop back - should restore Counter with count=3
    s.restore();
    std::cout << "Popped back to Counter" << std::endl;

    count = s.get_count();
    assert(count == 3);
    std::cout << "Counter after pop: " << count << std::endl;

    // Increment to verify it works
    s.increment();
    count = s.get_count();
    assert(count == 4);
    std::cout << "Counter after increment: " << count << std::endl;

    std::cout << "PASS: State variables preserved across push/pop" << std::endl;
    return 0;
}
