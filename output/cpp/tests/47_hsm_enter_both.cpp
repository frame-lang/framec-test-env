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

class HSMEnterBothFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMEnterBothFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMEnterBothFrameContext {
public:
    HSMEnterBothFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMEnterBothFrameContext(HSMEnterBothFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMEnterBothCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMEnterBothFrameEvent> forward_event;
    std::unique_ptr<HSMEnterBothCompartment> parent_compartment;

    explicit HSMEnterBothCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HSMEnterBothCompartment> clone() const {
        auto c = std::make_unique<HSMEnterBothCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HSMEnterBoth {
private:
    std::vector<std::unique_ptr<HSMEnterBothCompartment>> _state_stack;
    std::unique_ptr<HSMEnterBothCompartment> __compartment;
    std::unique_ptr<HSMEnterBothCompartment> __next_compartment;
    std::vector<HSMEnterBothFrameContext> _context_stack;

    void __kernel(HSMEnterBothFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMEnterBothFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMEnterBothFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMEnterBothFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMEnterBothFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMEnterBothCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(HSMEnterBothFrameEvent& __e) {
        if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Start"));
            return;;
        } else if (__e._message == "go_to_child") {
            auto __new_compartment = std::make_unique<HSMEnterBothCompartment>("Child");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "go_to_parent") {
            auto __new_compartment = std::make_unique<HSMEnterBothCompartment>("Parent");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Child(HSMEnterBothFrameEvent& __e) {
        if (__e._message == "$>") {
            event_log.push_back("Child:enter");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Child"));
            return;;
        } else if (__e._message == "go_to_parent") {
            auto __new_compartment = std::make_unique<HSMEnterBothCompartment>("Parent");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Parent(HSMEnterBothFrameEvent& __e) {
        if (__e._message == "$>") {
            event_log.push_back("Parent:enter");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Parent"));
            return;;
        } else if (__e._message == "go_to_child") {
            auto __new_compartment = std::make_unique<HSMEnterBothCompartment>("Child");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    std::vector<std::string> event_log = {};

    HSMEnterBoth() {
        __compartment = std::make_unique<HSMEnterBothCompartment>("Start");
        HSMEnterBothFrameEvent __frame_event("$>");
        HSMEnterBothFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_child() {
        HSMEnterBothFrameEvent __e("go_to_child");
        HSMEnterBothFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_parent() {
        HSMEnterBothFrameEvent __e("go_to_parent");
        HSMEnterBothFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMEnterBothFrameEvent __e("get_log");
        HSMEnterBothFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMEnterBothFrameEvent __e("get_state");
        HSMEnterBothFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 47: HSM Enter in Both ===\n");
    HSMEnterBoth s;

    s.go_to_child();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:enter") == log.end()) {
        printf("FAIL: Expected Child:enter\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:enter") != log.end()) {
        printf("FAIL: Parent:enter should NOT fire when entering child\n");
        assert(false);
    }
    if (s.get_state() != "Child") {
        printf("FAIL: Expected Child\n");
        assert(false);
    }
    printf("TC2.3.1: Only child's enter fires when entering child - PASS\n");

    s.go_to_parent();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Parent:enter") == log.end()) {
        printf("FAIL: Expected Parent:enter\n");
        assert(false);
    }
    if (s.get_state() != "Parent") {
        printf("FAIL: Expected Parent\n");
        assert(false);
    }
    printf("TC2.3.2: Parent's enter fires when transitioning to parent - PASS\n");

    int childCount = std::count(log.begin(), log.end(), "Child:enter");
    int parentCount = std::count(log.begin(), log.end(), "Parent:enter");
    if (childCount != 1) {
        printf("FAIL: Expected exactly 1 Child:enter\n");
        assert(false);
    }
    if (parentCount != 1) {
        printf("FAIL: Expected exactly 1 Parent:enter\n");
        assert(false);
    }
    printf("TC2.3.3: No implicit cascading of enter handlers - PASS\n");

    s.go_to_child();
    log = s.get_log();
    int childCount2 = std::count(log.begin(), log.end(), "Child:enter");
    int parentCount2 = std::count(log.begin(), log.end(), "Parent:enter");
    if (childCount2 != 2) {
        printf("FAIL: Expected 2 Child:enter\n");
        assert(false);
    }
    if (parentCount2 != 1) {
        printf("FAIL: Expected still 1 Parent:enter\n");
        assert(false);
    }
    printf("TC2.3.4: Re-entering child fires child enter again - PASS\n");

    printf("PASS: HSM enter in both works correctly\n");
    return 0;
}
