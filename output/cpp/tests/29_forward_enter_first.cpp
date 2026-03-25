#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <cassert>

class ForwardEnterFirstFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ForwardEnterFirstFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ForwardEnterFirstFrameContext {
public:
    ForwardEnterFirstFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ForwardEnterFirstFrameContext(ForwardEnterFirstFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ForwardEnterFirstCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ForwardEnterFirstFrameEvent> forward_event;
    std::unique_ptr<ForwardEnterFirstCompartment> parent_compartment;

    explicit ForwardEnterFirstCompartment(const std::string& state) : state(state) {}
};

class ForwardEnterFirst {
private:
    std::unique_ptr<ForwardEnterFirstCompartment> __compartment;
    std::unique_ptr<ForwardEnterFirstCompartment> __next_compartment;
    std::vector<std::unique_ptr<ForwardEnterFirstCompartment>> _state_stack;
    std::vector<ForwardEnterFirstFrameContext> _context_stack;

    int log_code;

    void __kernel(ForwardEnterFirstFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ForwardEnterFirstFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ForwardEnterFirstFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ForwardEnterFirstFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ForwardEnterFirstFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Working") {
            _state_Working(__e);
        }
    }

    void __transition(std::unique_ptr<ForwardEnterFirstCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(ForwardEnterFirstFrameEvent& __e) {
        if (__e._message == "process") {
            {
            -> => $Working
            }
            return;
        } else if (__e._message == "get_counter") {
            {
            _context_stack.back()._return = -1;
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

    void _state_Working(ForwardEnterFirstFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            self->log_code = self->log_code + 1;  // "Working:enter"
            }
            return;
        } else if (__e._message == "process") {
            {
            self->log_code = self->log_code + 10;  // "Working:process:counter=100"
            __compartment->state_vars["counter"] = std::any(std::any_cast<int>(__compartment->state_vars["counter"]) + 1);
            }
            return;
        } else if (__e._message == "get_counter") {
            {
            _context_stack.back()._return = std::any_cast<int>(__compartment->state_vars["counter"]);
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
    ForwardEnterFirst() {
        __compartment = std::make_unique<ForwardEnterFirstCompartment>("Idle");
        ForwardEnterFirstFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void process() {
        ForwardEnterFirstFrameEvent __e("process");
        ForwardEnterFirstFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_counter() {
        ForwardEnterFirstFrameEvent __e("get_counter");
        ForwardEnterFirstFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_log_code() {
        ForwardEnterFirstFrameEvent __e("get_log_code");
        ForwardEnterFirstFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 29: Forward Enter First ===" << std::endl;
    ForwardEnterFirst s;

    // Initial state is Idle
    int counter = s.get_counter();
    assert(counter == -1);

    // Call process - should forward to Working
    // Correct behavior: $> runs first (inits counter=100, logs +1)
    // Then process runs (logs +10, increments to 101)
    s.process();

    // Check counter was initialized and incremented
    counter = s.get_counter();
    int log_code = s.get_log_code();
    std::cout << "Counter after forward: " << counter << std::endl;
    std::cout << "Log code: " << log_code << std::endl;

    // Verify $> ran first (log_code has +1)
    // Verify process ran after $> (log_code has +10)
    // Total should be 11
    assert(log_code == 11);

    // Verify counter was incremented from 100 to 101
    assert(counter == 101);

    std::cout << "PASS: Forward sends $> first for non-$> events" << std::endl;
    return 0;
}
