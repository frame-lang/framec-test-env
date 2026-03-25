#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>

// Mealy Machine - output depends on state AND input (output on transitions)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

class MealyMachineFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    MealyMachineFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class MealyMachineFrameContext {
public:
    MealyMachineFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    MealyMachineFrameContext(MealyMachineFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class MealyMachineCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<MealyMachineFrameEvent> forward_event;
    std::unique_ptr<MealyMachineCompartment> parent_compartment;

    explicit MealyMachineCompartment(const std::string& state) : state(state) {}
};

class MealyMachine {
private:
    std::unique_ptr<MealyMachineCompartment> __compartment;
    std::unique_ptr<MealyMachineCompartment> __next_compartment;
    std::vector<std::unique_ptr<MealyMachineCompartment>> _state_stack;
    std::vector<MealyMachineFrameContext> _context_stack;

    int last_output = 0;;

    void __kernel(MealyMachineFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            MealyMachineFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                MealyMachineFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    MealyMachineFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(MealyMachineFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Q0") {
            _state_Q0(__e);
        } else if (state_name == "Q1") {
            _state_Q1(__e);
        } else if (state_name == "Q2") {
            _state_Q2(__e);
        }
    }

    void __transition(std::unique_ptr<MealyMachineCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Q0(MealyMachineFrameEvent& __e) {
        if (__e._message == "i_0") {
            {
            emit_output(0);
            auto __comp = std::make_unique<MealyMachineCompartment>("Q1");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            emit_output(0);
            auto __comp = std::make_unique<MealyMachineCompartment>("Q2");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Q1(MealyMachineFrameEvent& __e) {
        if (__e._message == "i_0") {
            {
            emit_output(0);
            auto __comp = std::make_unique<MealyMachineCompartment>("Q1");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            emit_output(1);
            auto __comp = std::make_unique<MealyMachineCompartment>("Q2");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

    void _state_Q2(MealyMachineFrameEvent& __e) {
        if (__e._message == "i_0") {
            {
            emit_output(1);
            auto __comp = std::make_unique<MealyMachineCompartment>("Q1");
            __transition(std::move(__comp));
            return;
            }
            return;
        } else if (__e._message == "i_1") {
            {
            emit_output(0);
            auto __comp = std::make_unique<MealyMachineCompartment>("Q2");
            __transition(std::move(__comp));
            return;
            }
            return;
        }
    }

public:
    MealyMachine() {
        __compartment = std::make_unique<MealyMachineCompartment>("Q0");
        last_output = 0;;
        MealyMachineFrameEvent __frame_event("$>");
        __kernel(__frame_event);
    }

    void i_0() {
        MealyMachineFrameEvent __e("i_0");
        MealyMachineFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void i_1() {
        MealyMachineFrameEvent __e("i_1");
        MealyMachineFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void emit_output() {
        {
        last_output = value;
        }
    }

    int get_last_output() {
        {
        return last_output;
        }
    }

};

int main() {
    std::cout << "TAP version 14" << std::endl;
    std::cout << "1..4" << std::endl;

    MealyMachine m;

    // Test sequence: i_0, i_0, i_1, i_0
    m.i_0();  // Q0 -> Q1, output 0
    if (m.get_last_output() == 0) {
        std::cout << "ok 1 - mealy i_0 from Q0 outputs 0" << std::endl;
    } else {
        std::cout << "not ok 1 - mealy i_0 from Q0 outputs 0 # got " << m.get_last_output() << std::endl;
    }

    m.i_0();  // Q1 -> Q1, output 0
    if (m.get_last_output() == 0) {
        std::cout << "ok 2 - mealy i_0 from Q1 outputs 0" << std::endl;
    } else {
        std::cout << "not ok 2 - mealy i_0 from Q1 outputs 0 # got " << m.get_last_output() << std::endl;
    }

    m.i_1();  // Q1 -> Q2, output 1
    if (m.get_last_output() == 1) {
        std::cout << "ok 3 - mealy i_1 from Q1 outputs 1" << std::endl;
    } else {
        std::cout << "not ok 3 - mealy i_1 from Q1 outputs 1 # got " << m.get_last_output() << std::endl;
    }

    m.i_0();  // Q2 -> Q1, output 1
    if (m.get_last_output() == 1) {
        std::cout << "ok 4 - mealy i_0 from Q2 outputs 1" << std::endl;
    } else {
        std::cout << "not ok 4 - mealy i_0 from Q2 outputs 1 # got " << m.get_last_output() << std::endl;
    }

    std::cout << "# PASS - Mealy machine outputs depend on state AND input" << std::endl;

    return 0;
}
