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

class HSMSiblingTransitionsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMSiblingTransitionsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMSiblingTransitionsFrameContext {
public:
    HSMSiblingTransitionsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMSiblingTransitionsFrameContext(HSMSiblingTransitionsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMSiblingTransitionsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMSiblingTransitionsFrameEvent> forward_event;
    std::unique_ptr<HSMSiblingTransitionsCompartment> parent_compartment;

    explicit HSMSiblingTransitionsCompartment(const std::string& state) : state(state) {}
};

class HSMSiblingTransitions {
private:
    std::unique_ptr<HSMSiblingTransitionsCompartment> __compartment;
    std::unique_ptr<HSMSiblingTransitionsCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMSiblingTransitionsCompartment>> _state_stack;
    std::vector<HSMSiblingTransitionsFrameContext> _context_stack;

    std::vector<std::string> event_log = {};

    void __kernel(HSMSiblingTransitionsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMSiblingTransitionsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMSiblingTransitionsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMSiblingTransitionsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMSiblingTransitionsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "ChildA") {
            _state_ChildA(__e);
        } else if (state_name == "ChildB") {
            _state_ChildB(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMSiblingTransitionsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_ChildA(HSMSiblingTransitionsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back("ChildA:enter");
            }
            return;
        } else if (__e._message == "<$") {
            {
            event_log.push_back("ChildA:exit");
            }
            return;
        } else if (__e._message == "go_to_b") {
            {
            event_log.push_back("ChildA:go_to_b");
            auto __comp = std::make_unique<HSMSiblingTransitionsCompartment>("ChildB");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "forward_action") {
            {
            event_log.push_back("ChildA:forward");
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
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("ChildA");
            return;
            }
            return;
        }
    }

    void _state_ChildB(HSMSiblingTransitionsFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            event_log.push_back("ChildB:enter");
            }
            return;
        } else if (__e._message == "<$") {
            {
            event_log.push_back("ChildB:exit");
            }
            return;
        } else if (__e._message == "go_to_a") {
            {
            event_log.push_back("ChildB:go_to_a");
            auto __comp = std::make_unique<HSMSiblingTransitionsCompartment>("ChildA");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "forward_action") {
            {
            event_log.push_back("ChildB:forward");
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
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("ChildB");
            return;
            }
            return;
        }
    }

    void _state_Parent(HSMSiblingTransitionsFrameEvent& __e) {
        if (__e._message == "forward_action") {
            {
            event_log.push_back("Parent:forward_action");
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
            _context_stack.back()._return = std::string("Parent");
            return;
            }
            return;
        }
    }

public:
    HSMSiblingTransitions() {
        __compartment = std::make_unique<HSMSiblingTransitionsCompartment>("ChildA");
        event_log = {};
        HSMSiblingTransitionsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void go_to_b() {
        HSMSiblingTransitionsFrameEvent __e("go_to_b");
        HSMSiblingTransitionsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_to_a() {
        HSMSiblingTransitionsFrameEvent __e("go_to_a");
        HSMSiblingTransitionsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forward_action() {
        HSMSiblingTransitionsFrameEvent __e("forward_action");
        HSMSiblingTransitionsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMSiblingTransitionsFrameEvent __e("get_log");
        HSMSiblingTransitionsFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMSiblingTransitionsFrameEvent __e("get_state");
        HSMSiblingTransitionsFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 44: HSM Sibling Transitions ===\n");
    HSMSiblingTransitions s;

    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildA:enter") == log.end()) {
        printf("FAIL: Expected ChildA:enter on init\n");
        assert(false);
    }
    if (s.get_state() != "ChildA") {
        printf("FAIL: Expected ChildA\n");
        assert(false);
    }
    printf("TC1.4.0: Initial state ChildA with enter - PASS\n");

    s.go_to_b();
    if (s.get_state() != "ChildB") {
        printf("FAIL: Expected ChildB\n");
        assert(false);
    }
    printf("TC1.4.1: Transition A->B works - PASS\n");

    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildA:exit") == log.end()) {
        printf("FAIL: Expected ChildA:exit\n");
        assert(false);
    }
    printf("TC1.4.2: Exit handler fires on source - PASS\n");

    if (std::find(log.begin(), log.end(), "ChildB:enter") == log.end()) {
        printf("FAIL: Expected ChildB:enter\n");
        assert(false);
    }
    printf("TC1.4.3: Enter handler fires on target - PASS\n");

    s.forward_action();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildB:forward") == log.end()) {
        printf("FAIL: Expected ChildB:forward\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:forward_action") == log.end()) {
        printf("FAIL: Expected Parent handler\n");
        assert(false);
    }
    printf("TC1.4.4: Parent relationship preserved - PASS\n");

    s.go_to_a();
    if (s.get_state() != "ChildA") {
        printf("FAIL: Expected ChildA\n");
        assert(false);
    }
    log = s.get_log();
    int exitBCount = std::count(log.begin(), log.end(), "ChildB:exit");
    int enterACount = std::count(log.begin(), log.end(), "ChildA:enter");
    if (exitBCount != 1) {
        printf("FAIL: Expected ChildB:exit once\n");
        assert(false);
    }
    if (enterACount != 2) {
        printf("FAIL: Expected ChildA:enter twice\n");
        assert(false);
    }
    printf("TC1.4.5: Transition B->A works with enter/exit - PASS\n");

    s.forward_action();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildA:forward") == log.end()) {
        printf("FAIL: Expected ChildA:forward\n");
        assert(false);
    }
    int parentCount = std::count(log.begin(), log.end(), "Parent:forward_action");
    if (parentCount != 2) {
        printf("FAIL: Expected 2 Parent handlers\n");
        assert(false);
    }
    printf("TC1.4.6: ChildA forwards after returning - PASS\n");

    printf("PASS: HSM sibling transitions work correctly\n");
    return 0;
}
