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

// Documentation Example: HSM with History (History203)

class HistoryHSMFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HistoryHSMFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HistoryHSMFrameContext {
public:
    HistoryHSMFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HistoryHSMFrameContext(HistoryHSMFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HistoryHSMCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HistoryHSMFrameEvent> forward_event;
    std::unique_ptr<HistoryHSMCompartment> parent_compartment;

    explicit HistoryHSMCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HistoryHSMCompartment> clone() const {
        auto c = std::make_unique<HistoryHSMCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HistoryHSM {
private:
    std::vector<std::unique_ptr<HistoryHSMCompartment>> _state_stack;
    std::unique_ptr<HistoryHSMCompartment> __compartment;
    std::unique_ptr<HistoryHSMCompartment> __next_compartment;
    std::vector<HistoryHSMFrameContext> _context_stack;

    void __kernel(HistoryHSMFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HistoryHSMFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HistoryHSMFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HistoryHSMFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HistoryHSMFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Waiting") {
            _state_Waiting(__e);
        } else if (state_name == "A") {
            _state_A(__e);
        } else if (state_name == "B") {
            _state_B(__e);
        } else if (state_name == "AB") {
            _state_AB(__e);
        } else if (state_name == "C") {
            _state_C(__e);
        }
    }

    void __transition(std::unique_ptr<HistoryHSMCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_A(HistoryHSMFrameEvent& __e) {
        if (__e._message == "$>") {
            this->log_msg("In $A");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("A"));
            return;;
        } else if (__e._message == "gotoB") {
            this->log_msg("gotoB");
            auto __new_compartment = std::make_unique<HistoryHSMCompartment>("B");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else {
            _state_AB(__e);
        }
    }

    void _state_Waiting(HistoryHSMFrameEvent& __e) {
        if (__e._message == "$>") {
            this->log_msg("In $Waiting");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Waiting"));
            return;;
        } else if (__e._message == "gotoA") {
            this->log_msg("gotoA");
            auto __new_compartment = std::make_unique<HistoryHSMCompartment>("A");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "gotoB") {
            this->log_msg("gotoB");
            auto __new_compartment = std::make_unique<HistoryHSMCompartment>("B");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_B(HistoryHSMFrameEvent& __e) {
        if (__e._message == "$>") {
            this->log_msg("In $B");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("B"));
            return;;
        } else if (__e._message == "gotoA") {
            this->log_msg("gotoA");
            auto __new_compartment = std::make_unique<HistoryHSMCompartment>("A");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else {
            _state_AB(__e);
        }
    }

    void _state_C(HistoryHSMFrameEvent& __e) {
        if (__e._message == "$>") {
            this->log_msg("In $C");
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("C"));
            return;;
        } else if (__e._message == "goBack") {
            this->log_msg("goBack");
            auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
        }
    }

    void _state_AB(HistoryHSMFrameEvent& __e) {
        if (__e._message == "gotoC") {
            this->log_msg("gotoC in $AB");
            _state_stack.push_back(__compartment->clone());
            auto __new_compartment = std::make_unique<HistoryHSMCompartment>("C");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void log_msg(std::string msg) {
                    event_log.push_back(msg);
    }

public:
    std::vector<std::string> event_log = {};

    HistoryHSM() {
        __compartment = std::make_unique<HistoryHSMCompartment>("Waiting");
        HistoryHSMFrameEvent __frame_event("$>");
        HistoryHSMFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void gotoA() {
        HistoryHSMFrameEvent __e("gotoA");
        HistoryHSMFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void gotoB() {
        HistoryHSMFrameEvent __e("gotoB");
        HistoryHSMFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void gotoC() {
        HistoryHSMFrameEvent __e("gotoC");
        HistoryHSMFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void goBack() {
        HistoryHSMFrameEvent __e("goBack");
        HistoryHSMFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        HistoryHSMFrameEvent __e("get_state");
        HistoryHSMFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::vector<std::string> get_log() {
        HistoryHSMFrameEvent __e("get_log");
        HistoryHSMFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 34: Doc History HSM ===\n");
    HistoryHSM h;

    if (h.get_state() != "Waiting") {
        printf("FAIL: Expected 'Waiting', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.gotoA();
    if (h.get_state() != "A") {
        printf("FAIL: Expected 'A', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.gotoC();
    if (h.get_state() != "C") {
        printf("FAIL: Expected 'C', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.goBack();
    if (h.get_state() != "A") {
        printf("FAIL: Expected 'A' after goBack, got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.gotoB();
    if (h.get_state() != "B") {
        printf("FAIL: Expected 'B', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.gotoC();
    if (h.get_state() != "C") {
        printf("FAIL: Expected 'C', got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    h.goBack();
    if (h.get_state() != "B") {
        printf("FAIL: Expected 'B' after goBack, got '%s'\n", h.get_state().c_str());
        assert(false);
    }

    printf("PASS: HSM with history works correctly\n");
    return 0;
}
