#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>
#include <vector>

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
};

class ContextDataTest {
private:
    std::unique_ptr<ContextDataTestCompartment> __compartment;
    std::unique_ptr<ContextDataTestCompartment> __next_compartment;
    std::vector<std::unique_ptr<ContextDataTestCompartment>> _state_stack;
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
            {
            auto& trace = @@:data["trace"];
            trace.push_back("exit");
            }
            return;
        } else if (__e._message == "process_with_data") {
            auto value = std::any_cast<int>(__e._parameters.at("value"));
            {
            @@:data["input"] = @@.value;
            @@:data["trace"] = std::vector<std::string>{"handler"};
            _context_stack.back()._return = std::string("processed:") + std::to_string(@@:data["input"]);
            }
            return;
        } else if (__e._message == "check_data_isolation") {
            {
            @@:data["outer"] = std::string("outer_value");
            std::string inner_result = this->process_with_data(99);
            _context_stack.back()._return = std::string("outer_data=") + @@:data["outer"] + ",inner=" + inner_result;
            }
            return;
        } else if (__e._message == "transition_preserves_data") {
            auto x = std::any_cast<int>(__e._parameters.at("x"));
            {
            @@:data["started_in"] = std::string("Start");
            @@:data["value"] = @@.x;
            @@:data["trace"] = std::vector<std::string>{"handler"};
            auto __comp = std::make_unique<ContextDataTestCompartment>("End");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_End(ContextDataTestFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            auto& trace = @@:data["trace"];
            trace.push_back("enter");
            @@:data["ended_in"] = std::string("End");
            std::string trace_str = "";
            for (size_t i = 0; i < trace.size(); i++) {
            if (i > 0) trace_str += ",";
            trace_str += trace[i];
            }
            _context_stack.back()._return = std::string("from=") + @@:data["started_in"] + ",to=" + @@:data["ended_in"] + ",value=" + std::to_string(@@:data["value"]) + ",trace=" + trace_str;
            }
            return;
        }
    }

public:
    ContextDataTest() {
        __compartment = std::make_unique<ContextDataTestCompartment>("Start");
        ContextDataTestFrameEvent __frame_event("$>");
        __kernel(__frame_event);
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
