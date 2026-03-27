#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>
#include <nlohmann/json.hpp>

class PersistTestFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    PersistTestFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class PersistTestFrameContext {
public:
    PersistTestFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    PersistTestFrameContext(PersistTestFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class PersistTestCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<PersistTestFrameEvent> forward_event;
    std::unique_ptr<PersistTestCompartment> parent_compartment;

    explicit PersistTestCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<PersistTestCompartment> clone() const {
        auto c = std::make_unique<PersistTestCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class PersistTest {
private:
    std::vector<std::unique_ptr<PersistTestCompartment>> _state_stack;
    std::unique_ptr<PersistTestCompartment> __compartment;
    std::unique_ptr<PersistTestCompartment> __next_compartment;
    std::vector<PersistTestFrameContext> _context_stack;

    void __kernel(PersistTestFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            PersistTestFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                PersistTestFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    PersistTestFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(PersistTestFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    void __transition(std::unique_ptr<PersistTestCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(PersistTestFrameEvent& __e) {
        if (__e._message == "get_value") {
            _context_stack.back()._return = std::any(value);
            return;;
        } else if (__e._message == "go_active") {
            auto __new_compartment = std::make_unique<PersistTestCompartment>("Active");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "go_idle") {
            // Already idle
        } else if (__e._message == "set_value") {
            auto v = std::any_cast<int>(__e._parameters.at("v"));
            value = v;
        }
    }

    void _state_Active(PersistTestFrameEvent& __e) {
        if (__e._message == "get_value") {
            _context_stack.back()._return = std::any(value);
            return;;
        } else if (__e._message == "go_active") {
            // Already active
        } else if (__e._message == "go_idle") {
            auto __new_compartment = std::make_unique<PersistTestCompartment>("Idle");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "set_value") {
            auto v = std::any_cast<int>(__e._parameters.at("v"));
            value = v * 2;
        }
    }

public:
    int value = 0;
    std::string name = "default";

    PersistTest() {
        __compartment = std::make_unique<PersistTestCompartment>("Idle");
        PersistTestFrameEvent __frame_event("$>");
        PersistTestFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void set_value(int v) {
        std::unordered_map<std::string, std::any> __params;
        __params["v"] = v;
        PersistTestFrameEvent __e("set_value", std::move(__params));
        PersistTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_value() {
        PersistTestFrameEvent __e("get_value");
        PersistTestFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void go_active() {
        PersistTestFrameEvent __e("go_active");
        PersistTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_idle() {
        PersistTestFrameEvent __e("go_idle");
        PersistTestFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string save_state() {
        std::function<nlohmann::json(const PersistTestCompartment*)> __ser = [&](const PersistTestCompartment* c) -> nlohmann::json {
            if (!c) return nullptr;
            nlohmann::json __cj;
            __cj["state"] = c->state;
            nlohmann::json __sv;
            for (auto& [k, v] : c->state_vars) {
            }
            __cj["state_vars"] = __sv;
            __cj["parent"] = __ser(c->parent_compartment.get());
            return __cj;
        };
        nlohmann::json __j;
        __j["_compartment"] = __ser(__compartment.get());
        nlohmann::json __stack = nlohmann::json::array();
        for (auto& c : _state_stack) { __stack.push_back(__ser(c.get())); }
        __j["_state_stack"] = __stack;
        __j["value"] = value;
        __j["name"] = name;
        return __j.dump();
    }

    static PersistTest restore_state(const std::string& json) {
        std::function<std::unique_ptr<PersistTestCompartment>(const nlohmann::json&)> __deser = [&](const nlohmann::json& d) -> std::unique_ptr<PersistTestCompartment> {
            if (d.is_null()) return nullptr;
            auto c = std::make_unique<PersistTestCompartment>(std::string(d["state"]));
            if (d.contains("state_vars")) {
                auto& sv = d["state_vars"];
            }
            if (d.contains("parent") && !d["parent"].is_null()) {
                c->parent_compartment = __deser(d["parent"]);
            }
            return c;
        };
        auto __j = nlohmann::json::parse(json);
        PersistTest __instance;
        __instance.__compartment = __deser(__j["_compartment"]);
        if (__j.contains("_state_stack")) {
            for (auto& __sc : __j["_state_stack"]) {
                __instance._state_stack.push_back(__deser(__sc));
            }
        }
        if (__j.contains("value")) { __j["value"].get_to(__instance.value); }
        if (__j.contains("name")) { __j["name"].get_to(__instance.name); }
        return __instance;
    }
};

int main() {
    printf("=== Test 23: Persist Basic (C++) ===\n");

    // Test 1: Create and modify system
    PersistTest s1;
    s1.set_value(10);
    s1.go_active();
    s1.set_value(5);  // Should be doubled to 10 in Active state

    // Test 2: Save state
    std::string json = s1.save_state();
    auto data = nlohmann::json::parse(json);
    if (data["_compartment"]["state"] != "Active") {
        printf("FAIL: Expected 'Active', got '%s'\n", std::string(data["_compartment"]["state"]).c_str());
        assert(false);
    }
    if (data["value"] != 10) {
        printf("FAIL: Expected 10, got %d\n", int(data["value"]));
        assert(false);
    }
    printf("1. Saved state: %s\n", json.c_str());

    // Test 3: Restore state
    PersistTest s2 = PersistTest::restore_state(json);
    if (s2.get_value() != 10) {
        printf("FAIL: Expected 10, got %d\n", s2.get_value());
        assert(false);
    }
    printf("2. Restored value: %d\n", s2.get_value());

    // Test 4: Verify state is preserved (Active state doubles)
    s2.set_value(3);  // Should be doubled to 6 in Active state
    if (s2.get_value() != 6) {
        printf("FAIL: Expected 6, got %d\n", s2.get_value());
        assert(false);
    }
    printf("3. After set_value(3) in Active: %d\n", s2.get_value());

    // Test 5: Verify transitions work after restore
    s2.go_idle();
    s2.set_value(4);  // Should NOT be doubled in Idle state
    if (s2.get_value() != 4) {
        printf("FAIL: Expected 4, got %d\n", s2.get_value());
        assert(false);
    }
    printf("4. After go_idle, set_value(4): %d\n", s2.get_value());

    printf("PASS: Persist basic works correctly\n");
    return 0;
}
