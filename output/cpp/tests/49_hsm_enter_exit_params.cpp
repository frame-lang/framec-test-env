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

class HSMEnterExitParamsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMEnterExitParamsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMEnterExitParamsFrameContext {
public:
    HSMEnterExitParamsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMEnterExitParamsFrameContext(HSMEnterExitParamsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMEnterExitParamsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMEnterExitParamsFrameEvent> forward_event;
    std::unique_ptr<HSMEnterExitParamsCompartment> parent_compartment;

    explicit HSMEnterExitParamsCompartment(const std::string& state) : state(state) {}
};

class HSMEnterExitParams {
private:
    std::unique_ptr<HSMEnterExitParamsCompartment> __compartment;
    std::unique_ptr<HSMEnterExitParamsCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMEnterExitParamsCompartment>> _state_stack;
    std::vector<HSMEnterExitParamsFrameContext> _context_stack;

    std::vector<std::string> event_log = {};

    void __kernel(HSMEnterExitParamsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMEnterExitParamsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMEnterExitParamsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMEnterExitParamsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMEnterExitParamsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "ChildA") {
            _state_ChildA(__e);
        } else if (state_name == "ChildB") {
            _state_ChildB(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMEnterExitParamsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(HSMEnterExitParamsFrameEvent& __e) {
        if (__e._message == "go_to_a") {
            {
            -> ("starting") $ChildA
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Start");
            return;
            }
            return;
        }
    }

    void _state_ChildA(HSMEnterExitParamsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back(std::string("ChildA:enter(") + msg + ")");
            }
            return;
        } else if (__e._message == "<$") {
            {
            event_log.push_back(std::string("ChildA:exit(") + reason + ")");
            }
            return;
        } else if (__e._message == "go_to_sibling") {
            {
            ("leaving_A") -> ("arriving_B") $ChildB
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("ChildA");
            return;
            }
            return;
        }
    }

    void _state_ChildB(HSMEnterExitParamsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back(std::string("ChildB:enter(") + msg + ")");
            }
            return;
        } else if (__e._message == "<$") {
            {
            event_log.push_back(std::string("ChildB:exit(") + reason + ")");
            }
            return;
        } else if (__e._message == "go_back") {
            {
            ("leaving_B") -> ("returning_A") $ChildA
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("ChildB");
            return;
            }
            return;
        }
    }

    void _state_Parent(HSMEnterExitParamsFrameEvent& __e) {
        if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Parent");
            return;
            }
            return;
        }
    }

public:
    HSMEnterExitParams() {
        __compartment = std::make_unique<HSMEnterExitParamsCompartment>("Start");
        event_log = {};
        HSMEnterExitParamsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void go_to_a() {
        HSMEnterExitParamsFrameEvent __e("go_to_a");
        HSMEnterExitParamsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_sibling() {
        HSMEnterExitParamsFrameEvent __e("go_to_sibling");
        HSMEnterExitParamsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_back() {
        HSMEnterExitParamsFrameEvent __e("go_back");
        HSMEnterExitParamsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMEnterExitParamsFrameEvent __e("get_log");
        HSMEnterExitParamsFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMEnterExitParamsFrameEvent __e("get_state");
        HSMEnterExitParamsFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 49: HSM Enter/Exit with Params ===\n");
    HSMEnterExitParams s;

    s.go_to_a();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildA:enter(starting)") == log.end()) {
        printf("FAIL: Expected ChildA:enter(starting)\n");
        assert(false);
    }
    printf("TC2.5.0: Initial transition with enter params - PASS\n");

    s.go_to_sibling();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildA:exit(leaving_A)") == log.end()) {
        printf("FAIL: Expected exit with param\n");
        assert(false);
    }
    printf("TC2.5.1: Exit params passed correctly - PASS\n");

    if (std::find(log.begin(), log.end(), "ChildB:enter(arriving_B)") == log.end()) {
        printf("FAIL: Expected enter with param\n");
        assert(false);
    }
    if (s.get_state() != "ChildB") {
        printf("FAIL: Expected ChildB\n");
        assert(false);
    }
    printf("TC2.5.2: Enter params passed to target - PASS\n");

    s.go_back();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildB:exit(leaving_B)") == log.end()) {
        printf("FAIL: Expected ChildB exit\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "ChildA:enter(returning_A)") == log.end()) {
        printf("FAIL: Expected ChildA enter\n");
        assert(false);
    }
    printf("TC2.5.3: Return transition with params - PASS\n");

    printf("PASS: HSM enter/exit with params works correctly\n");
    return 0;
}
