#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
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
};

class SystemReturnChainTest {
private:
    std::unique_ptr<SystemReturnChainTestCompartment> __compartment;
    std::unique_ptr<SystemReturnChainTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<SystemReturnChainTestCompartment>> _state_stack;
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
            {
            // Exit handler sets initial value (10)
            _context_stack.back()._return = 10;
            }
            return;
        } else if (__e._message == "test_enter_sets") {
            {
            auto __comp = std::make_unique<SystemReturnChainTestCompartment>("EnterSetter");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "test_exit_then_enter") {
            {
            auto __comp = std::make_unique<SystemReturnChainTestCompartment>("BothSet");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = 1;
            return;
            }
            return;
        }
    }

    void _state_EnterSetter(SystemReturnChainTestFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            // Enter handler sets return value (20)
            _context_stack.back()._return = 20;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = 2;
            return;
            }
            return;
        }
    }

    void _state_BothSet(SystemReturnChainTestFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            // Enter handler sets return - should overwrite exit's value (30)
            _context_stack.back()._return = 30;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = 3;
            return;
            }
            return;
        }
    }

public:
    SystemReturnChainTest() {
        __compartment = std::make_unique<SystemReturnChainTestCompartment>("Start");
        SystemReturnChainTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int test_enter_sets() {
        SystemReturnChainTestFrameEvent __e("test_enter_sets");
        SystemReturnChainTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int test_exit_then_enter() {
        SystemReturnChainTestFrameEvent __e("test_exit_then_enter");
        SystemReturnChainTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_state() {
        SystemReturnChainTestFrameEvent __e("get_state");
        SystemReturnChainTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 15: System Return Chain (Last Writer Wins) ===" << std::endl;

    // Test 1: Start exit + EnterSetter enter
    // Start's exit sets 10, EnterSetter's enter sets 20
    // Enter should win (last writer)
    SystemReturnChainTest s1;
    int result = s1.test_enter_sets();
    assert(result == 20);
    int state = s1.get_state();
    assert(state == 2);
    std::cout << "1. Exit set then enter set - enter wins: " << result << std::endl;

    // Test 2: Both handlers set, enter wins
    SystemReturnChainTest s2;
    result = s2.test_exit_then_enter();
    assert(result == 30);
    state = s2.get_state();
    assert(state == 3);
    std::cout << "2. Both set - enter wins: " << result << std::endl;

    std::cout << "PASS: System return chain (last writer wins) works correctly" << std::endl;
    return 0;
}
