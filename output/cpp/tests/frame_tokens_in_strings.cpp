#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

// Test: Frame tokens inside C++ strings should NOT be recognized as Frame syntax.

class FrameTokensInStringsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    FrameTokensInStringsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class FrameTokensInStringsFrameContext {
public:
    FrameTokensInStringsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    FrameTokensInStringsFrameContext(FrameTokensInStringsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class FrameTokensInStringsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<FrameTokensInStringsFrameEvent> forward_event;
    std::unique_ptr<FrameTokensInStringsCompartment> parent_compartment;

    explicit FrameTokensInStringsCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<FrameTokensInStringsCompartment> clone() const {
        auto c = std::make_unique<FrameTokensInStringsCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class FrameTokensInStrings {
private:
    std::vector<std::unique_ptr<FrameTokensInStringsCompartment>> _state_stack;
    std::unique_ptr<FrameTokensInStringsCompartment> __compartment;
    std::unique_ptr<FrameTokensInStringsCompartment> __next_compartment;
    std::vector<FrameTokensInStringsFrameContext> _context_stack;

    void __kernel(FrameTokensInStringsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            FrameTokensInStringsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                FrameTokensInStringsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    FrameTokensInStringsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(FrameTokensInStringsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<FrameTokensInStringsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(FrameTokensInStringsFrameEvent& __e) {
        if (__e._message == "run_test") {
            // Regular strings
            std::string a = "-> $FakeState";
            std::string b = "=> $^";
            std::string c = "push$ and pop$";
            std::string d = "dollar_dot_fake_var = 42";
            std::string e = "@@target cpp_17";
            std::string f = "@@system NotReal { }";
            std::string g = "@@:return = 99";

            printf("PASS: Frame tokens in strings correctly ignored\n");
        }
    }

public:
    FrameTokensInStrings() {
        __compartment = std::make_unique<FrameTokensInStringsCompartment>("Start");
        FrameTokensInStringsFrameEvent __frame_event("$>");
        FrameTokensInStringsFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void run_test() {
        FrameTokensInStringsFrameEvent __e("run_test");
        FrameTokensInStringsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

int main() {
    FrameTokensInStrings s;
    s.run_test();
    return 0;
}
