#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Tests that @@:return follows "last writer wins" across transition lifecycle

class SystemReturnChainTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SystemReturnChainTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SystemReturnChainTestFrameContext {
public:
    SystemReturnChainTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SystemReturnChainTestFrameContext(SystemReturnChainTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SystemReturnChainTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SystemReturnChainTestFrameEvent> forward_event;
    std::unique_ptr<SystemReturnChainTestCompartment> parent_compartment;

    explicit SystemReturnChainTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<SystemReturnChainTestCompartment> clone() const {
        auto c = std::make_unique<SystemReturnChainTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class SystemReturnChainTest {
private:
    std::vector<std::unique_ptr<SystemReturnChainTestCompartment>> _state_stack;
    std::unique_ptr<SystemReturnChainTestCompartment> __compartment;
    std::unique_ptr<SystemReturnChainTestCompartment> __next_compartment;
    std::vector<SystemReturnChainTestFrameContext> _context_stack;

    void __kernel(SystemReturnChainTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SystemReturnChainTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SystemReturnChainTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SystemReturnChainTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SystemReturnChainTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "EnterSetter") {
            _state_EnterSetter(__e);
        } else if (state_name == "BothSet") {
            _state_BothSet(__e);
        }
    }

    void __transition(std::unique_ptr<SystemReturnChainTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(SystemReturnChainTestFrameEvent& __e) {
        if (__e._message == "<$") {
            _context_stack.back()._return = std::any(std::string("from_exit"));
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Start"));
            return;;
        } else if (__e._message == "test_enter_sets") {
            auto __new_compartment = std::make_unique<SystemReturnChainTestCompartment>("EnterSetter");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "test_exit_then_enter") {
            auto __new_compartment = std::make_unique<SystemReturnChainTestCompartment>("BothSet");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_EnterSetter(SystemReturnChainTestFrameEvent& __e) {
        if (__e._message == "$>") {
            _context_stack.back()._return = std::any(std::string("from_enter"));
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("EnterSetter"));
            return;;
        }
    }

    void _state_BothSet(SystemReturnChainTestFrameEvent& __e) {
        if (__e._message == "$>") {
            _context_stack.back()._return = std::any(std::string("enter_wins"));
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("BothSet"));
            return;;
        }
    }

public:
    SystemReturnChainTest() {
        __compartment = std::make_unique<SystemReturnChainTestCompartment>("Start");
        SystemReturnChainTestFrameEvent __frame_event("$>");
        SystemReturnChainTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string test_enter_sets() {
        SystemReturnChainTestFrameEvent __e("test_enter_sets");
        SystemReturnChainTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string test_exit_then_enter() {
        SystemReturnChainTestFrameEvent __e("test_exit_then_enter");
        SystemReturnChainTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        SystemReturnChainTestFrameEvent __e("get_state");
        SystemReturnChainTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 15: System Return Chain (Last Writer Wins) ===\n");

    SystemReturnChainTest s1;
    std::string result1 = s1.test_enter_sets();
    if (result1 != "from_enter") {
        printf("FAIL: Expected 'from_enter', got '%s'\n", result1.c_str());
        assert(false);
    }
    if (s1.get_state() != "EnterSetter") {
        printf("FAIL: Expected state 'EnterSetter'\n");
        assert(false);
    }
    printf("1. Exit set then enter set - enter wins: '%s'\n", result1.c_str());

    SystemReturnChainTest s2;
    std::string result2 = s2.test_exit_then_enter();
    if (result2 != "enter_wins") {
        printf("FAIL: Expected 'enter_wins', got '%s'\n", result2.c_str());
        assert(false);
    }
    if (s2.get_state() != "BothSet") {
        printf("FAIL: Expected state 'BothSet'\n");
        assert(false);
    }
    printf("2. Both set - enter wins: '%s'\n", result2.c_str());

    printf("PASS: System return chain (last writer wins) works correctly\n");
    return 0;
}
