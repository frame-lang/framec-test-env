#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>
#include <vector>
#include <algorithm>

class HSMExitHandlersFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMExitHandlersFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMExitHandlersFrameContext {
public:
    HSMExitHandlersFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMExitHandlersFrameContext(HSMExitHandlersFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMExitHandlersCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMExitHandlersFrameEvent> forward_event;
    std::unique_ptr<HSMExitHandlersCompartment> parent_compartment;

    explicit HSMExitHandlersCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HSMExitHandlersCompartment> clone() const {
        auto c = std::make_unique<HSMExitHandlersCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HSMExitHandlers {
private:
    std::vector<std::unique_ptr<HSMExitHandlersCompartment>> _state_stack;
    std::unique_ptr<HSMExitHandlersCompartment> __compartment;
    std::unique_ptr<HSMExitHandlersCompartment> __next_compartment;
    std::vector<HSMExitHandlersFrameContext> _context_stack;

    void __kernel(HSMExitHandlersFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMExitHandlersFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMExitHandlersFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMExitHandlersFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMExitHandlersFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        } else if (state_name == "Other") {
            _state_Other(__e);
        }
    }

    void __transition(std::unique_ptr<HSMExitHandlersCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Child(HSMExitHandlersFrameEvent& __e) {
        auto* __sv_comp = __compartment.get();
        while (__sv_comp && __sv_comp->state != "Child") { __sv_comp = __sv_comp->parent_compartment.get(); }
        if (__e._message == "<$") {
            int val = std::any_cast<int>(__sv_comp->state_vars["child_var"]);
            event_log.push_back(std::string("Child:exit(var=") + std::to_string(val) + ")");
        } else if (__e._message == "$>") {
            if (__compartment->state_vars.count("child_var") == 0) { __compartment->state_vars["child_var"] = std::any(42); }
            event_log.push_back("Child:enter");
        } else if (__e._message == "get_child_var") {
            _context_stack.back()._return = std::any(std::any_cast<int>(__sv_comp->state_vars["child_var"]));
            return;;
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Child"));
            return;;
        } else if (__e._message == "go_to_other") {
            auto __new_compartment = std::make_unique<HSMExitHandlersCompartment>("Other");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "go_to_parent") {
            auto __new_compartment = std::make_unique<HSMExitHandlersCompartment>("Parent");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Parent(HSMExitHandlersFrameEvent& __e) {
        if (__e._message == "<$") {
            event_log.push_back("Parent:exit");
        } else if (__e._message == "$>") {
            event_log.push_back("Parent:enter");
        } else if (__e._message == "get_child_var") {
            _context_stack.back()._return = std::any(-1);
            return;;
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Parent"));
            return;;
        } else if (__e._message == "go_to_child") {
            auto __new_compartment = std::make_unique<HSMExitHandlersCompartment>("Child");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "go_to_other") {
            auto __new_compartment = std::make_unique<HSMExitHandlersCompartment>("Other");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Other(HSMExitHandlersFrameEvent& __e) {
        if (__e._message == "$>") {
            event_log.push_back("Other:enter");
        } else if (__e._message == "get_child_var") {
            _context_stack.back()._return = std::any(-1);
            return;;
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Other"));
            return;;
        } else if (__e._message == "go_to_child") {
            auto __new_compartment = std::make_unique<HSMExitHandlersCompartment>("Child");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "go_to_parent") {
            auto __new_compartment = std::make_unique<HSMExitHandlersCompartment>("Parent");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    std::vector<std::string> event_log = {};

    HSMExitHandlers() {
        // HSM: Create parent compartment chain
        auto __parent_comp_0 = std::make_unique<HSMExitHandlersCompartment>("Parent");
        __compartment = std::make_unique<HSMExitHandlersCompartment>("Child");
        __compartment->parent_compartment = std::move(__parent_comp_0);
        HSMExitHandlersFrameEvent __frame_event("$>");
        HSMExitHandlersFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_other() {
        HSMExitHandlersFrameEvent __e("go_to_other");
        HSMExitHandlersFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_parent() {
        HSMExitHandlersFrameEvent __e("go_to_parent");
        HSMExitHandlersFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_child() {
        HSMExitHandlersFrameEvent __e("go_to_child");
        HSMExitHandlersFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMExitHandlersFrameEvent __e("get_log");
        HSMExitHandlersFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMExitHandlersFrameEvent __e("get_state");
        HSMExitHandlersFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_child_var() {
        HSMExitHandlersFrameEvent __e("get_child_var");
        HSMExitHandlersFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 48: HSM Exit Handlers ===\n");
    HSMExitHandlers s;

    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:enter") == log.end()) {
        printf("FAIL: Expected Child:enter on init\n");
        assert(false);
    }
    if (s.get_state() != "Child") {
        printf("FAIL: Expected Child\n");
        assert(false);
    }
    printf("TC2.4.0: Initial state is Child with enter - PASS\n");

    s.go_to_other();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:exit(var=42)") == log.end()) {
        printf("FAIL: Expected Child:exit\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Other:enter") == log.end()) {
        printf("FAIL: Expected Other:enter\n");
        assert(false);
    }
    printf("TC2.4.1: Child exit fires when transitioning out - PASS\n");

    if (std::find(log.begin(), log.end(), "Parent:exit") != log.end()) {
        printf("FAIL: Parent:exit should NOT fire for child exit\n");
        assert(false);
    }
    printf("TC2.4.2: Parent exit NOT fired for child exit - PASS\n");

    printf("TC2.4.3: Exit handler accesses state var (var=42) - PASS\n");

    s.go_to_parent();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Parent:enter") == log.end()) {
        printf("FAIL: Expected Parent:enter\n");
        assert(false);
    }

    s.go_to_other();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Parent:exit") == log.end()) {
        printf("FAIL: Expected Parent:exit\n");
        assert(false);
    }
    printf("TC2.4.4: Parent exit fires when leaving parent - PASS\n");

    printf("PASS: HSM exit handlers work correctly\n");
    return 0;
}
