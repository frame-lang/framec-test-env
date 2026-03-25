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
};

class HSMDefaultForward {
private:
    std::unique_ptr<HSMDefaultForwardCompartment> __compartment;
    std::unique_ptr<HSMDefaultForwardCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMDefaultForwardCompartment>> _state_stack;
    std::vector<HSMDefaultForwardFrameContext> _context_stack;

    log: std::vector<std::string> = {};

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
        if (__e._message == "handled_event") {
            {
            log.push_back("Child:handled_event");
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = log;
            return;
            }
            return;
        } else if (true) {
            _state_Parent(__e);
        }
    }

    void _state_Parent(HSMDefaultForwardFrameEvent& __e) {
        if (__e._message == "handled_event") {
            {
            log.push_back("Parent:handled_event");
            }
            return;
        } else if (__e._message == "unhandled_event") {
            {
            log.push_back("Parent:unhandled_event");
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = log;
            return;
            }
            return;
        }
    }

public:
    HSMDefaultForward() {
        __compartment = std::make_unique<HSMDefaultForwardCompartment>("Child");
        log = {};
        HSMDefaultForwardFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void handled_event() {
        HSMDefaultForwardFrameEvent __e("handled_event");
        HSMDefaultForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void unhandled_event() {
        HSMDefaultForwardFrameEvent __e("unhandled_event");
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
    printf("=== Test 30: HSM State-Level Default Forward ===\n");
    HSMDefaultForward s;

    s.handled_event();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:handled_event") == log.end()) {
        printf("FAIL: Expected 'Child:handled_event' in log\n");
        assert(false);
    }
    printf("After handled_event: Child:handled_event found\n");

    s.unhandled_event();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Parent:unhandled_event") == log.end()) {
        printf("FAIL: Expected 'Parent:unhandled_event' in log (forwarded)\n");
        assert(false);
    }
    printf("After unhandled_event (forwarded): Parent:unhandled_event found\n");

    printf("PASS: HSM state-level default forward works correctly\n");
    return 0;
}
