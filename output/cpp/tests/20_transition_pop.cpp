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

class TransitionPopTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    TransitionPopTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class TransitionPopTestFrameContext {
public:
    TransitionPopTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    TransitionPopTestFrameContext(TransitionPopTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class TransitionPopTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<TransitionPopTestFrameEvent> forward_event;
    std::unique_ptr<TransitionPopTestCompartment> parent_compartment;

    explicit TransitionPopTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<TransitionPopTestCompartment> clone() const {
        auto c = std::make_unique<TransitionPopTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class TransitionPopTest {
private:
    std::vector<std::unique_ptr<TransitionPopTestCompartment>> _state_stack;
    std::unique_ptr<TransitionPopTestCompartment> __compartment;
    std::unique_ptr<TransitionPopTestCompartment> __next_compartment;
    std::vector<TransitionPopTestFrameContext> _context_stack;

    void __kernel(TransitionPopTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            TransitionPopTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                TransitionPopTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    TransitionPopTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(TransitionPopTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Working") {
            _state_Working(__e);
        }
    }

    void __transition(std::unique_ptr<TransitionPopTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(TransitionPopTestFrameEvent& __e) {
        if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Idle"));
            return;;
        } else if (__e._message == "process") {
            event_log.push_back("idle:process");
        } else if (__e._message == "start") {
            event_log.push_back("idle:start:push");
            _state_stack.push_back(__compartment->clone());
            auto __new_compartment = std::make_unique<TransitionPopTestCompartment>("Working");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Working(TransitionPopTestFrameEvent& __e) {
        if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Working"));
            return;;
        } else if (__e._message == "process") {
            event_log.push_back("working:process:before_pop");
            auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
            // This should NOT execute because pop transitions away
            event_log.push_back("working:process:after_pop");
        }
    }

public:
    std::vector<std::string> event_log = {};

    TransitionPopTest() {
        __compartment = std::make_unique<TransitionPopTestCompartment>("Idle");
        TransitionPopTestFrameEvent __frame_event("$>");
        TransitionPopTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void start() {
        TransitionPopTestFrameEvent __e("start");
        TransitionPopTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void process() {
        TransitionPopTestFrameEvent __e("process");
        TransitionPopTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        TransitionPopTestFrameEvent __e("get_state");
        TransitionPopTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::vector<std::string> get_log() {
        TransitionPopTestFrameEvent __e("get_log");
        TransitionPopTestFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 20: Transition Pop (C++) ===\n");
    TransitionPopTest s;

    if (s.get_state() != "Idle") {
        printf("FAIL: Expected 'Idle', got '%s'\n", s.get_state().c_str());
        assert(false);
    }
    printf("Initial state: %s\n", s.get_state().c_str());

    s.start();
    if (s.get_state() != "Working") {
        printf("FAIL: Expected 'Working', got '%s'\n", s.get_state().c_str());
        assert(false);
    }
    printf("After start(): %s\n", s.get_state().c_str());

    s.process();
    if (s.get_state() != "Idle") {
        printf("FAIL: Expected 'Idle' after pop, got '%s'\n", s.get_state().c_str());
        assert(false);
    }
    printf("After process() with pop: %s\n", s.get_state().c_str());

    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "idle:start:push") == log.end()) {
        printf("FAIL: Expected 'idle:start:push' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "working:process:before_pop") == log.end()) {
        printf("FAIL: Expected 'working:process:before_pop' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "working:process:after_pop") != log.end()) {
        printf("FAIL: Should NOT have 'working:process:after_pop' in log\n");
        assert(false);
    }

    printf("PASS: Transition pop works correctly\n");
    return 0;
}
