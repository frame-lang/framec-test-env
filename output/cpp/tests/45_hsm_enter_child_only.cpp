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

class HSMEnterChildOnlyFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMEnterChildOnlyFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMEnterChildOnlyFrameContext {
public:
    HSMEnterChildOnlyFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMEnterChildOnlyFrameContext(HSMEnterChildOnlyFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMEnterChildOnlyCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMEnterChildOnlyFrameEvent> forward_event;
    std::unique_ptr<HSMEnterChildOnlyCompartment> parent_compartment;

    explicit HSMEnterChildOnlyCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HSMEnterChildOnlyCompartment> clone() const {
        auto c = std::make_unique<HSMEnterChildOnlyCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HSMEnterChildOnly {
private:
    std::vector<std::unique_ptr<HSMEnterChildOnlyCompartment>> _state_stack;
    std::unique_ptr<HSMEnterChildOnlyCompartment> __compartment;
    std::unique_ptr<HSMEnterChildOnlyCompartment> __next_compartment;
    std::vector<HSMEnterChildOnlyFrameContext> _context_stack;

    void __kernel(HSMEnterChildOnlyFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMEnterChildOnlyFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMEnterChildOnlyFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMEnterChildOnlyFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMEnterChildOnlyFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMEnterChildOnlyCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Parent(HSMEnterChildOnlyFrameEvent& __e) {
        if (__e._message == "forward_action") {
            event_log.push_back("Parent:forward_action");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Parent"));
            return;;
        }
    }

    void _state_Start(HSMEnterChildOnlyFrameEvent& __e) {
        if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Start"));
            return;;
        } else if (__e._message == "go_to_child") {
            auto __new_compartment = std::make_unique<HSMEnterChildOnlyCompartment>("Child");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Child(HSMEnterChildOnlyFrameEvent& __e) {
        if (__e._message == "$>") {
            event_log.push_back("Child:enter");
        } else if (__e._message == "forward_action") {
            event_log.push_back("Child:forward");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Child"));
            return;;
        }
    }

public:
    std::vector<std::string> event_log = {};

    HSMEnterChildOnly() {
        __compartment = std::make_unique<HSMEnterChildOnlyCompartment>("Start");
        HSMEnterChildOnlyFrameEvent __frame_event("$>");
        HSMEnterChildOnlyFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_child() {
        HSMEnterChildOnlyFrameEvent __e("go_to_child");
        HSMEnterChildOnlyFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forward_action() {
        HSMEnterChildOnlyFrameEvent __e("forward_action");
        HSMEnterChildOnlyFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMEnterChildOnlyFrameEvent __e("get_log");
        HSMEnterChildOnlyFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMEnterChildOnlyFrameEvent __e("get_state");
        HSMEnterChildOnlyFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 45: HSM Enter in Child Only ===\n");
    HSMEnterChildOnly s;

    if (s.get_state() != "Start") {
        printf("FAIL: Expected Start\n");
        assert(false);
    }
    printf("TC2.1.0: Initial state is Start - PASS\n");

    s.go_to_child();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:enter") == log.end()) {
        printf("FAIL: Expected Child:enter\n");
        assert(false);
    }
    if (s.get_state() != "Child") {
        printf("FAIL: Expected Child\n");
        assert(false);
    }
    printf("TC2.1.1: Child enter handler fires - PASS\n");

    printf("TC2.1.2: No error when parent lacks enter - PASS\n");

    s.forward_action();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:forward") == log.end()) {
        printf("FAIL: Expected Child:forward\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:forward_action") == log.end()) {
        printf("FAIL: Expected Parent handler\n");
        assert(false);
    }
    printf("TC2.1.3: Forward works without parent enter - PASS\n");

    printf("PASS: HSM enter in child only works correctly\n");
    return 0;
}
