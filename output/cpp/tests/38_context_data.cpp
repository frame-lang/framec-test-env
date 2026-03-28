#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Test: Context Data (@@:data)
// Validates call-scoped data that persists across handler -> <$ -> $> chain

class ContextDataTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    ContextDataTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class ContextDataTestFrameContext {
public:
    ContextDataTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    ContextDataTestFrameContext(ContextDataTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class ContextDataTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<ContextDataTestFrameEvent> forward_event;
    std::unique_ptr<ContextDataTestCompartment> parent_compartment;

    explicit ContextDataTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<ContextDataTestCompartment> clone() const {
        auto c = std::make_unique<ContextDataTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class ContextDataTest {
private:
    std::vector<std::unique_ptr<ContextDataTestCompartment>> _state_stack;
    std::unique_ptr<ContextDataTestCompartment> __compartment;
    std::unique_ptr<ContextDataTestCompartment> __next_compartment;
    std::vector<ContextDataTestFrameContext> _context_stack;

    void __kernel(ContextDataTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            ContextDataTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                ContextDataTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    ContextDataTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(ContextDataTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "End") {
            _state_End(__e);
        }
    }

    void __transition(std::unique_ptr<ContextDataTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(ContextDataTestFrameEvent& __e) {
        if (__e._message == "<$") {
            auto trace = std::any_cast<std::string>(_context_stack.back()._data["trace"]);
            _context_stack.back()._data["trace"] = std::any(trace + ",exit");
        } else if (__e._message == "check_data_isolation") {
            _context_stack.back()._data["outer"] = std::any(std::string("outer_value"));
            std::string inner_result = this->process_with_data(99);
            _context_stack.back()._return = std::any(std::string("outer_data=") + std::any_cast<std::string>(_context_stack.back()._data["outer"]) + ",inner=" + inner_result);
        } else if (__e._message == "process_with_data") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            _context_stack.back()._data["input"] = std::any(value);
            _context_stack.back()._data["trace"] = std::any(std::string("handler"));

            _context_stack.back()._return = std::any(std::string("processed:") + std::to_string(std::any_cast<int>(_context_stack.back()._data["input"])));
        } else if (__e._message == "transition_preserves_data") {
            auto x = std::any_cast<int>(__e._parameters.at("x"));
            _context_stack.back()._data["started_in"] = std::any(std::string("Start"));
            _context_stack.back()._data["value"] = std::any(x);
            _context_stack.back()._data["trace"] = std::any(std::string("handler"));
            auto __new_compartment = std::make_unique<ContextDataTestCompartment>("End");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_End(ContextDataTestFrameEvent& __e) {
        if (__e._message == "$>") {
            auto trace = std::any_cast<std::string>(_context_stack.back()._data["trace"]);
            trace += ",enter";
            _context_stack.back()._data["trace"] = std::any(trace);
            _context_stack.back()._data["ended_in"] = std::any(std::string("End"));

            _context_stack.back()._return = std::any(std::string("from=") + std::any_cast<std::string>(_context_stack.back()._data["started_in"]) + ",to=" + std::any_cast<std::string>(_context_stack.back()._data["ended_in"]) + ",value=" + std::to_string(std::any_cast<int>(_context_stack.back()._data["value"])) + ",trace=" + trace);
        }
    }

public:
    ContextDataTest() {
        __compartment = std::make_unique<ContextDataTestCompartment>("Start");
        ContextDataTestFrameEvent __frame_event("$>");
        ContextDataTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string process_with_data(int value) {
        std::unordered_map<std::string, std::any> __params;
        __params["value"] = value;
        ContextDataTestFrameEvent __e("process_with_data", std::move(__params));
        ContextDataTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string check_data_isolation() {
        ContextDataTestFrameEvent __e("check_data_isolation");
        ContextDataTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string transition_preserves_data(int x) {
        std::unordered_map<std::string, std::any> __params;
        __params["x"] = x;
        ContextDataTestFrameEvent __e("transition_preserves_data", std::move(__params));
        ContextDataTestFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 38: Context Data ===\n");

    // Test 1: Basic data set/get
    ContextDataTest s1;
    std::string result = s1.process_with_data(42);
    if (result != "processed:42") {
        printf("FAIL: Expected 'processed:42', got '%s'\n", result.c_str());
        assert(false);
    }
    printf("1. process_with_data(42) = '%s'\n", result.c_str());

    // Test 2: Data isolation
    ContextDataTest s2;
    result = s2.check_data_isolation();
    std::string expected = "outer_data=outer_value,inner=processed:99";
    if (result != expected) {
        printf("FAIL: Expected '%s', got '%s'\n", expected.c_str(), result.c_str());
        assert(false);
    }
    printf("2. check_data_isolation() = '%s'\n", result.c_str());

    // Test 3: Data preserved across transition
    ContextDataTest s3;
    result = s3.transition_preserves_data(100);
    if (result.find("from=Start") == std::string::npos) {
        printf("FAIL: Expected 'from=Start' in '%s'\n", result.c_str());
        assert(false);
    }
    if (result.find("to=End") == std::string::npos) {
        printf("FAIL: Expected 'to=End' in '%s'\n", result.c_str());
        assert(false);
    }
    if (result.find("value=100") == std::string::npos) {
        printf("FAIL: Expected 'value=100' in '%s'\n", result.c_str());
        assert(false);
    }
    printf("3. transition_preserves_data(100) = '%s'\n", result.c_str());

    printf("PASS: Context data works correctly\n");
    return 0;
}
