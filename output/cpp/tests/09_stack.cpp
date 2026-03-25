#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


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
};

class StackOps {
private:
    std::unique_ptr<StackOpsCompartment> __compartment;
    std::unique_ptr<StackOpsCompartment> __next_compartment;
    std::vector<std::unique_ptr<StackOpsCompartment>> _state_stack;
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

    void _state_Main(StackOpsFrameEvent& __e) {
        if (__e._message == "push_and_go") {
            {
            std::cout << "Pushing Main to stack, going to Sub" << std::endl;
            _state_stack.push_back(std::make_unique<StackOpsCompartment>(__compartment->state));
            _state_stack.back()->state_vars = __compartment->state_vars;
            _state_stack.back()->state_args = __compartment->state_args;
            auto __comp = std::make_unique<StackOpsCompartment>("Sub");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "pop_back") {
            {
            std::cout << "Cannot pop - nothing on stack in Main" << std::endl;
            }
            return;
        } else if (__e._message == "do_work") {
            {
            _context_stack.back()._return = std::string("Working in Main");
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Main");
            return;
            }
            return;
        }
    }

    void _state_Sub(StackOpsFrameEvent& __e) {
        if (__e._message == "push_and_go") {
            {
            std::cout << "Already in Sub" << std::endl;
            }
            return;
        } else if (__e._message == "pop_back") {
            {
            std::cout << "Popping back to previous state" << std::endl;
            auto __popped = std::move(_state_stack.back());
            _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
            }
            return;
        } else if (__e._message == "do_work") {
            {
            _context_stack.back()._return = std::string("Working in Sub");
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("Sub");
            return;
            }
            return;
        }
    }

public:
    StackOps() {
        __compartment = std::make_unique<StackOpsCompartment>("Main");
        StackOpsFrameEvent __frame_event("$>");
        __kernel(__frame_event);
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
    std::cout << "=== Test 09: Stack Push/Pop ===" << std::endl;
    StackOps s;

    // Initial state should be Main
    std::string state = s.get_state();
    assert(state == "Main");
    std::cout << "Initial state: " << state << std::endl;

    // Do work in Main
    std::string work = s.do_work();
    assert(work == "Working in Main");
    std::cout << "do_work(): " << work << std::endl;

    // Push and go to Sub
    s.push_and_go();
    state = s.get_state();
    assert(state == "Sub");
    std::cout << "After push_and_go(): " << state << std::endl;

    // Do work in Sub
    work = s.do_work();
    assert(work == "Working in Sub");
    std::cout << "do_work(): " << work << std::endl;

    // Pop back to Main
    s.pop_back();
    state = s.get_state();
    assert(state == "Main");
    std::cout << "After pop_back(): " << state << std::endl;

    std::cout << "PASS: 09 stack" << std::endl;
    return 0;
}
