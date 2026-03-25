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

class HSMForwardFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMForwardFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMForwardFrameContext {
public:
    HSMForwardFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMForwardFrameContext(HSMForwardFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMForwardCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMForwardFrameEvent> forward_event;
    std::unique_ptr<HSMForwardCompartment> parent_compartment;

    explicit HSMForwardCompartment(const std::string& state) : state(state) {}
};

class HSMForward {
private:
    std::unique_ptr<HSMForwardCompartment> __compartment;
    std::unique_ptr<HSMForwardCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMForwardCompartment>> _state_stack;
    std::vector<HSMForwardFrameContext> _context_stack;

    std::vector<std::string> event_log = {};

    void __kernel(HSMForwardFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMForwardFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMForwardFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMForwardFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMForwardFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMForwardCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Child(HSMForwardFrameEvent& __e) {
        if (__e._message == "event_a") {
            {
            event_log.push_back("Child:event_a");
            }
            return;
        } else if (__e._message == "event_b") {
            {
            event_log.push_back("Child:event_b_forward");
            _state_Parent(__e);
            return;
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        }
    }

    void _state_Parent(HSMForwardFrameEvent& __e) {
        if (__e._message == "event_a") {
            {
            event_log.push_back("Parent:event_a");
            }
            return;
        } else if (__e._message == "event_b") {
            {
            event_log.push_back("Parent:event_b");
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        }
    }

public:
    HSMForward() {
        __compartment = std::make_unique<HSMForwardCompartment>("Child");
        event_log = {};
        HSMForwardFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void event_a() {
        HSMForwardFrameEvent __e("event_a");
        HSMForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void event_b() {
        HSMForwardFrameEvent __e("event_b");
        HSMForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMForwardFrameEvent __e("get_log");
        HSMForwardFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 08: HSM Forward ===\n");
    HSMForward s;

    s.event_a();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:event_a") == log.end()) {
        printf("FAIL: Expected 'Child:event_a' in log\n");
        assert(false);
    }
    printf("After event_a: Child:event_a found\n");

    s.event_b();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:event_b_forward") == log.end()) {
        printf("FAIL: Expected 'Child:event_b_forward' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:event_b") == log.end()) {
        printf("FAIL: Expected 'Parent:event_b' in log (forwarded)\n");
        assert(false);
    }
    printf("After event_b (forwarded): Child:event_b_forward and Parent:event_b found\n");

    printf("PASS: HSM forward works correctly\n");
    return 0;
}
