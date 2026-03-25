#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>
#include <stdexcept>

class ActionsTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ActionsTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ActionsTestFrameContext {
public:
    ActionsTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ActionsTestFrameContext(ActionsTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ActionsTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ActionsTestFrameEvent> forward_event;
    std::unique_ptr<ActionsTestCompartment> parent_compartment;

    explicit ActionsTestCompartment(const std::string& state) : state(state) {}
};

class ActionsTest {
private:
    std::unique_ptr<ActionsTestCompartment> __compartment;
    std::unique_ptr<ActionsTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<ActionsTestCompartment>> _state_stack;
    std::vector<ActionsTestFrameContext> _context_stack;

    std::string event_log = "";

    void __kernel(ActionsTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ActionsTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ActionsTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ActionsTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ActionsTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<ActionsTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(ActionsTestFrameEvent& __e) {
        if (__e._message == "process") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            {
            this->__log_event("start");
            this->__validate_positive(value);
            this->__log_event("valid");
            int result = value * 2;
            this->__log_event("done");
            _context_stack.back()._return = result;
            return;
            }
            return;
        } else if (__e._message == "get_log") {
            {
            _context_stack.back()._return = event_log;
            return;
            }
            return;
        }
    }

public:
    ActionsTest() {
        __compartment = std::make_unique<ActionsTestCompartment>("Ready");
        event_log = "";
        ActionsTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    int process(int value) {
        std::unordered_map<std::string, std::any> __params;
        __params["value"] = value;
        ActionsTestFrameEvent __e("process", std::move(__params));
        ActionsTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_log() {
        ActionsTestFrameEvent __e("get_log");
        ActionsTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void __log_event() {
        {
        event_log = event_log + msg + ";";
        }
    }

    void __validate_positive() {
        {
        if (n < 0) {
        throw std::runtime_error("Value must be positive");
        }
        }
    }

};

int main() {
    printf("=== Test 21: Actions Basic (C++) ===\n");
    ActionsTest s;

    // Test 1: Actions are called correctly
    int result = s.process(5);
    if (result != 10) {
        printf("FAIL: Expected 10, got %d\n", result);
        assert(false);
    }
    printf("1. process(5) = %d\n", result);

    // Test 2: Log shows action calls
    std::string log = s.get_log();
    if (log.find("start") == std::string::npos) {
        printf("FAIL: Missing 'start' in log: %s\n", log.c_str());
        assert(false);
    }
    if (log.find("valid") == std::string::npos) {
        printf("FAIL: Missing 'valid' in log: %s\n", log.c_str());
        assert(false);
    }
    if (log.find("done") == std::string::npos) {
        printf("FAIL: Missing 'done' in log: %s\n", log.c_str());
        assert(false);
    }
    printf("2. Log: %s\n", log.c_str());

    // Test 3: Action with validation
    try {
        s.process(-1);
        printf("FAIL: Should have thrown exception\n");
        assert(false);
    } catch (const std::runtime_error& e) {
        printf("3. Validation caught: %s\n", e.what());
    }

    printf("PASS: Actions basic works correctly\n");
    return 0;
}
