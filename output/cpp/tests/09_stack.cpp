#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class StackOpsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    StackOpsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class StackOpsFrameContext {
public:
    StackOpsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    StackOpsFrameContext(StackOpsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class StackOpsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<StackOpsFrameEvent> forward_event;
    std::unique_ptr<StackOpsCompartment> parent_compartment;

    explicit StackOpsCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<StackOpsCompartment> clone() const {
        auto c = std::make_unique<StackOpsCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class StackOps {
private:
    std::vector<std::unique_ptr<StackOpsCompartment>> _state_stack;
    std::unique_ptr<StackOpsCompartment> __compartment;
    std::unique_ptr<StackOpsCompartment> __next_compartment;
    std::vector<StackOpsFrameContext> _context_stack;

    void __kernel(StackOpsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            StackOpsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                StackOpsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    StackOpsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(StackOpsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Main") {
            _state_Main(__e);
        } else if (state_name == "Sub") {
            _state_Sub(__e);
        }
    }

    void __transition(std::unique_ptr<StackOpsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Sub(StackOpsFrameEvent& __e) {
        if (__e._message == "do_work") {
            _context_stack.back()._return = std::any(std::string("Working in Sub"));
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Sub"));
            return;;
        } else if (__e._message == "pop_back") {
            printf("Popping back to previous state\n");
            auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
        } else if (__e._message == "push_and_go") {
            printf("Already in Sub\n");
        }
    }

    void _state_Main(StackOpsFrameEvent& __e) {
        if (__e._message == "do_work") {
            _context_stack.back()._return = std::any(std::string("Working in Main"));
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Main"));
            return;;
        } else if (__e._message == "pop_back") {
            printf("Cannot pop - nothing on stack in Main\n");
        } else if (__e._message == "push_and_go") {
            printf("Pushing Main to stack, going to Sub\n");
            _state_stack.push_back(__compartment->clone());
            auto __new_compartment = std::make_unique<StackOpsCompartment>("Sub");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    StackOps() {
        __compartment = std::make_unique<StackOpsCompartment>("Main");
        StackOpsFrameEvent __frame_event("$>");
        StackOpsFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void push_and_go() {
        StackOpsFrameEvent __e("push_and_go");
        StackOpsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void pop_back() {
        StackOpsFrameEvent __e("pop_back");
        StackOpsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string do_work() {
        StackOpsFrameEvent __e("do_work");
        StackOpsFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        StackOpsFrameEvent __e("get_state");
        StackOpsFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 09: Stack Push/Pop ===\n");
    StackOps s;

    std::string state = s.get_state();
    if (state != "Main") {
        printf("FAIL: Expected 'Main', got '%s'\n", state.c_str());
        assert(false);
    }
    printf("Initial state: %s\n", state.c_str());

    std::string work = s.do_work();
    if (work != "Working in Main") {
        printf("FAIL: Expected 'Working in Main', got '%s'\n", work.c_str());
        assert(false);
    }
    printf("do_work(): %s\n", work.c_str());

    s.push_and_go();
    state = s.get_state();
    if (state != "Sub") {
        printf("FAIL: Expected 'Sub', got '%s'\n", state.c_str());
        assert(false);
    }
    printf("After push_and_go(): %s\n", state.c_str());

    work = s.do_work();
    if (work != "Working in Sub") {
        printf("FAIL: Expected 'Working in Sub', got '%s'\n", work.c_str());
        assert(false);
    }
    printf("do_work(): %s\n", work.c_str());

    s.pop_back();
    state = s.get_state();
    if (state != "Main") {
        printf("FAIL: Expected 'Main' after pop, got '%s'\n", state.c_str());
        assert(false);
    }
    printf("After pop_back(): %s\n", state.c_str());

    printf("PASS: Stack push/pop works correctly\n");
    return 0;
}
