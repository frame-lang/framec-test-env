#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

class EnterExitFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    EnterExitFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class EnterExitFrameContext {
public:
    EnterExitFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    EnterExitFrameContext(EnterExitFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class EnterExitCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<EnterExitFrameEvent> forward_event;
    std::unique_ptr<EnterExitCompartment> parent_compartment;

    explicit EnterExitCompartment(const std::string& state) : state(state) {}
};

class EnterExit {
private:
    std::unique_ptr<EnterExitCompartment> __compartment;
    std::unique_ptr<EnterExitCompartment> __next_compartment;
    std::vector<std::unique_ptr<EnterExitCompartment>> _state_stack;
    std::vector<EnterExitFrameContext> _context_stack;

    int enter_off_count = 0;;
    int exit_off_count = 0;;
    int enter_on_count = 0;;
    int exit_on_count = 0;;

    void __kernel(EnterExitFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            EnterExitFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                EnterExitFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    EnterExitFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(EnterExitFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Off") {
            _state_Off(__e);
        } else if (state_name == "On") {
            _state_On(__e);
        }
    }

    void __transition(std::unique_ptr<EnterExitCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Off(EnterExitFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            enter_off_count += 1;
            std::cout << "Entered Off state" << std::endl;
            }
            return;
        } else if (__e._message == "<$") {
            {
            exit_off_count += 1;
            std::cout << "Exiting Off state" << std::endl;
            }
            return;
        } else if (__e._message == "toggle") {
            {
            auto __comp = std::make_unique<EnterExitCompartment>("On");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "get_log_count") {
            {
            // Return encoded counts: enter_off * 1000 + exit_off * 100 + enter_on * 10 + exit_on
            int result = enter_off_count * 1000 + exit_off_count * 100 + enter_on_count * 10 + exit_on_count;
            _context_stack.back()._return = result;
            return;
            }
            return;
        }
    }

    void _state_On(EnterExitFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            enter_on_count += 1;
            std::cout << "Entered On state" << std::endl;
            }
            return;
        } else if (__e._message == "<$") {
            {
            exit_on_count += 1;
            std::cout << "Exiting On state" << std::endl;
            }
            return;
        } else if (__e._message == "toggle") {
            {
            auto __comp = std::make_unique<EnterExitCompartment>("Off");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "get_log_count") {
            {
            int result = enter_off_count * 1000 + exit_off_count * 100 + enter_on_count * 10 + exit_on_count;
            _context_stack.back()._return = result;
            return;
            }
            return;
        }
    }

public:
    EnterExit() {
        __compartment = std::make_unique<EnterExitCompartment>("Off");
        enter_off_count = 0;;
        exit_off_count = 0;;
        enter_on_count = 0;;
        exit_on_count = 0;;
        EnterExitFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void toggle() {
        EnterExitFrameEvent __e("toggle");
        EnterExitFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_log_count() {
        EnterExitFrameEvent __e("get_log_count");
        EnterExitFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

};

int main() {
    std::cout << "=== Test 05: Enter/Exit Handlers ===" << std::endl;
    EnterExit s;

    // Initial enter should have been called (enter_off_count = 1)
    int log = s.get_log_count();
    // Expected: 1*1000 + 0*100 + 0*10 + 0 = 1000
    assert(log == 1000);
    std::cout << "After construction: log_count = " << log << " (enter_off=1)" << std::endl;

    // Toggle to On - should exit Off, enter On
    s.toggle();
    log = s.get_log_count();
    // Expected: 1*1000 + 1*100 + 1*10 + 0 = 1110
    assert(log == 1110);
    std::cout << "After toggle to On: log_count = " << log << " (enter_off=1, exit_off=1, enter_on=1)" << std::endl;

    // Toggle back to Off - should exit On, enter Off
    s.toggle();
    log = s.get_log_count();
    // Expected: 2*1000 + 1*100 + 1*10 + 1 = 2111
    assert(log == 2111);
    std::cout << "After toggle to Off: log_count = " << log << " (enter_off=2, exit_off=1, enter_on=1, exit_on=1)" << std::endl;

    std::cout << "PASS: 05 enter exit" << std::endl;
    return 0;
}
