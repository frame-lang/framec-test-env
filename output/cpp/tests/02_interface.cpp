#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

class WithInterfaceFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    WithInterfaceFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class WithInterfaceFrameContext {
public:
    WithInterfaceFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    WithInterfaceFrameContext(WithInterfaceFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class WithInterfaceCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<WithInterfaceFrameEvent> forward_event;
    std::unique_ptr<WithInterfaceCompartment> parent_compartment;

    explicit WithInterfaceCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<WithInterfaceCompartment> clone() const {
        auto c = std::make_unique<WithInterfaceCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class WithInterface {
private:
    std::vector<std::unique_ptr<WithInterfaceCompartment>> _state_stack;
    std::unique_ptr<WithInterfaceCompartment> __compartment;
    std::unique_ptr<WithInterfaceCompartment> __next_compartment;
    std::vector<WithInterfaceFrameContext> _context_stack;

    void __kernel(WithInterfaceFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            WithInterfaceFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                WithInterfaceFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    WithInterfaceFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(WithInterfaceFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    void __transition(std::unique_ptr<WithInterfaceCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Ready(WithInterfaceFrameEvent& __e) {
        if (__e._message == "get_count") {
            _context_stack.back()._return = std::any(call_count);
            return;;
        } else if (__e._message == "greet") {
            auto name = std::any_cast<std::string>(__e._parameters.at("name"));
            call_count += 1;
            _context_stack.back()._return = std::any(std::string("Hello, ") + name + "!");
            return;;
        }
    }

public:
    int call_count = 0;

    WithInterface() {
        __compartment = std::make_unique<WithInterfaceCompartment>("Ready");
        WithInterfaceFrameEvent __frame_event("$>");
        WithInterfaceFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string greet(std::string name) {
        std::unordered_map<std::string, std::any> __params;
        __params["name"] = name;
        WithInterfaceFrameEvent __e("greet", std::move(__params));
        WithInterfaceFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_count() {
        WithInterfaceFrameEvent __e("get_count");
        WithInterfaceFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 02: Interface Methods ===\n");
    WithInterface s;

    std::string result = s.greet("World");
    if (result != "Hello, World!") {
        printf("FAIL: Expected 'Hello, World!', got '%s'\n", result.c_str());
        assert(false);
    }
    printf("greet('World') = %s\n", result.c_str());

    int count = s.get_count();
    if (count != 1) {
        printf("FAIL: Expected count=1, got %d\n", count);
        assert(false);
    }
    printf("get_count() = %d\n", count);

    s.greet("Frame");
    int count2 = s.get_count();
    if (count2 != 2) {
        printf("FAIL: Expected count=2, got %d\n", count2);
        assert(false);
    }
    printf("After second call: get_count() = %d\n", count2);

    printf("PASS: Interface methods work correctly\n");
    return 0;
}
