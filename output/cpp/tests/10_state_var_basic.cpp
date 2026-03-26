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

    std::unique_ptr<StateVarBasicCompartment> clone() const {
        auto c = std::make_unique<StateVarBasicCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class StateVarBasic {
private:
    std::vector<std::unique_ptr<StateVarBasicCompartment>> _state_stack;
    std::unique_ptr<StateVarBasicCompartment> __compartment;
    std::unique_ptr<StateVarBasicCompartment> __next_compartment;
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
        auto* __sv_comp = __compartment.get();
        while (__sv_comp && __sv_comp->state != "Counter") { __sv_comp = __sv_comp->parent_compartment.get(); }
        if (__e._message == "$>") {
            if (__compartment->state_vars.count("count") == 0) { __compartment->state_vars["count"] = std::any(0); }
        } else if (__e._message == "get_count") {
            _context_stack.back()._return = std::any(std::any_cast<int>(__sv_comp->state_vars["count"]));
            return;;
        } else if (__e._message == "increment") {
            __sv_comp->state_vars["count"] = std::any(std::any_cast<int>(__sv_comp->state_vars["count"]) + 1);
            _context_stack.back()._return = std::any(std::any_cast<int>(__sv_comp->state_vars["count"]));
            return;;
        } else if (__e._message == "reset") {
            __sv_comp->state_vars["count"] = std::any(0);
        }
    }

public:
    StateVarBasic() {
        __compartment = std::make_unique<StateVarBasicCompartment>("Counter");
        StateVarBasicFrameEvent __frame_event("$>");
        StateVarBasicFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
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
    printf("=== Test 10: State Variable Basic ===\n");
    StateVarBasic s;

    if (s.get_count() != 0) {
        printf("FAIL: Expected 0, got %d\n", s.get_count());
        assert(false);
    }
    printf("Initial count: %d\n", s.get_count());

    int result = s.increment();
    if (result != 1) {
        printf("FAIL: Expected 1 after first increment, got %d\n", result);
        assert(false);
    }
    printf("After first increment: %d\n", result);

    result = s.increment();
    if (result != 2) {
        printf("FAIL: Expected 2 after second increment, got %d\n", result);
        assert(false);
    }
    printf("After second increment: %d\n", result);

    s.reset();
    if (s.get_count() != 0) {
        printf("FAIL: Expected 0 after reset, got %d\n", s.get_count());
        assert(false);
    }
    printf("After reset: %d\n", s.get_count());

    printf("PASS: State variable basic operations work correctly\n");
    return 0;
}
