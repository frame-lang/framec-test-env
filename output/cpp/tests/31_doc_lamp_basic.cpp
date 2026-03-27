#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Documentation Example: Basic Lamp with enter/exit events

class LampFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    LampFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class LampFrameContext {
public:
    LampFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    LampFrameContext(LampFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class LampCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<LampFrameEvent> forward_event;
    std::unique_ptr<LampCompartment> parent_compartment;

    explicit LampCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<LampCompartment> clone() const {
        auto c = std::make_unique<LampCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class Lamp {
private:
    std::vector<std::unique_ptr<LampCompartment>> _state_stack;
    std::unique_ptr<LampCompartment> __compartment;
    std::unique_ptr<LampCompartment> __next_compartment;
    std::vector<LampFrameContext> _context_stack;

    void __kernel(LampFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            LampFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                LampFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    LampFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(LampFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Off") {
            _state_Off(__e);
        } else if (state_name == "On") {
            _state_On(__e);
        }
    }

    void __transition(std::unique_ptr<LampCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Off(LampFrameEvent& __e) {
        if (__e._message == "getColor") {
            _context_stack.back()._return = std::any(color);
            return;;
        } else if (__e._message == "isSwitchClosed") {
            _context_stack.back()._return = std::any(switch_closed);
            return;;
        } else if (__e._message == "setColor") {
            auto color = std::any_cast<std::string>(__e._parameters.at("color"));
            this->color = color;
        } else if (__e._message == "turnOn") {
            auto __new_compartment = std::make_unique<LampCompartment>("On");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_On(LampFrameEvent& __e) {
        if (__e._message == "<$") {
            this->openSwitch();
        } else if (__e._message == "$>") {
            this->closeSwitch();
        } else if (__e._message == "getColor") {
            _context_stack.back()._return = std::any(color);
            return;;
        } else if (__e._message == "isSwitchClosed") {
            _context_stack.back()._return = std::any(switch_closed);
            return;;
        } else if (__e._message == "setColor") {
            auto color = std::any_cast<std::string>(__e._parameters.at("color"));
            this->color = color;
        } else if (__e._message == "turnOff") {
            auto __new_compartment = std::make_unique<LampCompartment>("Off");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void closeSwitch() {
                    switch_closed = true;
    }

    void openSwitch() {
                    switch_closed = false;
    }

public:
    std::string color = "white";
    bool switch_closed = false;

    Lamp() {
        __compartment = std::make_unique<LampCompartment>("Off");
        LampFrameEvent __frame_event("$>");
        LampFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void turnOn() {
        LampFrameEvent __e("turnOn");
        LampFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void turnOff() {
        LampFrameEvent __e("turnOff");
        LampFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string getColor() {
        LampFrameEvent __e("getColor");
        LampFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void setColor(std::string color) {
        std::unordered_map<std::string, std::any> __params;
        __params["color"] = color;
        LampFrameEvent __e("setColor", std::move(__params));
        LampFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    bool isSwitchClosed() {
        LampFrameEvent __e("isSwitchClosed");
        LampFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 31: Doc Lamp Basic ===\n");
    Lamp lamp;

    if (lamp.isSwitchClosed() != false) {
        printf("FAIL: Switch should be open initially\n");
        assert(false);
    }

    lamp.turnOn();
    if (lamp.isSwitchClosed() != true) {
        printf("FAIL: Switch should be closed after turnOn\n");
        assert(false);
    }

    if (lamp.getColor() != "white") {
        printf("FAIL: Expected 'white', got '%s'\n", lamp.getColor().c_str());
        assert(false);
    }

    lamp.setColor("blue");
    if (lamp.getColor() != "blue") {
        printf("FAIL: Expected 'blue', got '%s'\n", lamp.getColor().c_str());
        assert(false);
    }

    lamp.turnOff();
    if (lamp.isSwitchClosed() != false) {
        printf("FAIL: Switch should be open after turnOff\n");
        assert(false);
    }

    printf("PASS: Basic lamp works correctly\n");
    return 0;
}
