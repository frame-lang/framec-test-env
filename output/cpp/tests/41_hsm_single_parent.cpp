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

class HSMSingleParentFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMSingleParentFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMSingleParentFrameContext {
public:
    HSMSingleParentFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMSingleParentFrameContext(HSMSingleParentFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMSingleParentCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMSingleParentFrameEvent> forward_event;
    std::unique_ptr<HSMSingleParentCompartment> parent_compartment;

    explicit HSMSingleParentCompartment(const std::string& state) : state(state) {}
};

class HSMSingleParent {
private:
    std::unique_ptr<HSMSingleParentCompartment> __compartment;
    std::unique_ptr<HSMSingleParentCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMSingleParentCompartment>> _state_stack;
    std::vector<HSMSingleParentFrameContext> _context_stack;

    log: std::vector<std::string> = {};

    void __kernel(HSMSingleParentFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMSingleParentFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMSingleParentFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMSingleParentFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMSingleParentFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMSingleParentCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Child(HSMSingleParentFrameEvent& __e) {
        if (__e._message == "child_only") {
            {
            log.push_back("Child:child_only");
            }
            return;
        } else if (__e._message == "forward_to_parent") {
            {
            log.push_back("Child:before_forward");
            _state_Parent(__e);
            return;
            log.push_back("Child:after_forward");
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = log;
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Child");
            return;
            }
            return;
        }
    }

    void _state_Parent(HSMSingleParentFrameEvent& __e) {
        if (__e._message == "forward_to_parent") {
            {
            log.push_back("Parent:forward_to_parent");
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = log;
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
    HSMSingleParent() {
        __compartment = std::make_unique<HSMSingleParentCompartment>("Child");
        log = {};
        HSMSingleParentFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void child_only() {
        HSMSingleParentFrameEvent __e("child_only");
        HSMSingleParentFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forward_to_parent() {
        HSMSingleParentFrameEvent __e("forward_to_parent");
        HSMSingleParentFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMSingleParentFrameEvent __e("get_log");
        HSMSingleParentFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMSingleParentFrameEvent __e("get_state");
        HSMSingleParentFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 41: HSM Single Parent ===\n");
    HSMSingleParent s;

    printf("TC1.1.1: Child-Parent relationship compiles - PASS\n");

    s.forward_to_parent();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "Child:before_forward") == log.end()) {
        printf("FAIL: Expected Child:before_forward in log\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:forward_to_parent") == log.end()) {
        printf("FAIL: Expected Parent:forward_to_parent in log\n");
        assert(false);
    }
    printf("TC1.1.2: Child forwards to parent - PASS\n");

    std::string state = s.get_state();
    if (state != "Child") {
        printf("FAIL: Expected state 'Child', got '%s'\n", state.c_str());
        assert(false);
    }
    printf("TC1.1.3: Child remains current state after forward - PASS\n");

    if (std::find(log.begin(), log.end(), "Child:after_forward") == log.end()) {
        printf("FAIL: Expected Child:after_forward in log\n");
        assert(false);
    }
    auto idx_parent = std::find(log.begin(), log.end(), "Parent:forward_to_parent");
    auto idx_after = std::find(log.begin(), log.end(), "Child:after_forward");
    if (idx_after <= idx_parent) {
        printf("FAIL: Expected Child:after_forward after Parent handler\n");
        assert(false);
    }
    printf("TC1.1.4: Parent executes and returns control - PASS\n");

    s.child_only();
    log = s.get_log();
    int count = std::count(log.begin(), log.end(), "Child:child_only");
    if (count != 1) {
        printf("FAIL: Expected exactly 1 Child:child_only\n");
        assert(false);
    }
    printf("TC1.1.5: Child-only event handled locally - PASS\n");

    printf("PASS: HSM single parent relationship works correctly\n");
    return 0;
}
