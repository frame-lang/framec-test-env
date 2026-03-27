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

class HSMOmittedHandlersFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMOmittedHandlersFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMOmittedHandlersFrameContext {
public:
    HSMOmittedHandlersFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMOmittedHandlersFrameContext(HSMOmittedHandlersFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMOmittedHandlersCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMOmittedHandlersFrameEvent> forward_event;
    std::unique_ptr<HSMOmittedHandlersCompartment> parent_compartment;

    explicit HSMOmittedHandlersCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HSMOmittedHandlersCompartment> clone() const {
        auto c = std::make_unique<HSMOmittedHandlersCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HSMOmittedHandlers {
private:
    std::vector<std::unique_ptr<HSMOmittedHandlersCompartment>> _state_stack;
    std::unique_ptr<HSMOmittedHandlersCompartment> __compartment;
    std::unique_ptr<HSMOmittedHandlersCompartment> __next_compartment;
    std::vector<HSMOmittedHandlersFrameContext> _context_stack;

    void __kernel(HSMOmittedHandlersFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMOmittedHandlersFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMOmittedHandlersFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMOmittedHandlersFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMOmittedHandlersFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMOmittedHandlersCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Child(HSMOmittedHandlersFrameEvent& __e) {
        if (__e._message == "forwarded_explicitly") {
            event_log.push_back("Child:before_forward");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Child"));
            return;;
        } else if (__e._message == "handled_by_child") {
            event_log.push_back("Child:handled_by_child");
        }
    }

    void _state_Parent(HSMOmittedHandlersFrameEvent& __e) {
        if (__e._message == "forwarded_explicitly") {
            event_log.push_back("Parent:forwarded_explicitly");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Parent"));
            return;;
        } else if (__e._message == "handled_by_child") {
            event_log.push_back("Parent:handled_by_child");
        } else if (__e._message == "unhandled_no_forward") {
            event_log.push_back("Parent:unhandled_no_forward");
        }
    }

public:
    std::vector<std::string> event_log = {};

    HSMOmittedHandlers() {
        // HSM: Create parent compartment chain
        auto __parent_comp_0 = std::make_unique<HSMOmittedHandlersCompartment>("Parent");
        __compartment = std::make_unique<HSMOmittedHandlersCompartment>("Child");
        __compartment->parent_compartment = std::move(__parent_comp_0);
        HSMOmittedHandlersFrameEvent __frame_event("$>");
        HSMOmittedHandlersFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void handled_by_child() {
        HSMOmittedHandlersFrameEvent __e("handled_by_child");
        HSMOmittedHandlersFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forwarded_explicitly() {
        HSMOmittedHandlersFrameEvent __e("forwarded_explicitly");
        HSMOmittedHandlersFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void unhandled_no_forward() {
        HSMOmittedHandlersFrameEvent __e("unhandled_no_forward");
        HSMOmittedHandlersFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMOmittedHandlersFrameEvent __e("get_log");
        HSMOmittedHandlersFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMOmittedHandlersFrameEvent __e("get_state");
        HSMOmittedHandlersFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

class HSMDefaultForwardFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMDefaultForwardFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMDefaultForwardFrameContext {
public:
    HSMDefaultForwardFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMDefaultForwardFrameContext(HSMDefaultForwardFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMDefaultForwardCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMDefaultForwardFrameEvent> forward_event;
    std::unique_ptr<HSMDefaultForwardCompartment> parent_compartment;

    explicit HSMDefaultForwardCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HSMDefaultForwardCompartment> clone() const {
        auto c = std::make_unique<HSMDefaultForwardCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HSMDefaultForward {
private:
    std::vector<std::unique_ptr<HSMDefaultForwardCompartment>> _state_stack;
    std::unique_ptr<HSMDefaultForwardCompartment> __compartment;
    std::unique_ptr<HSMDefaultForwardCompartment> __next_compartment;
    std::vector<HSMDefaultForwardFrameContext> _context_stack;

    void __kernel(HSMDefaultForwardFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMDefaultForwardFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMDefaultForwardFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMDefaultForwardFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMDefaultForwardFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMDefaultForwardCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Child(HSMDefaultForwardFrameEvent& __e) {
        if (__e._message == "child_handled") {
            event_log.push_back("Child:child_handled");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else {
            _state_Parent(__e);
        }
    }

    void _state_Parent(HSMDefaultForwardFrameEvent& __e) {
        if (__e._message == "both_respond") {
            event_log.push_back("Parent:both_respond");
        } else if (__e._message == "child_handled") {
            event_log.push_back("Parent:child_handled");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "parent_handled") {
            event_log.push_back("Parent:parent_handled");
        }
    }

public:
    std::vector<std::string> event_log = {};

    HSMDefaultForward() {
        // HSM: Create parent compartment chain
        auto __parent_comp_0 = std::make_unique<HSMDefaultForwardCompartment>("Parent");
        __compartment = std::make_unique<HSMDefaultForwardCompartment>("Child");
        __compartment->parent_compartment = std::move(__parent_comp_0);
        HSMDefaultForwardFrameEvent __frame_event("$>");
        HSMDefaultForwardFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void child_handled() {
        HSMDefaultForwardFrameEvent __e("child_handled");
        HSMDefaultForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void parent_handled() {
        HSMDefaultForwardFrameEvent __e("parent_handled");
        HSMDefaultForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void both_respond() {
        HSMDefaultForwardFrameEvent __e("both_respond");
        HSMDefaultForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMDefaultForwardFrameEvent __e("get_log");
        HSMDefaultForwardFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 50: HSM Omitted Handlers ===\n");

    // Part 1: Explicit forwarding vs no forwarding
    HSMOmittedHandlers s1;

    s1.handled_by_child();
    auto log = s1.get_log();
    if (std::find(log.begin(), log.end(), "Child:handled_by_child") == log.end()) {
        printf("FAIL: Expected Child handler\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:handled_by_child") != log.end()) {
        printf("FAIL: Parent should NOT be called\n");
        assert(false);
    }
    printf("TC2.6.1: Handled by child, not forwarded - PASS\n");

    s1.forwarded_explicitly();
    log = s1.get_log();
    if (std::find(log.begin(), log.end(), "Child:before_forward") == log.end()) {
        printf("FAIL: Expected Child forward\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:forwarded_explicitly") == log.end()) {
        printf("FAIL: Expected Parent handler\n");
        assert(false);
    }
    printf("TC2.6.2: Explicitly forwarded to parent - PASS\n");

    s1.unhandled_no_forward();
    log = s1.get_log();
    if (std::find(log.begin(), log.end(), "Parent:unhandled_no_forward") != log.end()) {
        printf("FAIL: Unhandled should be ignored\n");
        assert(false);
    }
    printf("TC2.6.3: Unhandled (no forward) is silently ignored - PASS\n");

    // Part 2: State-level default forward
    HSMDefaultForward s2;

    s2.child_handled();
    log = s2.get_log();
    if (std::find(log.begin(), log.end(), "Child:child_handled") == log.end()) {
        printf("FAIL: Expected Child handler\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:child_handled") != log.end()) {
        printf("FAIL: Handled by child, not forwarded\n");
        assert(false);
    }
    printf("TC2.6.4: Child handles, not forwarded - PASS\n");

    s2.parent_handled();
    log = s2.get_log();
    if (std::find(log.begin(), log.end(), "Parent:parent_handled") == log.end()) {
        printf("FAIL: Expected Parent handler\n");
        assert(false);
    }
    printf("TC2.6.5: Unhandled forwarded via state-level => $^ - PASS\n");

    s2.both_respond();
    log = s2.get_log();
    if (std::find(log.begin(), log.end(), "Parent:both_respond") == log.end()) {
        printf("FAIL: Expected Parent handler\n");
        assert(false);
    }
    printf("TC2.6.6: Default forward works for multiple events - PASS\n");

    printf("PASS: HSM omitted handlers work correctly\n");
    return 0;
}
