#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <cassert>

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
};

class TransitionPopTest {
private:
    std::unique_ptr<TransitionPopTestCompartment> __compartment;
    std::unique_ptr<TransitionPopTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<TransitionPopTestCompartment>> _state_stack;
    std::vector<TransitionPopTestFrameContext> _context_stack;

    int log_code;

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
        if (__e._message == "start") {
            {
            self->log_code = self->log_code + 1;  // "idle:start:push"
            _state_stack.push_back(std::make_unique<TransitionPopTestCompartment>(__compartment->state));
            _state_stack.back()->state_vars = __compartment->state_vars;
            _state_stack.back()->state_args = __compartment->state_args;
            auto __comp = std::make_unique<TransitionPopTestCompartment>("Working");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "process") {
            {
            self->log_code = self->log_code + 10;  // "idle:process"
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = 1;
            return;
            }
            return;
        } else if (__e._message == "get_log_code") {
            {
            _context_stack.back()._return = self->log_code;
            return;
            }
            return;
        }
    }

    void _state_Working(TransitionPopTestFrameEvent& __e) {
        if (__e._message == "process") {
            {
            self->log_code = self->log_code + 100;  // "working:process:before_pop"
            auto __popped = std::move(_state_stack.back());
            _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
            // This should NOT execute because pop transitions away
            self->log_code = self->log_code + 1000;  // "working:process:after_pop"
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = 2;
            return;
            }
            return;
        } else if (__e._message == "get_log_code") {
            {
            _context_stack.back()._return = self->log_code;
            return;
            }
            return;
        }
    }

public:
    TransitionPopTest() {
        __compartment = std::make_unique<TransitionPopTestCompartment>("Idle");
        TransitionPopTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void start() {
        TransitionPopTestFrameEvent __e("start");
        TransitionPopTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void process() {
        TransitionPopTestFrameEvent __e("process");
        TransitionPopTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_state() {
        TransitionPopTestFrameEvent __e("get_state");
        TransitionPopTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_log_code() {
        TransitionPopTestFrameEvent __e("get_log_code");
        TransitionPopTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 20: Transition Pop ===" << std::endl;
    TransitionPopTest s;

    // Initial state should be Idle (1)
    int state = s.get_state();
    assert(state == 1);
    std::cout << "Initial state: " << state << " (Idle)" << std::endl;

    // start() pushes Idle, transitions to Working
    s.start();
    state = s.get_state();
    assert(state == 2);
    std::cout << "After start(): " << state << " (Working)" << std::endl;

    // process() in Working does pop transition back to Idle
    s.process();
    state = s.get_state();
    assert(state == 1);
    std::cout << "After process() with pop: " << state << " (Idle)" << std::endl;

    int log_code = s.get_log_code();
    std::cout << "Log code: " << log_code << std::endl;

    // Verify log contents: 1 (idle:start) + 100 (working:process:before_pop) = 101
    // Should NOT have +1000 (working:process:after_pop)
    assert(log_code == 101);

    std::cout << "PASS: Transition pop works correctly" << std::endl;
    return 0;
}
