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

class EnterExitFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    EnterExitFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class EnterExitFrameContext {
public:
    EnterExitFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    EnterExitFrameContext(EnterExitFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class EnterExitCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<EnterExitFrameEvent> forward_event;
    std::unique_ptr<EnterExitCompartment> parent_compartment;

    explicit EnterExitCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<EnterExitCompartment> clone() const {
        auto c = std::make_unique<EnterExitCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class EnterExit {
private:
    std::vector<std::unique_ptr<EnterExitCompartment>> _state_stack;
    std::unique_ptr<EnterExitCompartment> __compartment;
    std::unique_ptr<EnterExitCompartment> __next_compartment;
    std::vector<EnterExitFrameContext> _context_stack;

    void __kernel(EnterExitFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            EnterExitFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                EnterExitFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    EnterExitFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(EnterExitFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Off") {
            _state_Off(__e);
        } else if (state_name == "On") {
            _state_On(__e);
        }
    }

    void __transition(std::unique_ptr<EnterExitCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Off(EnterExitFrameEvent& __e) {
        if (__e._message == "<$") {
            event_log.push_back("exit:Off");
            printf("Exiting Off state\n");
        } else if (__e._message == "$>") {
            event_log.push_back("enter:Off");
            printf("Entered Off state\n");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "toggle") {
            auto __new_compartment = std::make_unique<EnterExitCompartment>("On");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_On(EnterExitFrameEvent& __e) {
        if (__e._message == "<$") {
            event_log.push_back("exit:On");
            printf("Exiting On state\n");
        } else if (__e._message == "$>") {
            event_log.push_back("enter:On");
            printf("Entered On state\n");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "toggle") {
            auto __new_compartment = std::make_unique<EnterExitCompartment>("Off");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    std::vector<std::string> event_log = {};

    EnterExit() {
        __compartment = std::make_unique<EnterExitCompartment>("Off");
        EnterExitFrameEvent __frame_event("$>");
        EnterExitFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void toggle() {
        EnterExitFrameEvent __e("toggle");
        EnterExitFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        EnterExitFrameEvent __e("get_log");
        EnterExitFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 05: Enter/Exit Handlers ===\n");
    EnterExit s;

    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "enter:Off") == log.end()) {
        printf("FAIL: Expected 'enter:Off' in log\n");
        assert(false);
    }
    printf("After construction: enter:Off found\n");

    s.toggle();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "exit:Off") == log.end()) {
        printf("FAIL: Expected 'exit:Off' in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "enter:On") == log.end()) {
        printf("FAIL: Expected 'enter:On' in log\n");
        assert(false);
    }
    printf("After toggle to On: exit:Off and enter:On found\n");

    s.toggle();
    log = s.get_log();
    int enterOffCount = std::count(log.begin(), log.end(), "enter:Off");
    if (enterOffCount != 2) {
        printf("FAIL: Expected 2 'enter:Off' entries, got %d\n", enterOffCount);
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "exit:On") == log.end()) {
        printf("FAIL: Expected 'exit:On' in log\n");
        assert(false);
    }
    printf("After toggle to Off: correct enter/exit sequence\n");

    printf("PASS: Enter/Exit handlers work correctly\n");
    return 0;
}
