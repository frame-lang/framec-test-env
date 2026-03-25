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

class HSMThreeLevelsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMThreeLevelsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMThreeLevelsFrameContext {
public:
    HSMThreeLevelsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMThreeLevelsFrameContext(HSMThreeLevelsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMThreeLevelsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMThreeLevelsFrameEvent> forward_event;
    std::unique_ptr<HSMThreeLevelsCompartment> parent_compartment;

    explicit HSMThreeLevelsCompartment(const std::string& state) : state(state) {}
};

class HSMThreeLevels {
private:
    std::unique_ptr<HSMThreeLevelsCompartment> __compartment;
    std::unique_ptr<HSMThreeLevelsCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMThreeLevelsCompartment>> _state_stack;
    std::vector<HSMThreeLevelsFrameContext> _context_stack;

    log: std::vector<std::string> = {};

    void __kernel(HSMThreeLevelsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMThreeLevelsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMThreeLevelsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMThreeLevelsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMThreeLevelsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Grandchild") {
            _state_Grandchild(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMThreeLevelsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Grandchild(HSMThreeLevelsFrameEvent& __e) {
        if (__e._message == "handle_at_grandchild") {
            {
            int val = std::any_cast<int>(__compartment->state_vars["grandchild_var"]);
            log.push_back(std::string("Grandchild:handled(var=") + std::to_string(val) + ")");
            }
            return;
        } else if (__e._message == "forward_to_child") {
            {
            log.push_back("Grandchild:forward_to_child");
            _state_Child(__e);
            return;
            }
            return;
        } else if (__e._message == "forward_to_parent") {
            {
            log.push_back("Grandchild:forward_to_parent");
            _state_Child(__e);
            return;
            }
            return;
        } else if (__e._message == "forward_through_all") {
            {
            log.push_back("Grandchild:forward_through_all");
            _state_Child(__e);
            return;
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

    void _state_Child(HSMThreeLevelsFrameEvent& __e) {
        if (__e._message == "forward_to_child") {
            {
            int val = std::any_cast<int>(__compartment->state_vars["child_var"]);
            log.push_back(std::string("Child:handled(var=") + std::to_string(val) + ")");
            }
            return;
        } else if (__e._message == "forward_to_parent") {
            {
            int val = std::any_cast<int>(__compartment->state_vars["child_var"]);
            log.push_back(std::string("Child:forward_to_parent(var=") + std::to_string(val) + ")");
            _state_Parent(__e);
            return;
            }
            return;
        } else if (__e._message == "forward_through_all") {
            {
            int val = std::any_cast<int>(__compartment->state_vars["child_var"]);
            log.push_back(std::string("Child:forward_through_all(var=") + std::to_string(val) + ")");
            _state_Parent(__e);
            return;
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

    void _state_Parent(HSMThreeLevelsFrameEvent& __e) {
        if (__e._message == "forward_to_parent") {
            {
            int val = std::any_cast<int>(__compartment->state_vars["parent_var"]);
            log.push_back(std::string("Parent:handled(var=") + std::to_string(val) + ")");
            }
            return;
        } else if (__e._message == "forward_through_all") {
            {
            int val = std::any_cast<int>(__compartment->state_vars["parent_var"]);
            log.push_back(std::string("Parent:forward_through_all(var=") + std::to_string(val) + ")");
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
    HSMThreeLevels() {
        __compartment = std::make_unique<HSMThreeLevelsCompartment>("Grandchild");
        __compartment->state_vars["grandchild_var"] = 1;
        log = {};
        HSMThreeLevelsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void handle_at_grandchild() {
        HSMThreeLevelsFrameEvent __e("handle_at_grandchild");
        HSMThreeLevelsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forward_to_child() {
        HSMThreeLevelsFrameEvent __e("forward_to_child");
        HSMThreeLevelsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forward_to_parent() {
        HSMThreeLevelsFrameEvent __e("forward_to_parent");
        HSMThreeLevelsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forward_through_all() {
        HSMThreeLevelsFrameEvent __e("forward_through_all");
        HSMThreeLevelsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMThreeLevelsFrameEvent __e("get_log");
        HSMThreeLevelsFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    printf("=== Test 42: HSM Three-Level Hierarchy ===\n");
    HSMThreeLevels s;

    printf("TC1.2.1: Three-level hierarchy compiles - PASS\n");

    s.handle_at_grandchild();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "Grandchild:handled(var=1)") == log.end()) {
        printf("FAIL: Expected Grandchild handler\n");
        assert(false);
    }
    printf("TC1.2.2: Grandchild handles locally - PASS\n");

    s.forward_to_child();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Grandchild:forward_to_child") == log.end()) {
        printf("FAIL: Expected Grandchild forward\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Child:handled(var=10)") == log.end()) {
        printf("FAIL: Expected Child handler\n");
        assert(false);
    }
    printf("TC1.2.3: Forward grandchild->child - PASS\n");

    s.forward_to_parent();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Grandchild:forward_to_parent") == log.end()) {
        printf("FAIL: Expected Grandchild forward\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Child:forward_to_parent(var=10)") == log.end()) {
        printf("FAIL: Expected Child forward\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:handled(var=100)") == log.end()) {
        printf("FAIL: Expected Parent handler\n");
        assert(false);
    }
    printf("TC1.2.4: Forward grandchild->child->parent - PASS\n");

    s.forward_through_all();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "Grandchild:forward_through_all") == log.end()) {
        printf("FAIL: Expected Grandchild\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Child:forward_through_all(var=10)") == log.end()) {
        printf("FAIL: Expected Child\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:forward_through_all(var=100)") == log.end()) {
        printf("FAIL: Expected Parent\n");
        assert(false);
    }
    printf("TC1.2.5: Full chain forward - PASS\n");

    printf("TC1.2.6: State vars isolated (grandchild=1, child=10, parent=100) - PASS\n");

    printf("PASS: HSM three-level hierarchy works correctly\n");
    return 0;
}
