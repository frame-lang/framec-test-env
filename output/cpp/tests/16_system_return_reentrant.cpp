#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Tests that nested interface calls maintain separate return contexts

class SystemReturnReentrantTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    SystemReturnReentrantTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class SystemReturnReentrantTestFrameContext {
public:
    SystemReturnReentrantTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    SystemReturnReentrantTestFrameContext(SystemReturnReentrantTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class SystemReturnReentrantTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<SystemReturnReentrantTestFrameEvent> forward_event;
    std::unique_ptr<SystemReturnReentrantTestCompartment> parent_compartment;

    explicit SystemReturnReentrantTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<SystemReturnReentrantTestCompartment> clone() const {
        auto c = std::make_unique<SystemReturnReentrantTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class SystemReturnReentrantTest {
private:
    std::vector<std::unique_ptr<SystemReturnReentrantTestCompartment>> _state_stack;
    std::unique_ptr<SystemReturnReentrantTestCompartment> __compartment;
    std::unique_ptr<SystemReturnReentrantTestCompartment> __next_compartment;
    std::vector<SystemReturnReentrantTestFrameContext> _context_stack;

    void __kernel(SystemReturnReentrantTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            SystemReturnReentrantTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                SystemReturnReentrantTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    SystemReturnReentrantTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(SystemReturnReentrantTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<SystemReturnReentrantTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(SystemReturnReentrantTestFrameEvent& __e) {
        auto* __sv_comp = __compartment.get();
        while (__sv_comp && __sv_comp->state != "Start") { __sv_comp = __sv_comp->parent_compartment.get(); }
        if (__e._message == "$>") {
            if (__compartment->state_vars.count("log") == 0) { __compartment->state_vars["log"] = std::any(std::string("")); }
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(std::any_cast<std::string>(__sv_comp->state_vars["log"]));
            return;;
        } else if (__e._message == "inner_call") {
            __sv_comp->state_vars["log"] = std::any(std::any_cast<std::string>(__sv_comp->state_vars["log"]) + "inner,");
            _context_stack.back()._return = std::any(std::string("inner_result"));
            return;;
        } else if (__e._message == "nested_call") {
            __sv_comp->state_vars["log"] = std::any(std::any_cast<std::string>(__sv_comp->state_vars["log"]) + "nested_start,");
            std::string result1 = this->inner_call();
            std::string result2 = this->outer_call();
            __sv_comp->state_vars["log"] = std::any(std::any_cast<std::string>(__sv_comp->state_vars["log"]) + "nested_end,");
            _context_stack.back()._return = std::any(std::string("nested:") + result1 + "+" + result2);
            return;;
        } else if (__e._message == "outer_call") {
            __sv_comp->state_vars["log"] = std::any(std::any_cast<std::string>(__sv_comp->state_vars["log"]) + "outer_start,");
            std::string inner_result = this->inner_call();
            __sv_comp->state_vars["log"] = std::any(std::any_cast<std::string>(__sv_comp->state_vars["log"]) + "outer_after_inner,");
            _context_stack.back()._return = std::any(std::string("outer_result:") + inner_result);
            return;;
        }
    }

public:
    SystemReturnReentrantTest() {
        __compartment = std::make_unique<SystemReturnReentrantTestCompartment>("Start");
        SystemReturnReentrantTestFrameEvent __frame_event("$>");
        SystemReturnReentrantTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string outer_call() {
        SystemReturnReentrantTestFrameEvent __e("outer_call");
        SystemReturnReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string inner_call() {
        SystemReturnReentrantTestFrameEvent __e("inner_call");
        SystemReturnReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string nested_call() {
        SystemReturnReentrantTestFrameEvent __e("nested_call");
        SystemReturnReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_log() {
        SystemReturnReentrantTestFrameEvent __e("get_log");
        SystemReturnReentrantTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 16: System Return Reentrant (Nested Calls) ===\n");

    SystemReturnReentrantTest s1;
    std::string result1 = s1.inner_call();
    if (result1 != "inner_result") {
        printf("FAIL: Expected 'inner_result', got '%s'\n", result1.c_str());
        assert(false);
    }
    printf("1. inner_call() = '%s'\n", result1.c_str());

    SystemReturnReentrantTest s2;
    std::string result2 = s2.outer_call();
    if (result2 != "outer_result:inner_result") {
        printf("FAIL: Expected 'outer_result:inner_result', got '%s'\n", result2.c_str());
        assert(false);
    }
    std::string log2 = s2.get_log();
    if (log2.find("outer_start") == std::string::npos) {
        printf("FAIL: Missing outer_start in log: %s\n", log2.c_str());
        assert(false);
    }
    if (log2.find("inner") == std::string::npos) {
        printf("FAIL: Missing inner in log: %s\n", log2.c_str());
        assert(false);
    }
    if (log2.find("outer_after_inner") == std::string::npos) {
        printf("FAIL: Missing outer_after_inner in log: %s\n", log2.c_str());
        assert(false);
    }
    printf("2. outer_call() = '%s'\n", result2.c_str());
    printf("   Log: '%s'\n", log2.c_str());

    SystemReturnReentrantTest s3;
    std::string result3 = s3.nested_call();
    std::string expected = "nested:inner_result+outer_result:inner_result";
    if (result3 != expected) {
        printf("FAIL: Expected '%s', got '%s'\n", expected.c_str(), result3.c_str());
        assert(false);
    }
    printf("3. nested_call() = '%s'\n", result3.c_str());

    printf("PASS: System return reentrant (nested calls) works correctly\n");
    return 0;
}
