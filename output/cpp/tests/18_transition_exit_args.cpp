#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class TransitionExitArgsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    TransitionExitArgsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class TransitionExitArgsFrameContext {
public:
    TransitionExitArgsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    TransitionExitArgsFrameContext(TransitionExitArgsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class TransitionExitArgsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<TransitionExitArgsFrameEvent> forward_event;
    std::unique_ptr<TransitionExitArgsCompartment> parent_compartment;

    explicit TransitionExitArgsCompartment(const std::string& state) : state(state) {}
};

class TransitionExitArgs {
private:
    std::unique_ptr<TransitionExitArgsCompartment> __compartment;
    std::unique_ptr<TransitionExitArgsCompartment> __next_compartment;
    std::vector<std::unique_ptr<TransitionExitArgsCompartment>> _state_stack;
    std::vector<TransitionExitArgsFrameContext> _context_stack;

    int exit_code;
    int enter_done;

    void __kernel(TransitionExitArgsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            TransitionExitArgsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                TransitionExitArgsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    TransitionExitArgsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(TransitionExitArgsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Active") {
            _state_Active(__e);
        } else if (state_name == "Done") {
            _state_Done(__e);
        }
    }

    void __transition(std::unique_ptr<TransitionExitArgsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Active(TransitionExitArgsFrameEvent& __e) {
        if (__e._message == "<$") {
            {
            std::cout << "exit:reason=" << reason << ",code=" << code << std::endl;
            self->exit_code = code;
            }
            return;
        } else if (__e._message == "leave") {
            {
            std::cout << "leaving" << std::endl;
            ("cleanup", 42) -> $Done
            }
            return;
        } else if (__e._message == "get_exit_code") {
            {
            _context_stack.back()._return = self->exit_code;
            return;
            }
            return;
        }
    }

    void _state_Done(TransitionExitArgsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            std::cout << "enter:done" << std::endl;
            self->enter_done = 1;
            }
            return;
        } else if (__e._message == "get_exit_code") {
            {
            _context_stack.back()._return = self->exit_code;
            return;
            }
            return;
        }
    }

public:
    TransitionExitArgs() {
        __compartment = std::make_unique<TransitionExitArgsCompartment>("Active");
        TransitionExitArgsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void leave() {
        TransitionExitArgsFrameEvent __e("leave");
        TransitionExitArgsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<void>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_exit_code() {
        TransitionExitArgsFrameEvent __e("get_exit_code");
        TransitionExitArgsFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 18: Transition Exit Args ===" << std::endl;
    TransitionExitArgs s;

    // Initial state is Active
    int code = s.get_exit_code();
    assert(code == 0);

    // Leave - should call exit handler with args
    s.leave();
    code = s.get_exit_code();
    assert(code == 42);
    std::cout << "After transition: exit_code = " << code << std::endl;

    std::cout << "PASS: Transition exit args work correctly" << std::endl;
    return 0;
}
