#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Test: Frame tokens inside C++ comments should NOT be recognized as Frame syntax.

// @@system FakeSystem { }
// @@target python_3
// -> $FakeTransition
/* @@system BlockComment { } */
/*
 * -> $MultiLine
 * => $^
 * push$
 * @@target rust
 */

class FrameTokensInCommentsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    FrameTokensInCommentsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class FrameTokensInCommentsFrameContext {
public:
    FrameTokensInCommentsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    FrameTokensInCommentsFrameContext(FrameTokensInCommentsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class FrameTokensInCommentsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<FrameTokensInCommentsFrameEvent> forward_event;
    std::unique_ptr<FrameTokensInCommentsCompartment> parent_compartment;

    explicit FrameTokensInCommentsCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<FrameTokensInCommentsCompartment> clone() const {
        auto c = std::make_unique<FrameTokensInCommentsCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class FrameTokensInComments {
private:
    std::vector<std::unique_ptr<FrameTokensInCommentsCompartment>> _state_stack;
    std::unique_ptr<FrameTokensInCommentsCompartment> __compartment;
    std::unique_ptr<FrameTokensInCommentsCompartment> __next_compartment;
    std::vector<FrameTokensInCommentsFrameContext> _context_stack;

    void __kernel(FrameTokensInCommentsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            FrameTokensInCommentsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                FrameTokensInCommentsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    FrameTokensInCommentsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(FrameTokensInCommentsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<FrameTokensInCommentsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(FrameTokensInCommentsFrameEvent& __e) {
        if (__e._message == "run_test") {
            // -> $FakeState
            // => $^
            // push$
            /* -> $BlockTransition */
            /* @@:return = 99 */
            int x = 1; // -> $InlineComment
            printf("PASS: Frame tokens in comments correctly ignored\n");
        }
    }

public:
    FrameTokensInComments() {
        __compartment = std::make_unique<FrameTokensInCommentsCompartment>("Start");
        FrameTokensInCommentsFrameEvent __frame_event("$>");
        FrameTokensInCommentsFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void run_test() {
        FrameTokensInCommentsFrameEvent __e("run_test");
        FrameTokensInCommentsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

int main() {
    FrameTokensInComments s;
    s.run_test();
    return 0;
}
