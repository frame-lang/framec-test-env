#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class TransitionTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    TransitionTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class TransitionTestFrameContext {
public:
    TransitionTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    TransitionTestFrameContext(TransitionTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class TransitionTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<TransitionTestFrameEvent> forward_event;
    std::unique_ptr<TransitionTestCompartment> parent_compartment;

    explicit TransitionTestCompartment(const std::string& state) : state(state) {}
};

class TransitionTest {
private:
    std::unique_ptr<TransitionTestCompartment> __compartment;
    std::unique_ptr<TransitionTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<TransitionTestCompartment>> _state_stack;
    std::vector<TransitionTestFrameContext> _context_stack;

    void __kernel(TransitionTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            TransitionTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                TransitionTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    TransitionTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(TransitionTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        } else if (state_name == "C") {
            _state_C(__e);
        }
    }

    void __transition(std::unique_ptr<TransitionTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_A(TransitionTestFrameEvent& __e) {
        if (__e._message == "next") {
            {
            auto __compartment = std::make_unique<TransitionTestCompartment>("B");
            __transition(std::move(__compartment));
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("A");
            return;
            }
            return;
        }
    }

    void _state_B(TransitionTestFrameEvent& __e) {
        if (__e._message == "next") {
            {
            auto __compartment = std::make_unique<TransitionTestCompartment>("C");
            __transition(std::move(__compartment));
            return;
            }
            return;
        } else if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("B");
            return;
            }
            return;
        }
    }

    void _state_C(TransitionTestFrameEvent& __e) {
        if (__e._message == "get_state") {
            {
            _context_stack.back()._return = std::string("C");
            return;
            }
            return;
        }
    }

public:
    TransitionTest() {
        __compartment = std::make_unique<TransitionTestCompartment>("A");
        TransitionTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void next() {
        TransitionTestFrameEvent __e("next");
        TransitionTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        TransitionTestFrameEvent __e("get_state");
        TransitionTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    TransitionTest s;
    assert(s.get_state() == "A");
    s.next();
    assert(s.get_state() == "B");
    s.next();
    assert(s.get_state() == "C");
    std::cout << "PASS: 03 transition" << std::endl;
    return 0;
}
