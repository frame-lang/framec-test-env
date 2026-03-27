#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>
#include <vector>
#include <algorithm>

class ForwardEnterFirstFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ForwardEnterFirstFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ForwardEnterFirstFrameContext {
public:
    ForwardEnterFirstFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ForwardEnterFirstFrameContext(ForwardEnterFirstFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ForwardEnterFirstCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ForwardEnterFirstFrameEvent> forward_event;
    std::unique_ptr<ForwardEnterFirstCompartment> parent_compartment;

    explicit ForwardEnterFirstCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<ForwardEnterFirstCompartment> clone() const {
        auto c = std::make_unique<ForwardEnterFirstCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class ForwardEnterFirst {
private:
    std::vector<std::unique_ptr<ForwardEnterFirstCompartment>> _state_stack;
    std::unique_ptr<ForwardEnterFirstCompartment> __compartment;
    std::unique_ptr<ForwardEnterFirstCompartment> __next_compartment;
    std::vector<ForwardEnterFirstFrameContext> _context_stack;

    void __kernel(ForwardEnterFirstFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ForwardEnterFirstFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ForwardEnterFirstFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ForwardEnterFirstFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ForwardEnterFirstFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Working") {
            _state_Working(__e);
        }
    }

    void __transition(std::unique_ptr<ForwardEnterFirstCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Working(ForwardEnterFirstFrameEvent& __e) {
        auto* __sv_comp = __compartment.get();
        while (__sv_comp && __sv_comp->state != "Working") { __sv_comp = __sv_comp->parent_compartment.get(); }
        if (__e._message == "$>") {
            if (__compartment->state_vars.count("counter") == 0) { __compartment->state_vars["counter"] = std::any(100); }
            event_log.push_back("Working:enter");
        } else if (__e._message == "get_counter") {
            _context_stack.back()._return = std::any(std::any_cast<int>(__sv_comp->state_vars["counter"]));
            return;;
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "process") {
            event_log.push_back(std::string("Working:process:counter=") + std::to_string(std::any_cast<int>(__sv_comp->state_vars["counter"])));
            __sv_comp->state_vars["counter"] = std::any(std::any_cast<int>(__sv_comp->state_vars["counter"]) + 1);
        }
    }

    void _state_Idle(ForwardEnterFirstFrameEvent& __e) {
        if (__e._message == "get_counter") {
            _context_stack.back()._return = std::any(-1);
            return;;
        } else if (__e._message == "get_log") {
            _context_stack.back()._return = std::any(event_log);
            return;;
        } else if (__e._message == "process") {
            auto __new_compartment = std::make_unique<ForwardEnterFirstCompartment>("Working");
            __new_compartment->parent_compartment = __compartment->clone();
            __new_compartment->forward_event = std::make_unique<ForwardEnterFirstFrameEvent>(__e);
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    std::vector<std::string> event_log = {};

    ForwardEnterFirst() {
        __compartment = std::make_unique<ForwardEnterFirstCompartment>("Idle");
        ForwardEnterFirstFrameEvent __frame_event("$>");
        ForwardEnterFirstFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void process() {
        ForwardEnterFirstFrameEvent __e("process");
        ForwardEnterFirstFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_counter() {
        ForwardEnterFirstFrameEvent __e("get_counter");
        ForwardEnterFirstFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::vector<std::string> get_log() {
        ForwardEnterFirstFrameEvent __e("get_log");
        ForwardEnterFirstFrameContext __ctx(std::move(__e), std::any(std::vector<std::string>()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::vector<std::string>>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 29: Forward Enter First ===\n");
    ForwardEnterFirst s;

    if (s.get_counter() != -1) {
        printf("FAIL: Expected -1 in Idle\n");
        assert(false);
    }

    s.process();

    int counter = s.get_counter();
    auto log = s.get_log();
    printf("Counter after forward: %d\n", counter);

    if (std::find(log.begin(), log.end(), "Working:enter") == log.end()) {
        printf("FAIL: Expected 'Working:enter' in log\n");
        assert(false);
    }

    if (std::find(log.begin(), log.end(), "Working:process:counter=100") == log.end()) {
        printf("FAIL: Expected 'Working:process:counter=100' in log\n");
        assert(false);
    }

    if (counter != 101) {
        printf("FAIL: Expected counter=101, got %d\n", counter);
        assert(false);
    }

    auto enterIt = std::find(log.begin(), log.end(), "Working:enter");
    auto processIt = std::find(log.begin(), log.end(), "Working:process:counter=100");
    if (enterIt >= processIt) {
        printf("FAIL: $> should run before process\n");
        assert(false);
    }

    printf("PASS: Forward sends $> first for non-$> events\n");
    return 0;
}
