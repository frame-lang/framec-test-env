#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>
#include <map>
#include <vector>

// Test: Deeply nested braces and braces-in-strings should not confuse the body closer.

class NestedBracesFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    NestedBracesFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class NestedBracesFrameContext {
public:
    NestedBracesFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    NestedBracesFrameContext(NestedBracesFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class NestedBracesCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<NestedBracesFrameEvent> forward_event;
    std::unique_ptr<NestedBracesCompartment> parent_compartment;

    explicit NestedBracesCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<NestedBracesCompartment> clone() const {
        auto c = std::make_unique<NestedBracesCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class NestedBraces {
private:
    std::vector<std::unique_ptr<NestedBracesCompartment>> _state_stack;
    std::unique_ptr<NestedBracesCompartment> __compartment;
    std::unique_ptr<NestedBracesCompartment> __next_compartment;
    std::vector<NestedBracesFrameContext> _context_stack;

    void __kernel(NestedBracesFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            NestedBracesFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                NestedBracesFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    NestedBracesFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(NestedBracesFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<NestedBracesCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(NestedBracesFrameEvent& __e) {
        if (__e._message == "run_test") {
            // String containing braces
            std::string s1 = "string with { braces }";
            std::string s2 = "nested { { { braces } } }";
            std::string s3 = "{\"json\": \"in string\"}";

            // Multi-level nesting
            std::map<int, std::map<std::string, int>> result;
            for (int i = 0; i < 3; i++) {
                result[i] = {{"level", i}};
            }

            if (result.size() == 3) {
                printf("PASS: Nested braces handled correctly\n");
            } else {
                printf("FAIL: Wrong result count\n");
                assert(false);
            }
        }
    }

public:
    NestedBraces() {
        __compartment = std::make_unique<NestedBracesCompartment>("Start");
        NestedBracesFrameEvent __frame_event("$>");
        NestedBracesFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void run_test() {
        NestedBracesFrameEvent __e("run_test");
        NestedBracesFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

int main() {
    NestedBraces s;
    s.run_test();
    return 0;
}
