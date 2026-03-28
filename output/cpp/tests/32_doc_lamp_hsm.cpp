#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

// Documentation Example: HSM Lamp with color behavior factored out

class LampHSMFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    LampHSMFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class LampHSMFrameContext {
public:
    LampHSMFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    LampHSMFrameContext(LampHSMFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class LampHSMCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<LampHSMFrameEvent> forward_event;
    std::unique_ptr<LampHSMCompartment> parent_compartment;

    explicit LampHSMCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<LampHSMCompartment> clone() const {
        auto c = std::make_unique<LampHSMCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class LampHSM {
private:
    std::vector<std::unique_ptr<LampHSMCompartment>> _state_stack;
    std::unique_ptr<LampHSMCompartment> __compartment;
    std::unique_ptr<LampHSMCompartment> __next_compartment;
    std::vector<LampHSMFrameContext> _context_stack;

    void __kernel(LampHSMFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            LampHSMFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                LampHSMFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    LampHSMFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(LampHSMFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Off") {
            _state_Off(__e);
        } else if (state_name == "On") {
            _state_On(__e);
        } else if (state_name == "ColorBehavior") {
            _state_ColorBehavior(__e);
        }
    }

    void __transition(std::unique_ptr<LampHSMCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_ColorBehavior(LampHSMFrameEvent& __e) {
        if (__e._message == "getColor") {
            _context_stack.back()._return = std::any(color);
            return;;
        } else if (__e._message == "setColor") {
            auto color = std::any_cast<std::string>(__e._parameters.at("color"));
            this->color = color;
        }
    }

    void _state_Off(LampHSMFrameEvent& __e) {
        if (__e._message == "isLampOn") {
            _context_stack.back()._return = std::any(lamp_on);
            return;;
        } else if (__e._message == "turnOn") {
            auto __new_compartment = std::make_unique<LampHSMCompartment>("On");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else {
            _state_ColorBehavior(__e);
        }
    }

    void _state_On(LampHSMFrameEvent& __e) {
        if (__e._message == "<$") {
            this->turnOffLamp();
        } else if (__e._message == "$>") {
            this->turnOnLamp();
        } else if (__e._message == "isLampOn") {
            _context_stack.back()._return = std::any(lamp_on);
            return;;
        } else if (__e._message == "turnOff") {
            auto __new_compartment = std::make_unique<LampHSMCompartment>("Off");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else {
            _state_ColorBehavior(__e);
        }
    }

    void turnOnLamp() {
                    lamp_on = true;
    }

    void turnOffLamp() {
                    lamp_on = false;
    }

public:
    std::string color = "white";
    bool lamp_on = false;

    LampHSM() {
        // HSM: Create parent compartment chain
        auto __parent_comp_0 = std::make_unique<LampHSMCompartment>("ColorBehavior");
        __compartment = std::make_unique<LampHSMCompartment>("Off");
        __compartment->parent_compartment = std::move(__parent_comp_0);
        LampHSMFrameEvent __frame_event("$>");
        LampHSMFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void turnOn() {
        LampHSMFrameEvent __e("turnOn");
        LampHSMFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void turnOff() {
        LampHSMFrameEvent __e("turnOff");
        LampHSMFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string getColor() {
        LampHSMFrameEvent __e("getColor");
        LampHSMFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void setColor(std::string color) {
        std::unordered_map<std::string, std::any> __params;
        __params["color"] = color;
        LampHSMFrameEvent __e("setColor", std::move(__params));
        LampHSMFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    bool isLampOn() {
        LampHSMFrameEvent __e("isLampOn");
        LampHSMFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 32: Doc Lamp HSM ===\n");
    LampHSM lamp;

    if (lamp.getColor() != "white") {
        printf("FAIL: Expected 'white', got '%s'\n", lamp.getColor().c_str());
        assert(false);
    }
    lamp.setColor("red");
    if (lamp.getColor() != "red") {
        printf("FAIL: Expected 'red', got '%s'\n", lamp.getColor().c_str());
        assert(false);
    }

    lamp.turnOn();
    if (lamp.isLampOn() != true) {
        printf("FAIL: Lamp should be on\n");
        assert(false);
    }

    lamp.setColor("green");
    if (lamp.getColor() != "green") {
        printf("FAIL: Expected 'green', got '%s'\n", lamp.getColor().c_str());
        assert(false);
    }

    lamp.turnOff();
    if (lamp.isLampOn() != false) {
        printf("FAIL: Lamp should be off\n");
        assert(false);
    }

    if (lamp.getColor() != "green") {
        printf("FAIL: Expected 'green', got '%s'\n", lamp.getColor().c_str());
        assert(false);
    }

    printf("PASS: HSM lamp works correctly\n");
    return 0;
}
