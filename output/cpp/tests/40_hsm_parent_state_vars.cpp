#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class HSMParentStateVarsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMParentStateVarsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMParentStateVarsFrameContext {
public:
    HSMParentStateVarsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMParentStateVarsFrameContext(HSMParentStateVarsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMParentStateVarsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMParentStateVarsFrameEvent> forward_event;
    std::unique_ptr<HSMParentStateVarsCompartment> parent_compartment;

    explicit HSMParentStateVarsCompartment(const std::string& state) : state(state) {}
};

class HSMParentStateVars {
private:
    std::unique_ptr<HSMParentStateVarsCompartment> __compartment;
    std::unique_ptr<HSMParentStateVarsCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMParentStateVarsCompartment>> _state_stack;
    std::vector<HSMParentStateVarsFrameContext> _context_stack;

    void __kernel(HSMParentStateVarsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMParentStateVarsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMParentStateVarsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMParentStateVarsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMParentStateVarsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMParentStateVarsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Child(HSMParentStateVarsFrameEvent& __e) {
        if (__e._message == "get_child_count") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["child_count"]);
            return;
            }
            return;
        } else if (__e._message == "get_parent_count") {
            {
            _state_Parent(__e);
            return;
            }
            return;
        }
    }

    void _state_Parent(HSMParentStateVarsFrameEvent& __e) {
        if (__e._message == "get_parent_count") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["parent_count"]);
            return;
            }
            return;
        }
    }

public:
    HSMParentStateVars() {
        __compartment = std::make_unique<HSMParentStateVarsCompartment>("Child");
        __compartment->state_vars["child_count"] = 0;
        HSMParentStateVarsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int get_child_count() {
        HSMParentStateVarsFrameEvent __e("get_child_count");
        HSMParentStateVarsFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_parent_count() {
        HSMParentStateVarsFrameEvent __e("get_parent_count");
        HSMParentStateVarsFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 40: HSM Parent State Variables ===\n");
    HSMParentStateVars s;

    int childCount = s.get_child_count();
    if (childCount != 0) {
        printf("FAIL: Expected child_count=0, got %d\n", childCount);
        assert(false);
    }
    printf("Child count: %d\n", childCount);

    int parentCount = s.get_parent_count();
    if (parentCount != 100) {
        printf("FAIL: Expected parent_count=100, got %d\n", parentCount);
        assert(false);
    }
    printf("Parent count: %d\n", parentCount);

    printf("PASS: HSM parent state variables work correctly\n");
    return 0;
}
