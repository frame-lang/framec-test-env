#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class MixedBodyStringsCommentsFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    MixedBodyStringsCommentsFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class MixedBodyStringsCommentsFrameContext {
public:
    MixedBodyStringsCommentsFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    MixedBodyStringsCommentsFrameContext(MixedBodyStringsCommentsFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class MixedBodyStringsCommentsCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<MixedBodyStringsCommentsFrameEvent> forward_event;
    std::unique_ptr<MixedBodyStringsCommentsCompartment> parent_compartment;

    explicit MixedBodyStringsCommentsCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<MixedBodyStringsCommentsCompartment> clone() const {
        auto c = std::make_unique<MixedBodyStringsCommentsCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class MixedBodyStringsComments {
private:
    std::vector<std::unique_ptr<MixedBodyStringsCommentsCompartment>> _state_stack;
    std::unique_ptr<MixedBodyStringsCommentsCompartment> __compartment;
    std::unique_ptr<MixedBodyStringsCommentsCompartment> __next_compartment;
    std::vector<MixedBodyStringsCommentsFrameContext> _context_stack;

    void __kernel(MixedBodyStringsCommentsFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            MixedBodyStringsCommentsFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                MixedBodyStringsCommentsFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    MixedBodyStringsCommentsFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(MixedBodyStringsCommentsFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Init") {
            _state_Init(__e);
        } else if (state_name == "Done") {
            _state_Done(__e);
        }
    }

    void __transition(std::unique_ptr<MixedBodyStringsCommentsCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Init(MixedBodyStringsCommentsFrameEvent& __e) {
        if (__e._message == "start") {
            // Native C++ with Frame-statement-like tokens in strings and comments
            std::string text = "This mentions -> $Next and pop$ inside a string.";
            // A comment that mentions => $^ and -> $Other should not be parsed as Frame
            printf("%s\n", text.c_str());
            auto __new_compartment = std::make_unique<MixedBodyStringsCommentsCompartment>("Done");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Done(MixedBodyStringsCommentsFrameEvent& __e) {

    }

public:
    MixedBodyStringsComments() {
        __compartment = std::make_unique<MixedBodyStringsCommentsCompartment>("Init");
        MixedBodyStringsCommentsFrameEvent __frame_event("$>");
        MixedBodyStringsCommentsFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void start() {
        MixedBodyStringsCommentsFrameEvent __e("start");
        MixedBodyStringsCommentsFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

// Stub functions for placeholder calls
void native() {}
void x() {}

// TAP test harness
int main() {
    printf("TAP version 14\n");
    printf("1..1\n");
    try {
        MixedBodyStringsComments s;
        s.start();
        printf("ok 1 - test_mixed_body_strings_comments\n");
    } catch (...) {
        printf("not ok 1 - test_mixed_body_strings_comments\n");
    }
    return 0;
}
