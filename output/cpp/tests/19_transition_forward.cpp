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

class EventForwardTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    EventForwardTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class EventForwardTestFrameContext {
public:
    EventForwardTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    EventForwardTestFrameContext(EventForwardTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class EventForwardTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<EventForwardTestFrameEvent> forward_event;
    std::unique_ptr<EventForwardTestCompartment> parent_compartment;

    explicit EventForwardTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<EventForwardTestCompartment> clone() const {
        auto c = std::make_unique<EventForwardTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class EventForwardTest {
private:
    std::vector<std::unique_ptr<EventForwardTestCompartment>> _state_stack;
    std::unique_ptr<EventForwardTestCompartment> __compartment;
    std::unique_ptr<EventForwardTestCompartment> __next_compartment;
    std::vector<EventForwardTestFrameContext> _context_stack;

    void __kernel(EventForwardTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            EventForwardTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                EventForwardTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    EventForwardTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(EventForwardTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Working") {
            _state_Working(__e);
        }
    }

    void __transition(std::unique_ptr<EventForwardTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Working(EventForwardTestFrameEvent& __e) {
        if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "process") {
            event_log.push_back("working:process");
        }
    }

    void _state_Idle(EventForwardTestFrameEvent& __e) {
        if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "process") {
            event_log.push_back("idle:process:before");
            auto __new_compartment = std::make_unique<EventForwardTestCompartment>("Working");
            __new_compartment->parent_compartment = __compartment->clone();
            __new_compartment->forward_event = std::make_unique<EventForwardTestFrameEvent>(__e);
            __transition(std::move(__new_compartment));
            return;
            // This should NOT execute because -> => returns after dispatch
            event_log.push_back("idle:process:after");
        }
    }

public:
    std::vector<std::string> event_log = {};

    EventForwardTest() {
        __compartment = std::make_unique<EventForwardTestCompartment>("Idle");
        EventForwardTestFrameEvent __frame_event("$>");
        EventForwardTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void process() {
        EventForwardTestFrameEvent __e("process");
        EventForwardTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        EventForwardTestFrameEvent __e("get_log");
        EventForwardTestFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 19: Transition Forward (C++) ===\n");
    EventForwardTest s;
    s.process();
    auto log = s.get_log();

    if (std::find(log.begin(), log.end(), "idle:process:before") == log.end()) {
        printf("FAIL: Expected 'idle:process:before' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "working:process") == log.end()) {
        printf("FAIL: Expected 'working:process' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "idle:process:after") != log.end()) {
        printf("FAIL: Should NOT have 'idle:process:after' in log\n");
        assert(false);
    }

    printf("PASS: Transition forward works correctly\n");
    return 0;
}
