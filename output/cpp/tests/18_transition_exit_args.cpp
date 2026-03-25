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

    std::vector<std::string> event_log = {};

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
            event_log.push_back(std::string("exit:") + reason + ":" + std::to_string(code));
            }
            return;
        } else if (__e._message == "leave") {
            {
            event_log.push_back("leaving");
            ("cleanup", 42) -> $Done
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

    void _state_Done(TransitionExitArgsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back("enter:done");
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
    TransitionExitArgs() {
        __compartment = std::make_unique<TransitionExitArgsCompartment>("Active");
        event_log = {};
        TransitionExitArgsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void leave() {
        TransitionExitArgsFrameEvent __e("leave");
        TransitionExitArgsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        TransitionExitArgsFrameEvent __e("get_log");
        TransitionExitArgsFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 18: Transition Exit Args ===\n");
    TransitionExitArgs s;

    auto log = s.get_log();
    if (log.size() != 0) {
        printf("FAIL: Expected empty log\n");
        assert(false);
    }

    s.leave();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "leaving") == log.end()) {
        printf("FAIL: Expected 'leaving' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "exit:cleanup:42") == log.end()) {
        printf("FAIL: Expected 'exit:cleanup:42' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "enter:done") == log.end()) {
        printf("FAIL: Expected 'enter:done' in log\n");
        assert(false);
    }
    printf("Log after transition: leaving, exit:cleanup:42, enter:done\n");

    printf("PASS: Transition exit args work correctly\n");
    return 0;
}
