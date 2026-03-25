#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class HSMForwardFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMForwardFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMForwardFrameContext {
public:
    HSMForwardFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMForwardFrameContext(HSMForwardFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMForwardCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMForwardFrameEvent> forward_event;
    std::unique_ptr<HSMForwardCompartment> parent_compartment;

    explicit HSMForwardCompartment(const std::string& state) : state(state) {}
};

class HSMForward {
private:
    std::unique_ptr<HSMForwardCompartment> __compartment;
    std::unique_ptr<HSMForwardCompartment> __next_compartment;
    std::vector<std::unique_ptr<HSMForwardCompartment>> _state_stack;
    std::vector<HSMForwardFrameContext> _context_stack;

    int count = 0;;

    void __kernel(HSMForwardFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMForwardFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMForwardFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMForwardFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMForwardFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMForwardCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Child(HSMForwardFrameEvent& __e) {
        if (__e._message == "event_a") {
            {
            count += 1;
            }
            return;
        } else if (__e._message == "event_b") {
            {
            count += 10;
            _state_Parent(__e);
            return;
            }
            return;
        } else if (__e._message == "get_count") {
            {
            _context_stack.back()._return = count;
            return;
            }
            return;
        }
    }

    void _state_Parent(HSMForwardFrameEvent& __e) {
        if (__e._message == "event_a") {
            {
            count += 100;
            }
            return;
        } else if (__e._message == "event_b") {
            {
            count += 1000;
            }
            return;
        } else if (__e._message == "get_count") {
            {
            _context_stack.back()._return = count;
            return;
            }
            return;
        }
    }

public:
    HSMForward() {
        __compartment = std::make_unique<HSMForwardCompartment>("Child");
        count = 0;;
        HSMForwardFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void event_a() {
        HSMForwardFrameEvent __e("event_a");
        HSMForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void event_b() {
        HSMForwardFrameEvent __e("event_b");
        HSMForwardFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_count() {
        HSMForwardFrameEvent __e("get_count");
        HSMForwardFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 08: HSM Forward ===" << std::endl;
    HSMForward s;

    // event_a should be handled by Child (no forward)
    s.event_a();
    int count = s.get_count();
    assert(count == 1);
    std::cout << "After event_a: count = " << count << " (expected 1)" << std::endl;

    // event_b should forward to Parent (+10 in Child, +1000 in Parent)
    s.event_b();
    count = s.get_count();
    assert(count == 1011);
    std::cout << "After event_b (forwarded): count = " << count << " (expected 1011)" << std::endl;

    std::cout << "PASS: 08 hsm" << std::endl;
    return 0;
}
