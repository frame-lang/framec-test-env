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

class TransitionEnterArgsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    TransitionEnterArgsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class TransitionEnterArgsFrameContext {
public:
    TransitionEnterArgsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    TransitionEnterArgsFrameContext(TransitionEnterArgsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class TransitionEnterArgsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<TransitionEnterArgsFrameEvent> forward_event;
    std::unique_ptr<TransitionEnterArgsCompartment> parent_compartment;

    explicit TransitionEnterArgsCompartment(const std::string& state) : state(state) {}
};

class TransitionEnterArgs {
private:
    std::unique_ptr<TransitionEnterArgsCompartment> __compartment;
    std::unique_ptr<TransitionEnterArgsCompartment> __next_compartment;
    std::vector<std::unique_ptr<TransitionEnterArgsCompartment>> _state_stack;
    std::vector<TransitionEnterArgsFrameContext> _context_stack;

    log: std::vector<std::string> = {};

    void __kernel(TransitionEnterArgsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            TransitionEnterArgsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                TransitionEnterArgsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    TransitionEnterArgsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(TransitionEnterArgsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    void __transition(std::unique_ptr<TransitionEnterArgsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(TransitionEnterArgsFrameEvent& __e) {
        if (__e._message == "start") {
            {
            log.push_back("idle:start");
            -> ("from_idle", 42) $Active
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

    void _state_Active(TransitionEnterArgsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            log.push_back(std::string("active:enter:") + source + ":" + std::to_string(value));
            }
            return;
        } else if (__e._message == "start") {
            {
            log.push_back("active:start");
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
    TransitionEnterArgs() {
        __compartment = std::make_unique<TransitionEnterArgsCompartment>("Idle");
        log = {};
        TransitionEnterArgsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void start() {
        TransitionEnterArgsFrameEvent __e("start");
        TransitionEnterArgsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        TransitionEnterArgsFrameEvent __e("get_log");
        TransitionEnterArgsFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 17: Transition Enter Args ===\n");
    TransitionEnterArgs s;

    auto log = s.get_log();
    if (log.size() != 0) {
        printf("FAIL: Expected empty log\n");
        assert(false);
    }

    s.start();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "idle:start") == log.end()) {
        printf("FAIL: Expected 'idle:start' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "active:enter:from_idle:42") == log.end()) {
        printf("FAIL: Expected 'active:enter:from_idle:42' in log\n");
        assert(false);
    }
    printf("Log after transition: idle:start, active:enter:from_idle:42\n");

    printf("PASS: Transition enter args work correctly\n");
    return 0;
}
