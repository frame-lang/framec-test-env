#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <cassert>

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

    int log_code;

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
            self->log_code = self->log_code + 1;  // "Child:handled_event"
            }
            return;
        } else if (__e._message == "get_log_code") {
            {
            _context_stack.back()._return = self->log_code;
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
            self->log_code = self->log_code + 10;  // "Parent:handled_event"
            }
            return;
        } else if (__e._message == "unhandled_event") {
            {
            self->log_code = self->log_code + 100;  // "Parent:unhandled_event"
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
    HSMDefaultForward() {
        __compartment = std::make_unique<HSMDefaultForwardCompartment>("Child");
        HSMDefaultForwardFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void handled_event() {
        HSMDefaultForwardFrameEvent __e("handled_event");
        HSMDefaultForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void unhandled_event() {
        HSMDefaultForwardFrameEvent __e("unhandled_event");
        HSMDefaultForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_log_code() {
        HSMDefaultForwardFrameEvent __e("get_log_code");
        HSMDefaultForwardFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 30: HSM State-Level Default Forward ===" << std::endl;
    HSMDefaultForward s;

    s.handled_event();
    int log_code = s.get_log_code();
    // Child handles it: +1
    assert(log_code == 1);
    std::cout << "After handled_event: log_code = " << log_code << std::endl;

    s.unhandled_event();
    log_code = s.get_log_code();
    // Child doesn't handle it, forwards to Parent: +100
    // Total: 1 + 100 = 101
    assert(log_code == 101);
    std::cout << "After unhandled_event (forwarded): log_code = " << log_code << std::endl;

    std::cout << "PASS: HSM state-level default forward works correctly" << std::endl;
    return 0;
}
