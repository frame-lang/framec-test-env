#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


// Test 51: HSM Persistence (C++)
//
// Tests that HSM parent compartment chain is properly saved and restored:
// - Child state vars preserved
// - Parent state vars preserved
// - Parent compartment chain intact after restore
// - Forwarding to parent still works after restore

#include <iostream>
#include <string>
#include <cassert>
#include <nlohmann/json.hpp>

class HSMPersistFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    HSMPersistFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class HSMPersistFrameContext {
public:
    HSMPersistFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    HSMPersistFrameContext(HSMPersistFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class HSMPersistCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<HSMPersistFrameEvent> forward_event;
    std::unique_ptr<HSMPersistCompartment> parent_compartment;

    explicit HSMPersistCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<HSMPersistCompartment> clone() const {
        auto c = std::make_unique<HSMPersistCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class HSMPersist {
private:
    std::vector<std::unique_ptr<HSMPersistCompartment>> _state_stack;
    std::unique_ptr<HSMPersistCompartment> __compartment;
    std::unique_ptr<HSMPersistCompartment> __next_compartment;
    std::vector<HSMPersistFrameContext> _context_stack;

    void __kernel(HSMPersistFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            HSMPersistFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                HSMPersistFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    HSMPersistFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(HSMPersistFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Child") {
            _state_Child(__e);
        } else if (state_name == "Parent") {
            _state_Parent(__e);
        }
    }

    void __transition(std::unique_ptr<HSMPersistCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Parent(HSMPersistFrameEvent& __e) {
        auto* __sv_comp = __compartment.get();
        while (__sv_comp && __sv_comp->state != "Parent") { __sv_comp = __sv_comp->parent_compartment.get(); }
        if (__e._message == "$>") {
            if (__compartment->state_vars.count("parent_count") == 0) { __compartment->state_vars["parent_count"] = std::any(100); }
        } else if (__e._message == "get_parent_count") {
            _context_stack.back()._return = std::any(std::any_cast<int>(__sv_comp->state_vars["parent_count"]));
            return;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Parent"));
            return;
        } else if (__e._message == "increment_parent") {
            __sv_comp->state_vars["parent_count"] = std::any(std::any_cast<int>(__sv_comp->state_vars["parent_count"]) + 1);
        }
    }

    void _state_Child(HSMPersistFrameEvent& __e) {
        auto* __sv_comp = __compartment.get();
        while (__sv_comp && __sv_comp->state != "Child") { __sv_comp = __sv_comp->parent_compartment.get(); }
        if (__e._message == "$>") {
            if (__compartment->state_vars.count("child_count") == 0) { __compartment->state_vars["child_count"] = std::any(0); }
        } else if (__e._message == "get_child_count") {
            _context_stack.back()._return = std::any(std::any_cast<int>(__sv_comp->state_vars["child_count"]));
            return;
        } else if (__e._message == "get_parent_count") {
            // Forward to parent
            _state_Parent(__e);
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Child"));
            return;
        } else if (__e._message == "increment_child") {
            __sv_comp->state_vars["child_count"] = std::any(std::any_cast<int>(__sv_comp->state_vars["child_count"]) + 1);
        } else if (__e._message == "increment_parent") {
            // Forward to parent
            _state_Parent(__e);
        }
    }

public:
    HSMPersist() {
        // HSM: Create parent compartment chain
        auto __parent_comp_0 = std::make_unique<HSMPersistCompartment>("Parent");
        __parent_comp_0->state_vars["parent_count"] = std::any(100);
        __compartment = std::make_unique<HSMPersistCompartment>("Child");
        __compartment->parent_compartment = std::move(__parent_comp_0);
        HSMPersistFrameEvent __frame_event("$>");
        HSMPersistFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void increment_child() {
        HSMPersistFrameEvent __e("increment_child");
        HSMPersistFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void increment_parent() {
        HSMPersistFrameEvent __e("increment_parent");
        HSMPersistFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_child_count() {
        HSMPersistFrameEvent __e("get_child_count");
        HSMPersistFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_parent_count() {
        HSMPersistFrameEvent __e("get_parent_count");
        HSMPersistFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_state() {
        HSMPersistFrameEvent __e("get_state");
        HSMPersistFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string save_state() {
        std::function<nlohmann::json(const HSMPersistCompartment*)> __ser = [&](const HSMPersistCompartment* c) -> nlohmann::json {
            if (!c) return nullptr;
            nlohmann::json __cj;
            __cj["state"] = c->state;
            nlohmann::json __sv;
            for (auto& [k, v] : c->state_vars) {
                if (k == "child_count") { try { __sv[k] = std::any_cast<int>(v); } catch(...) {} }
                if (k == "parent_count") { try { __sv[k] = std::any_cast<int>(v); } catch(...) {} }
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
        return __j.dump();
    }

    static HSMPersist restore_state(const std::string& json) {
        std::function<std::unique_ptr<HSMPersistCompartment>(const nlohmann::json&)> __deser = [&](const nlohmann::json& d) -> std::unique_ptr<HSMPersistCompartment> {
            if (d.is_null()) return nullptr;
            auto c = std::make_unique<HSMPersistCompartment>(std::string(d["state"]));
            if (d.contains("state_vars")) {
                auto& sv = d["state_vars"];
                if (sv.contains("child_count")) { c->state_vars["child_count"] = std::any(sv["child_count"].get<int>()); }
                if (sv.contains("parent_count")) { c->state_vars["parent_count"] = std::any(sv["parent_count"].get<int>()); }
            }
            if (d.contains("parent") && !d["parent"].is_null()) {
                c->parent_compartment = __deser(d["parent"]);
            }
            return c;
        };
        auto __j = nlohmann::json::parse(json);
        HSMPersist __instance;
        __instance.__compartment = __deser(__j["_compartment"]);
        if (__j.contains("_state_stack")) {
            for (auto& __sc : __j["_state_stack"]) {
                __instance._state_stack.push_back(__deser(__sc));
            }
        }
        return __instance;
    }
};

int main() {
    printf("=== Test 51: HSM Persistence (C++) ===\n");

    // Create system and modify state vars at both levels
    HSMPersist s1;

    // Verify initial state
    if (s1.get_state() != "Child") {
        printf("FAIL: Expected Child, got %s\n", s1.get_state().c_str());
        assert(false);
    }
    if (s1.get_child_count() != 0) {
        printf("FAIL: Expected 0, got %d\n", s1.get_child_count());
        assert(false);
    }
    if (s1.get_parent_count() != 100) {
        printf("FAIL: Expected 100, got %d\n", s1.get_parent_count());
        assert(false);
    }
    printf("1. Initial state verified: Child with child_count=0, parent_count=100\n");

    // Modify state vars at both levels
    s1.increment_child();
    s1.increment_child();
    s1.increment_child();  // child_count = 3
    s1.increment_parent();
    s1.increment_parent();  // parent_count = 102

    if (s1.get_child_count() != 3) {
        printf("FAIL: Expected 3, got %d\n", s1.get_child_count());
        assert(false);
    }
    if (s1.get_parent_count() != 102) {
        printf("FAIL: Expected 102, got %d\n", s1.get_parent_count());
        assert(false);
    }
    printf("2. After increments: child_count=%d, parent_count=%d\n", s1.get_child_count(), s1.get_parent_count());

    // Save state
    std::string json = s1.save_state();
    printf("3. Saved state: %zu chars\n", json.length());

    // Restore to new instance
    HSMPersist s2 = HSMPersist::restore_state(json);

    // Verify restored state
    if (s2.get_state() != "Child") {
        printf("FAIL: Expected Child after restore, got %s\n", s2.get_state().c_str());
        assert(false);
    }
    printf("4. Restored state: %s\n", s2.get_state().c_str());

    // Verify child state var preserved
    if (s2.get_child_count() != 3) {
        printf("FAIL: Expected child_count=3, got %d\n", s2.get_child_count());
        assert(false);
    }
    printf("5. Child state var preserved: child_count=%d\n", s2.get_child_count());

    // Verify parent state var preserved (requires parent compartment chain)
    if (s2.get_parent_count() != 102) {
        printf("FAIL: Expected parent_count=102, got %d\n", s2.get_parent_count());
        assert(false);
    }
    printf("6. Parent state var preserved: parent_count=%d\n", s2.get_parent_count());

    // Verify state machine still works after restore
    s2.increment_child();
    s2.increment_parent();
    if (s2.get_child_count() != 4) {
        printf("FAIL: Expected 4, got %d\n", s2.get_child_count());
        assert(false);
    }
    if (s2.get_parent_count() != 103) {
        printf("FAIL: Expected 103, got %d\n", s2.get_parent_count());
        assert(false);
    }
    printf("7. After post-restore increments: child_count=%d, parent_count=%d\n", s2.get_child_count(), s2.get_parent_count());

    printf("PASS: HSM persistence works correctly\n");
    return 0;
}
