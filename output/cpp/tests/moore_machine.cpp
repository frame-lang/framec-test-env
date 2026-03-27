#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


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

    std::unique_ptr<MooreMachineCompartment> clone() const {
        auto c = std::make_unique<MooreMachineCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class MooreMachine {
private:
    std::vector<std::unique_ptr<MooreMachineCompartment>> _state_stack;
    std::unique_ptr<MooreMachineCompartment> __compartment;
    std::unique_ptr<MooreMachineCompartment> __next_compartment;
    std::vector<MooreMachineFrameContext> _context_stack;

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

    void _state_Q4(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            this->set_output(1);
        } else if (__e._message == "i_0") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q1");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "i_1") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q3");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Q1(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            this->set_output(0);
        } else if (__e._message == "i_0") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q1");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "i_1") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q3");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Q2(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            this->set_output(0);
        } else if (__e._message == "i_0") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q4");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "i_1") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q2");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Q0(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            this->set_output(0);
        } else if (__e._message == "i_0") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q1");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "i_1") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q2");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Q3(MooreMachineFrameEvent& __e) {
        if (__e._message == "$>") {
            this->set_output(1);
        } else if (__e._message == "i_0") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q4");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "i_1") {
            auto __new_compartment = std::make_unique<MooreMachineCompartment>("Q2");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void set_output(int value) {
                    current_output = value;
    }

public:
    int current_output = 0;

    MooreMachine() {
        __compartment = std::make_unique<MooreMachineCompartment>("Q0");
        MooreMachineFrameEvent __frame_event("$>");
        MooreMachineFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
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

    int get_output() {
                    return current_output;
    }
};

int main() {
    printf("TAP version 14\n");
    printf("1..5\n");

    MooreMachine m;

    // Initial state Q0 has output 0
    if (m.get_output() == 0) {
        printf("ok 1 - moore initial state Q0 has output 0\n");
    } else {
        printf("not ok 1 - moore initial state Q0 has output 0 # got %d\n", m.get_output());
    }

    // i_0: Q0 -> Q1 (output 0)
    m.i_0();
    if (m.get_output() == 0) {
        printf("ok 2 - moore Q1 has output 0\n");
    } else {
        printf("not ok 2 - moore Q1 has output 0 # got %d\n", m.get_output());
    }

    // i_1: Q1 -> Q3 (output 1)
    m.i_1();
    if (m.get_output() == 1) {
        printf("ok 3 - moore Q3 has output 1\n");
    } else {
        printf("not ok 3 - moore Q3 has output 1 # got %d\n", m.get_output());
    }

    // i_0: Q3 -> Q4 (output 1)
    m.i_0();
    if (m.get_output() == 1) {
        printf("ok 4 - moore Q4 has output 1\n");
    } else {
        printf("not ok 4 - moore Q4 has output 1 # got %d\n", m.get_output());
    }

    // i_0: Q4 -> Q1 (output 0)
    m.i_0();
    if (m.get_output() == 0) {
        printf("ok 5 - moore Q1 has output 0 again\n");
    } else {
        printf("not ok 5 - moore Q1 has output 0 again # got %d\n", m.get_output());
    }

    printf("# PASS - Moore machine outputs depend ONLY on state\n");
    return 0;
}
