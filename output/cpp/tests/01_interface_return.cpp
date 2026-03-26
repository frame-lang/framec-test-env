#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>


#include <iostream>
#include <string>
#include <cassert>
#include <vector>

class InterfaceReturnFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    InterfaceReturnFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class InterfaceReturnFrameContext {
public:
    InterfaceReturnFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    InterfaceReturnFrameContext(InterfaceReturnFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class InterfaceReturnCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<InterfaceReturnFrameEvent> forward_event;
    std::unique_ptr<InterfaceReturnCompartment> parent_compartment;

    explicit InterfaceReturnCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<InterfaceReturnCompartment> clone() const {
        auto c = std::make_unique<InterfaceReturnCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class InterfaceReturn {
private:
    std::vector<std::unique_ptr<InterfaceReturnCompartment>> _state_stack;
    std::unique_ptr<InterfaceReturnCompartment> __compartment;
    std::unique_ptr<InterfaceReturnCompartment> __next_compartment;
    std::vector<InterfaceReturnFrameContext> _context_stack;

    void __kernel(InterfaceReturnFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            InterfaceReturnFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                InterfaceReturnFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    InterfaceReturnFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(InterfaceReturnFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    void __transition(std::unique_ptr<InterfaceReturnCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Active(InterfaceReturnFrameEvent& __e) {
        if (__e._message == "bool_return") {
            _context_stack.back()._return = std::any(true);
            return;;
        } else if (__e._message == "computed_return") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            int result = a * b + 10;
            _context_stack.back()._return = std::any(result);
            return;;
        } else if (__e._message == "conditional_return") {
            auto x = std::any_cast<int>(__e._parameters.at("x"));
            if (x < 0) {
                _context_stack.back()._return = std::any(std::string("negative"));
                return;;
            } else if (x == 0) {
                _context_stack.back()._return = std::any(std::string("zero"));
                return;;
            } else {
                _context_stack.back()._return = std::any(std::string("positive"));
                return;;
            }
        } else if (__e._message == "explicit_bool") {
            _context_stack.back()._return = std::any(true);
        } else if (__e._message == "explicit_computed") {
            auto a = std::any_cast<int>(__e._parameters.at("a"));
            auto b = std::any_cast<int>(__e._parameters.at("b"));
            int result = a * b + 10;
            _context_stack.back()._return = std::any(result);
        } else if (__e._message == "explicit_conditional") {
            auto x = std::any_cast<int>(__e._parameters.at("x"));
            if (x < 0) {
                _context_stack.back()._return = std::any(std::string("negative"));
                return;
            } else if (x == 0) {
                _context_stack.back()._return = std::any(std::string("zero"));
                return;
            } else {
                _context_stack.back()._return = std::any(std::string("positive"));
            }
        } else if (__e._message == "explicit_int") {
            _context_stack.back()._return = std::any(42);
        } else if (__e._message == "explicit_string") {
            _context_stack.back()._return = std::any(std::string("Frame"));
        } else if (__e._message == "int_return") {
            _context_stack.back()._return = std::any(42);
            return;;
        } else if (__e._message == "string_return") {
            _context_stack.back()._return = std::any(std::string("Frame"));
            return;;
        }
    }

public:
    InterfaceReturn() {
        __compartment = std::make_unique<InterfaceReturnCompartment>("Active");
        InterfaceReturnFrameEvent __frame_event("$>");
        InterfaceReturnFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    bool bool_return() {
        InterfaceReturnFrameEvent __e("bool_return");
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int int_return() {
        InterfaceReturnFrameEvent __e("int_return");
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string string_return() {
        InterfaceReturnFrameEvent __e("string_return");
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string conditional_return(int x) {
        std::unordered_map<std::string, std::any> __params;
        __params["x"] = x;
        InterfaceReturnFrameEvent __e("conditional_return", std::move(__params));
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int computed_return(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        InterfaceReturnFrameEvent __e("computed_return", std::move(__params));
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    bool explicit_bool() {
        InterfaceReturnFrameEvent __e("explicit_bool");
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(bool()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<bool>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int explicit_int() {
        InterfaceReturnFrameEvent __e("explicit_int");
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string explicit_string() {
        InterfaceReturnFrameEvent __e("explicit_string");
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string explicit_conditional(int x) {
        std::unordered_map<std::string, std::any> __params;
        __params["x"] = x;
        InterfaceReturnFrameEvent __e("explicit_conditional", std::move(__params));
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int explicit_computed(int a, int b) {
        std::unordered_map<std::string, std::any> __params;
        __params["a"] = a;
        __params["b"] = b;
        InterfaceReturnFrameEvent __e("explicit_computed", std::move(__params));
        InterfaceReturnFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }
};

int main() {
    printf("=== Test 01: Interface Return (C++) ===\n");
    InterfaceReturn s;
    std::vector<std::string> errors;

    printf("-- Testing 'return value' sugar --\n");

    bool rb = s.bool_return();
    if (rb != true) {
        errors.push_back("bool_return: expected true");
    } else {
        printf("1. bool_return() = true\n");
    }

    int ri = s.int_return();
    if (ri != 42) {
        errors.push_back("int_return: expected 42");
    } else {
        printf("2. int_return() = 42\n");
    }

    std::string rs = s.string_return();
    if (rs != "Frame") {
        errors.push_back("string_return: expected 'Frame'");
    } else {
        printf("3. string_return() = 'Frame'\n");
    }

    std::string rc = s.conditional_return(-5);
    if (rc != "negative") {
        errors.push_back("conditional_return(-5): expected 'negative'");
    }
    rc = s.conditional_return(0);
    if (rc != "zero") {
        errors.push_back("conditional_return(0): expected 'zero'");
    }
    rc = s.conditional_return(10);
    if (rc != "positive") {
        errors.push_back("conditional_return(10): expected 'positive'");
    } else {
        printf("4. conditional_return(-5,0,10) = 'negative','zero','positive'\n");
    }

    int rcomp = s.computed_return(3, 4);
    if (rcomp != 22) {
        errors.push_back("computed_return(3,4): expected 22");
    } else {
        printf("5. computed_return(3,4) = 22\n");
    }

    printf("-- Testing '@@:return = value' explicit --\n");

    rb = s.explicit_bool();
    if (rb != true) {
        errors.push_back("explicit_bool: expected true");
    } else {
        printf("6. explicit_bool() = true\n");
    }

    ri = s.explicit_int();
    if (ri != 42) {
        errors.push_back("explicit_int: expected 42");
    } else {
        printf("7. explicit_int() = 42\n");
    }

    rs = s.explicit_string();
    if (rs != "Frame") {
        errors.push_back("explicit_string: expected 'Frame'");
    } else {
        printf("8. explicit_string() = 'Frame'\n");
    }

    rc = s.explicit_conditional(-5);
    if (rc != "negative") {
        errors.push_back("explicit_conditional(-5): expected 'negative'");
    }
    rc = s.explicit_conditional(0);
    if (rc != "zero") {
        errors.push_back("explicit_conditional(0): expected 'zero'");
    }
    rc = s.explicit_conditional(10);
    if (rc != "positive") {
        errors.push_back("explicit_conditional(10): expected 'positive'");
    } else {
        printf("9. explicit_conditional(-5,0,10) = 'negative','zero','positive'\n");
    }

    rcomp = s.explicit_computed(3, 4);
    if (rcomp != 22) {
        errors.push_back("explicit_computed(3,4): expected 22");
    } else {
        printf("10. explicit_computed(3,4) = 22\n");
    }

    if (errors.size() > 0) {
        for (const auto& e : errors) {
            printf("FAIL: %s\n", e.c_str());
        }
        assert(false);
    } else {
        printf("PASS: All interface return tests passed\n");
    }
    return 0;
}
