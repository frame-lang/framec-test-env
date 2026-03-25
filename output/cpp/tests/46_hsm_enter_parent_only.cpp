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

class HSMEnterParentOnlyFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMEnterParentOnlyFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMEnterParentOnlyFrameContext {
public:
    HSMEnterParentOnlyFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMEnterParentOnlyFrameContext(HSMEnterParentOnlyFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMEnterParentOnlyCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMEnterParentOnlyFrameEvent> forward_event;
    std::unique_ptr<HSMEnterParentOnlyCompartment> parent_compartment;

    explicit HSMEnterParentOnlyCompartment(const std::string& state) : state(state) {}
};

class HSMEnterParentOnly {
private:
    std::unique_ptr<HSMEnterParentOnlyCompartment> __compartment;
    std::unique_ptr<HSMEnterParentOnlyCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMEnterParentOnlyCompartment>> _state_stack;
    std::vector<HSMEnterParentOnlyFrameContext> _context_stack;

    std::vector<std::string> event_log = {};

    void __kernel(HSMEnterParentOnlyFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMEnterParentOnlyFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMEnterParentOnlyFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMEnterParentOnlyFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMEnterParentOnlyFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMEnterParentOnlyCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(HSMEnterParentOnlyFrameEvent& __e) {
        if (__e._message == "go_to_child") {
            {
            auto __comp = std::make_unique<HSMEnterParentOnlyCompartment>("Child");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "go_to_parent") {
            {
            auto __comp = std::make_unique<HSMEnterParentOnlyCompartment>("Parent");
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
            _context_stack.back()._return = std::string("Start");
            return;
            }
            return;
        }
    }

    void _state_Child(HSMEnterParentOnlyFrameEvent& __e) {
        if (__e._message == "go_to_parent") {
            {
            auto __comp = std::make_unique<HSMEnterParentOnlyCompartment>("Parent");
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
        }
    }

    void _state_Parent(HSMEnterParentOnlyFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back("Parent:enter");
            }
            return;
        } else if (__e._message == "go_to_child") {
            {
            auto __comp = std::make_unique<HSMEnterParentOnlyCompartment>("Child");
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
        }
    }

public:
    HSMEnterParentOnly() {
        __compartment = std::make_unique<HSMEnterParentOnlyCompartment>("Start");
        event_log = {};
        HSMEnterParentOnlyFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void go_to_child() {
        HSMEnterParentOnlyFrameEvent __e("go_to_child");
        HSMEnterParentOnlyFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_parent() {
        HSMEnterParentOnlyFrameEvent __e("go_to_parent");
        HSMEnterParentOnlyFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMEnterParentOnlyFrameEvent __e("get_log");
        HSMEnterParentOnlyFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMEnterParentOnlyFrameEvent __e("get_state");
        HSMEnterParentOnlyFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 46: HSM Enter in Parent Only ===\n");
    HSMEnterParentOnly s;

    s.go_to_child();
    if (s.get_state() != "Child") {
        printf("FAIL: Expected Child\n");
        assert(false);
    }
    auto log = s.get_log();
    printf("TC2.2.1: Child enters without error - PASS\n");

    if (std::find(log.begin(), log.end(), "Parent:enter") != log.end()) {
        printf("FAIL: Parent:enter should NOT fire for child entry\n");
        assert(false);
    }
    printf("TC2.2.2: Parent enter NOT auto-fired for child - PASS\n");

    s.go_to_parent();
    if (s.get_state() != "Parent") {
        printf("FAIL: Expected Parent\n");
        assert(false);
    }
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Parent:enter") == log.end()) {
        printf("FAIL: Expected Parent:enter when transitioning to Parent\n");
        assert(false);
    }
    printf("TC2.2.3: Parent enter fires when transitioning to Parent - PASS\n");

    s.go_to_child();
    if (s.get_state() != "Child") {
        printf("FAIL: Expected Child\n");
        assert(false);
    }
    log = s.get_log();
    int count = std::count(log.begin(), log.end(), "Parent:enter");
    if (count != 1) {
        printf("FAIL: Expected exactly 1 Parent:enter\n");
        assert(false);
    }
    printf("TC2.2.4: Return to child, parent enter count unchanged - PASS\n");

    printf("PASS: HSM enter in parent only works correctly\n");
    return 0;
}
