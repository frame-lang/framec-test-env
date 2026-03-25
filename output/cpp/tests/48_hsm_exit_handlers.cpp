#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


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
};

class HSMExitHandlers {
private:
    std::unique_ptr<HSMExitHandlersCompartment> __compartment;
    std::unique_ptr<HSMExitHandlersCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMExitHandlersCompartment>> _state_stack;
    std::vector<HSMExitHandlersFrameContext> _context_stack;

    std::vector<std::string> event_log = {};

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
        if (__e._message == "$>") {
            {
            event_log.push_back("Child:enter");
            }
            return;
        } else if (__e._message == "<$") {
            {
            int val = std::any_cast<int>(__compartment->state_vars["child_var"]);
            event_log.push_back(std::string("Child:exit(var=") + std::to_string(val) + ")");
            }
            return;
        } else if (__e._message == "go_to_other") {
            {
            auto __comp = std::make_unique<HSMExitHandlersCompartment>("Other");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "go_to_parent") {
            {
            auto __comp = std::make_unique<HSMExitHandlersCompartment>("Parent");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Child");
            return;
            }
            return;
        } else if (__e._message == "get_child_var") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["child_var"]);
            return;
            }
            return;
        }
    }

    void _state_Parent(HSMExitHandlersFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back("Parent:enter");
            }
            return;
        } else if (__e._message == "<$") {
            {
            event_log.push_back("Parent:exit");
            }
            return;
        } else if (__e._message == "go_to_child") {
            {
            auto __comp = std::make_unique<HSMExitHandlersCompartment>("Child");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "go_to_other") {
            {
            auto __comp = std::make_unique<HSMExitHandlersCompartment>("Other");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Parent");
            return;
            }
            return;
        } else if (__e._message == "get_child_var") {
            {
            _context_stack.back()._return = -1;
            return;
            }
            return;
        }
    }

    void _state_Other(HSMExitHandlersFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back("Other:enter");
            }
            return;
        } else if (__e._message == "go_to_child") {
            {
            auto __comp = std::make_unique<HSMExitHandlersCompartment>("Child");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "go_to_parent") {
            {
            auto __comp = std::make_unique<HSMExitHandlersCompartment>("Parent");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Other");
            return;
            }
            return;
        } else if (__e._message == "get_child_var") {
            {
            _context_stack.back()._return = -1;
            return;
            }
            return;
        }
    }

public:
    HSMExitHandlers() {
        __compartment = std::make_unique<HSMExitHandlersCompartment>("Child");
        __compartment->state_vars["child_var"] = 42;
        event_log = {};
        HSMExitHandlersFrameEvent __frame_event("$>");
        __kernel(__frame_event);
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
