#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

// Moore Machine - output depends ONLY on state (output on entry)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

class MooreMachineFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    MooreMachineFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class MooreMachineFrameContext {
public:
    MooreMachineFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    MooreMachineFrameContext(MooreMachineFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class MooreMachineCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<MooreMachineFrameEvent> forward_event;
    std::unique_ptr<MooreMachineCompartment> parent_compartment;

    explicit MooreMachineCompartment(const std::string& state) : state(state) {}
};

class MooreMachine {
private:
    std::unique_ptr<MooreMachineCompartment> __compartment;
    std::unique_ptr<MooreMachineCompartment> __next_compartment;
    std::vector<std::unique_ptr<MooreMachineCompartment>> _state_stack;
    std::vector<MooreMachineFrameContext> _context_stack;

    int current_output = 0;;

    void __kernel(MooreMachineFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            MooreMachineFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                MooreMachineFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    MooreMachineFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(MooreMachineFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Q0") {
            _state_Q0(__e);
        } else if (state_name == "Q1") {
            _state_Q1(__e);
        } else if (state_name == "Q2") {
            _state_Q2(__e);
        } else if (state_name == "Q3") {
            _state_Q3(__e);
        } else if (state_name == "Q4") {
            _state_Q4(__e);
        }
    }

    void __transition(std::unique_ptr<MooreMachineCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Q0(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            set_output(0);
            }
            return;
        } else if (__e._message == "i_0") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q1");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q2");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Q1(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            set_output(0);
            }
            return;
        } else if (__e._message == "i_0") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q1");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q3");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Q2(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            set_output(0);
            }
            return;
        } else if (__e._message == "i_0") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q4");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q2");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Q3(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            set_output(1);
            }
            return;
        } else if (__e._message == "i_0") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q4");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q2");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Q4(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            {
            set_output(1);
            }
            return;
        } else if (__e._message == "i_0") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q1");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            auto __comp = std::make_unique<MooreMachineCompartment>("Q3");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

public:
    MooreMachine() {
        __compartment = std::make_unique<MooreMachineCompartment>("Q0");
        current_output = 0;;
        MooreMachineFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void i_0() {
        MooreMachineFrameEvent __e("i_0");
        MooreMachineFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void i_1() {
        MooreMachineFrameEvent __e("i_1");
        MooreMachineFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void set_output() {
        {
        current_output = value;
        }
    }

    int get_output() {
        {
        return current_output;
        }
    }

};

int main() {
    std::cout << "TAP version 14" << std::endl;
    std::cout << "1..5" << std::endl;

    MooreMachine m;

    // Initial state Q0 has output 0
    if (m.get_output() == 0) {
        std::cout << "ok 1 - moore initial state Q0 has output 0" << std::endl;
    } else {
        std::cout << "not ok 1 - moore initial state Q0 has output 0 # got " << m.get_output() << std::endl;
    }

    // i_0: Q0 -> Q1 (output 0)
    m.i_0();
    if (m.get_output() == 0) {
        std::cout << "ok 2 - moore Q1 has output 0" << std::endl;
    } else {
        std::cout << "not ok 2 - moore Q1 has output 0 # got " << m.get_output() << std::endl;
    }

    // i_1: Q1 -> Q3 (output 1)
    m.i_1();
    if (m.get_output() == 1) {
        std::cout << "ok 3 - moore Q3 has output 1" << std::endl;
    } else {
        std::cout << "not ok 3 - moore Q3 has output 1 # got " << m.get_output() << std::endl;
    }

    // i_0: Q3 -> Q4 (output 1)
    m.i_0();
    if (m.get_output() == 1) {
        std::cout << "ok 4 - moore Q4 has output 1" << std::endl;
    } else {
        std::cout << "not ok 4 - moore Q4 has output 1 # got " << m.get_output() << std::endl;
    }

    // i_0: Q4 -> Q1 (output 0)
    m.i_0();
    if (m.get_output() == 0) {
        std::cout << "ok 5 - moore Q1 has output 0 again" << std::endl;
    } else {
        std::cout << "not ok 5 - moore Q1 has output 0 again # got " << m.get_output() << std::endl;
    }

    std::cout << "# PASS - Moore machine outputs depend ONLY on state" << std::endl;

    return 0;
}
