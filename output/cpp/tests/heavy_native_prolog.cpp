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

// Test: Heavy native prolog and epilog with edge-case C++ syntax.

class NativeHelper {
    // Mentions @@system and -> $State in comments
    // These should NOT be parsed as Frame
public:
    std::string process(const std::map<std::string, std::string>& data) {
        // Comment with -> $Transition and => $^ and push$
        return std::string("{\"key\": \"value with { braces }\"}");
    }
};

// Global with @@ in string
std::map<std::string, std::string> GLOBAL_CONFIG = {
    {"description", "Config with @@system-like syntax"},
    {"pattern", "-> $Start"},
};

class HeavyNativePrologFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HeavyNativePrologFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HeavyNativePrologFrameContext {
public:
    HeavyNativePrologFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HeavyNativePrologFrameContext(HeavyNativePrologFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HeavyNativePrologCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HeavyNativePrologFrameEvent> forward_event;
    std::unique_ptr<HeavyNativePrologCompartment> parent_compartment;

    explicit HeavyNativePrologCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HeavyNativePrologCompartment> clone() const {
        auto c = std::make_unique<HeavyNativePrologCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HeavyNativeProlog {
private:
    std::vector<std::unique_ptr<HeavyNativePrologCompartment>> _state_stack;
    std::unique_ptr<HeavyNativePrologCompartment> __compartment;
    std::unique_ptr<HeavyNativePrologCompartment> __next_compartment;
    std::vector<HeavyNativePrologFrameContext> _context_stack;

    void __kernel(HeavyNativePrologFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HeavyNativePrologFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HeavyNativePrologFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HeavyNativePrologFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HeavyNativePrologFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        }
    }

    void __transition(std::unique_ptr<HeavyNativePrologCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Start(HeavyNativePrologFrameEvent& __e) {
        if (__e._message == "run_test") {
            NativeHelper h;
            std::string result = h.process(GLOBAL_CONFIG);
            if (result.length() > 0) {
                printf("PASS: Heavy native prolog handled correctly\n");
            } else {
                assert(false);
            }
        }
    }

public:
    HeavyNativeProlog() {
        __compartment = std::make_unique<HeavyNativePrologCompartment>("Start");
        HeavyNativePrologFrameEvent __frame_event("$>");
        HeavyNativePrologFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void run_test() {
        HeavyNativePrologFrameEvent __e("run_test");
        HeavyNativePrologFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }
};

// Heavy epilog
class PostSystem {
public:
    std::map<std::string, std::string> data = {{"@@system", "in dict"}, {"-> $State", "in dict"}};

    bool run() {
        // -> $NotATransition
        // => $^
        return true;
    }
};

int main() {
    HeavyNativeProlog s;
    s.run_test();
    PostSystem p;
    if (!p.run()) { assert(false); }
    return 0;
}
