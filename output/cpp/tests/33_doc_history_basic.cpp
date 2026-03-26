#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

// Documentation Example: History with push$/pop$ (History201)

class HistoryBasicFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HistoryBasicFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HistoryBasicFrameContext {
public:
    HistoryBasicFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HistoryBasicFrameContext(HistoryBasicFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HistoryBasicCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HistoryBasicFrameEvent> forward_event;
    std::unique_ptr<HistoryBasicCompartment> parent_compartment;

    explicit HistoryBasicCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HistoryBasicCompartment> clone() const {
        auto c = std::make_unique<HistoryBasicCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HistoryBasic {
private:
    std::vector<std::unique_ptr<HistoryBasicCompartment>> _state_stack;
    std::unique_ptr<HistoryBasicCompartment> __compartment;
    std::unique_ptr<HistoryBasicCompartment> __next_compartment;
    std::vector<HistoryBasicFrameContext> _context_stack;

    void __kernel(HistoryBasicFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HistoryBasicFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HistoryBasicFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HistoryBasicFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HistoryBasicFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        } else if (state_name == "C") {
            _state_C(__e);
        }
    }

    void __transition(std::unique_ptr<HistoryBasicCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_C(HistoryBasicFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("C"));
            return;;
        } else if (__e._message == "return_back") {
            auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
        }
    }

    void _state_A(HistoryBasicFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("A"));
            return;;
        } else if (__e._message == "gotoB") {
            auto __new_compartment = std::make_unique<HistoryBasicCompartment>("B");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "gotoC_from_A") {
            _state_stack.push_back(__compartment->clone());
            auto __new_compartment = std::make_unique<HistoryBasicCompartment>("C");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_B(HistoryBasicFrameEvent& __e) {
        if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("B"));
            return;;
        } else if (__e._message == "gotoC_from_B") {
            _state_stack.push_back(__compartment->clone());
            auto __new_compartment = std::make_unique<HistoryBasicCompartment>("C");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    HistoryBasic() {
        __compartment = std::make_unique<HistoryBasicCompartment>("A");
        HistoryBasicFrameEvent __frame_event("$>");
        HistoryBasicFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void gotoC_from_A() {
        HistoryBasicFrameEvent __e("gotoC_from_A");
        HistoryBasicFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void gotoC_from_B() {
        HistoryBasicFrameEvent __e("gotoC_from_B");
        HistoryBasicFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void gotoB() {
        HistoryBasicFrameEvent __e("gotoB");
        HistoryBasicFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void return_back() {
        HistoryBasicFrameEvent __e("return_back");
        HistoryBasicFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        HistoryBasicFrameEvent __e("get_state");
        HistoryBasicFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 33: Doc History Basic ===\n");
    HistoryBasic h;

    if (h.get_state() != "A") {
        printf("FAIL: Expected 'A', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.gotoC_from_A();
    if (h.get_state() != "C") {
        printf("FAIL: Expected 'C', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.return_back();
    if (h.get_state() != "A") {
        printf("FAIL: Expected 'A' after pop, got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.gotoB();
    if (h.get_state() != "B") {
        printf("FAIL: Expected 'B', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.gotoC_from_B();
    if (h.get_state() != "C") {
        printf("FAIL: Expected 'C', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.return_back();
    if (h.get_state() != "B") {
        printf("FAIL: Expected 'B' after pop, got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    printf("PASS: History push/pop works correctly\n");
    return 0;
}
