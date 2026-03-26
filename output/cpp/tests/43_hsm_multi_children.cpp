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

class HSMMultiChildrenFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMMultiChildrenFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMMultiChildrenFrameContext {
public:
    HSMMultiChildrenFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMMultiChildrenFrameContext(HSMMultiChildrenFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMMultiChildrenCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMMultiChildrenFrameEvent> forward_event;
    std::unique_ptr<HSMMultiChildrenCompartment> parent_compartment;

    explicit HSMMultiChildrenCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HSMMultiChildrenCompartment> clone() const {
        auto c = std::make_unique<HSMMultiChildrenCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HSMMultiChildren {
private:
    std::vector<std::unique_ptr<HSMMultiChildrenCompartment>> _state_stack;
    std::unique_ptr<HSMMultiChildrenCompartment> __compartment;
    std::unique_ptr<HSMMultiChildrenCompartment> __next_compartment;
    std::vector<HSMMultiChildrenFrameContext> _context_stack;

    void __kernel(HSMMultiChildrenFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMMultiChildrenFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMMultiChildrenFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMMultiChildrenFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMMultiChildrenFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "ChildA") {
            _state_ChildA(__e);
        } else if (state_name == "ChildB") {
            _state_ChildB(__e);
        } else if (state_name == "ChildC") {
            _state_ChildC(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMMultiChildrenCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_ChildB(HSMMultiChildrenFrameEvent& __e) {
        if (__e._message == "do_action") {
            event_log.push_back("ChildB:do_action");
        } else if (__e._message == "forward_action") {
            event_log.push_back("ChildB:forward_action");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("ChildB"));
            return;;
        } else if (__e._message == "start_a") {
            auto __new_compartment = std::make_unique<HSMMultiChildrenCompartment>("ChildA");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "start_b") {
            // stay
        } else if (__e._message == "start_c") {
            auto __new_compartment = std::make_unique<HSMMultiChildrenCompartment>("ChildC");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Parent(HSMMultiChildrenFrameEvent& __e) {
        if (__e._message == "forward_action") {
            event_log.push_back("Parent:forward_action");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Parent"));
            return;;
        }
    }

    void _state_ChildA(HSMMultiChildrenFrameEvent& __e) {
        if (__e._message == "do_action") {
            event_log.push_back("ChildA:do_action");
        } else if (__e._message == "forward_action") {
            event_log.push_back("ChildA:forward_action");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("ChildA"));
            return;;
        } else if (__e._message == "start_a") {
            // stay
        } else if (__e._message == "start_b") {
            auto __new_compartment = std::make_unique<HSMMultiChildrenCompartment>("ChildB");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "start_c") {
            auto __new_compartment = std::make_unique<HSMMultiChildrenCompartment>("ChildC");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_ChildC(HSMMultiChildrenFrameEvent& __e) {
        if (__e._message == "do_action") {
            event_log.push_back("ChildC:do_action");
        } else if (__e._message == "forward_action") {
            event_log.push_back("ChildC:forward_action");
            _state_Parent(__e);
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("ChildC"));
            return;;
        } else if (__e._message == "start_a") {
            auto __new_compartment = std::make_unique<HSMMultiChildrenCompartment>("ChildA");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "start_b") {
            auto __new_compartment = std::make_unique<HSMMultiChildrenCompartment>("ChildB");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "start_c") {
            // stay
        }
    }

public:
    std::vector<std::string> event_log = {};

    HSMMultiChildren() {
        // HSM: Create parent compartment chain
        auto __parent_comp_0 = std::make_unique<HSMMultiChildrenCompartment>("Parent");
        __compartment = std::make_unique<HSMMultiChildrenCompartment>("ChildA");
        __compartment->parent_compartment = std::move(__parent_comp_0);
        HSMMultiChildrenFrameEvent __frame_event("$>");
        HSMMultiChildrenFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void start_a() {
        HSMMultiChildrenFrameEvent __e("start_a");
        HSMMultiChildrenFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void start_b() {
        HSMMultiChildrenFrameEvent __e("start_b");
        HSMMultiChildrenFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void start_c() {
        HSMMultiChildrenFrameEvent __e("start_c");
        HSMMultiChildrenFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void do_action() {
        HSMMultiChildrenFrameEvent __e("do_action");
        HSMMultiChildrenFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void forward_action() {
        HSMMultiChildrenFrameEvent __e("forward_action");
        HSMMultiChildrenFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::vector<std::string> get_log() {
        HSMMultiChildrenFrameEvent __e("get_log");
        HSMMultiChildrenFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMMultiChildrenFrameEvent __e("get_state");
        HSMMultiChildrenFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 43: HSM Multiple Children ===\n");
    HSMMultiChildren s;

    printf("TC1.3.1: Multiple children with same parent compiles - PASS\n");

    if (s.get_state() != "ChildA") {
        printf("FAIL: Expected ChildA, got %s\n", s.get_state().c_str());
        assert(false);
    }

    s.forward_action();
    auto log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildA:forward_action") == log.end()) {
        printf("FAIL: Expected ChildA forward\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "Parent:forward_action") == log.end()) {
        printf("FAIL: Expected Parent handler\n");
        assert(false);
    }
    printf("TC1.3.2: ChildA forwards to parent - PASS\n");

    s.start_b();
    if (s.get_state() != "ChildB") {
        printf("FAIL: Expected ChildB\n");
        assert(false);
    }
    printf("TC1.3.3: Transition A->B works - PASS\n");

    s.forward_action();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildB:forward_action") == log.end()) {
        printf("FAIL: Expected ChildB forward\n");
        assert(false);
    }
    int parentCount = std::count(log.begin(), log.end(), "Parent:forward_action");
    if (parentCount != 2) {
        printf("FAIL: Expected 2 Parent forwards\n");
        assert(false);
    }
    printf("TC1.3.4: ChildB forwards to same parent - PASS\n");

    s.start_c();
    if (s.get_state() != "ChildC") {
        printf("FAIL: Expected ChildC\n");
        assert(false);
    }
    s.forward_action();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildC:forward_action") == log.end()) {
        printf("FAIL: Expected ChildC forward\n");
        assert(false);
    }
    int parentCount2 = std::count(log.begin(), log.end(), "Parent:forward_action");
    if (parentCount2 != 3) {
        printf("FAIL: Expected 3 Parent forwards\n");
        assert(false);
    }
    printf("TC1.3.5: ChildC forwards to same parent - PASS\n");

    s.start_a();
    s.do_action();
    s.start_b();
    s.do_action();
    s.start_c();
    s.do_action();
    log = s.get_log();
    if (std::find(log.begin(), log.end(), "ChildA:do_action") == log.end()) {
        printf("FAIL: Expected ChildA action\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "ChildB:do_action") == log.end()) {
        printf("FAIL: Expected ChildB action\n");
        assert(false);
    }
    if (std::find(log.begin(), log.end(), "ChildC:do_action") == log.end()) {
        printf("FAIL: Expected ChildC action\n");
        assert(false);
    }
    printf("TC1.3.6: Each sibling has independent handlers - PASS\n");

    printf("PASS: HSM multiple children work correctly\n");
    return 0;
}
